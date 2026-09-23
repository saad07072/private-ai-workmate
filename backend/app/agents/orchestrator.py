import json

from app.nemotron import client
from app.tools.registry import get_tool_definitions
from app.tools.executor import execute_tool
from app.agents.model_router import (
    select_model,
    get_route_name,
    FAST_MODEL,
    REASONING_MODEL,
)


MAX_TOOL_CALLS = 8


def _build_tool_instructions():
    tools = get_tool_definitions()
    tool_text = json.dumps(
        tools,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are Private AI Workmate, a personal AI agent
with controlled tools.

AVAILABLE TOOLS:

{tool_text}


TOOL USAGE PROTOCOL:

When you need a tool, respond with ONLY valid JSON
using exactly this format:

{{
  "action": "tool",
  "tool": "tool_name",
  "arguments": {{}}
}}

Example:

{{
  "action": "tool",
  "tool": "calculator",
  "arguments": {{
    "expression": "25 * 4"
  }}
}}


IMPORTANT TOOL RULES:

- Do not explain that you are going to use a tool.
- Do not say "Let me check".
- Do not say "Let me examine".
- Do not describe your planned tool usage.
- If a tool is required, output ONLY the JSON tool request.
- If no tool is required, answer the user normally.
- Never invent tool results.


GITHUB DEVELOPER MODE:

You have read-only access to GitHub through the
GitHub tools listed above.

Use GitHub tools when the user asks you to:

- inspect a repository
- understand project structure
- read source code
- locate code
- search for functions or classes
- inspect issues
- inspect pull requests
- analyze implementation details

GitHub repository names must use:

owner/name

Before analyzing source code, use the appropriate
GitHub tool to obtain the actual repository data.

Never invent GitHub repository contents.

Never claim that you inspected a file unless the
GitHub tool actually returned that file.

Never claim that a GitHub issue or pull request exists
unless a GitHub tool returned it.


GITHUB SECURITY BOUNDARY:

GitHub tools are read-only.

Never attempt to:

- create commits
- push code
- delete files
- create issues
- close issues
- merge pull requests
- approve pull requests
- modify repositories
- execute GitHub Actions

If the user requests one of these actions, explain
that the current developer mode only supports
read-only GitHub analysis.


GENERAL RULES:

1. Never invent tool results.
2. Never claim a tool was executed unless a tool
   result was actually provided.
3. Never request tools that are not listed above.
4. Never execute Python, PowerShell, shell commands,
   SQL, or arbitrary code through a tool.
5. Use calculator for arithmetic when precision matters.
6. Use private document tools when the user asks
   about uploaded documents.
7. Use GitHub tools when the user asks about a
   GitHub repository.
8. If a tool fails, explain the failure honestly.
9. Keep final answers concise and useful.
10. Do not expose internal tool protocol details.
"""


def _build_final_instructions(
    tool_results: list[dict],
    reasoning: bool,
):
    results_text = json.dumps(
        tool_results,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    model_description = (
        "You are the reasoning stage of Private AI Workmate."
        if reasoning
        else "You are the final response stage of Private AI Workmate."
    )

    return f"""
{model_description}

The user's request has already been processed through
the application's controlled tool layer.

You are now responsible for producing the final answer.

IMPORTANT:

- Do NOT request any tools.
- Do NOT output tool JSON.
- Do NOT say "Let me check".
- Do NOT say "Let me examine".
- Do NOT describe future tool calls.
- Use only the evidence contained in the conversation
  and the tool results below.
- Never invent information that is not supported by
  the provided evidence.
- If the evidence is incomplete, clearly state what
  could not be verified.
- Give the user a direct, useful answer.

TOOL RESULTS:

{results_text}
"""


def _extract_tool_request(response_text: str):
    text = response_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if data.get("action") != "tool":
        return None

    tool_name = data.get("tool")
    arguments = data.get("arguments", {})

    if not isinstance(tool_name, str):
        return None

    if not isinstance(arguments, dict):
        return None

    return {
        "tool": tool_name,
        "arguments": arguments,
    }


def _get_max_tokens(model: str) -> int:
    if model == REASONING_MODEL:
        return 2400

    return 700


def _request_model(
    messages: list[dict],
    model: str,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=_get_max_tokens(model),
    )

    content = response.choices[0].message.content

    if content:
        return content.strip()

    return ""


def _collect_tools(
    messages: list[dict],
) -> tuple[list[dict], str | None]:
    """
    Run the controlled tool-selection stage.

    Tool selection always uses the fast model so that
    the reasoning model is reserved for complex analysis
    and final synthesis.
    """

    tool_messages = [
        {
            "role": "system",
            "content": _build_tool_instructions(),
        }
    ]

    tool_messages.extend(messages)

    tool_results = []

    for _ in range(MAX_TOOL_CALLS):
        response_text = _request_model(
            tool_messages,
            FAST_MODEL,
        )

        if not response_text:
            return tool_results, None

        tool_request = _extract_tool_request(
            response_text
        )

        if tool_request is None:
            return tool_results, response_text

        tool_name = tool_request["tool"]
        arguments = tool_request["arguments"]

        tool_result = execute_tool(
            tool_name=tool_name,
            arguments=arguments,
        )

        tool_results.append(
            {
                "tool": tool_name,
                "arguments": arguments,
                "result": tool_result,
            }
        )

        tool_messages.append(
            {
                "role": "assistant",
                "content": response_text,
            }
        )

        tool_messages.append(
            {
                "role": "system",
                "content": (
                    "TOOL RESULT\n"
                    "============\n"
                    + json.dumps(
                        tool_result,
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n\n"
                    "If another tool is required, output ONLY "
                    "the JSON tool request. Otherwise answer "
                    "the user's request."
                ),
            }
        )

    return tool_results, None


def _final_answer(
    messages: list[dict],
    tool_results: list[dict],
    route: str,
    fallback_response: str | None,
) -> str:
    """
    Produce the final user-facing answer.

    Complex requests are synthesized by the reasoning model.
    Normal requests use the fast model.
    """

    if not tool_results and fallback_response:
        return fallback_response.strip()

    final_model = (
        REASONING_MODEL
        if route == "reasoning"
        else FAST_MODEL
    )

    final_messages = [
        {
            "role": "system",
            "content": _build_final_instructions(
                tool_results=tool_results,
                reasoning=(route == "reasoning"),
            ),
        }
    ]

    final_messages.extend(messages)

    response = _request_model(
        final_messages,
        final_model,
    )

    if response:
        return response.strip()

    if fallback_response:
        return fallback_response.strip()

    return (
        "I wasn't able to generate a final response. "
        "Please try again."
    )


def run_agent(messages: list[dict]) -> str:
    """
    Main Private AI Workmate agent.

    Architecture:

        User request
             |
             v
       Model Router
             |
             v
       Fast Tool Stage
             |
             v
       Controlled Tools
             |
             v
       Tool Results
             |
             v
    Final Model Synthesis
             |
             v
       User Response
    """

    route_model = select_model(messages)
    route = get_route_name(route_model)

    tool_results, fallback_response = _collect_tools(
        messages
    )

    return _final_answer(
        messages=messages,
        tool_results=tool_results,
        route=route,
        fallback_response=fallback_response,
    )