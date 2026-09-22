import json

from app.nemotron import client, MODEL
from app.tools.registry import get_tool_definitions
from app.tools.executor import execute_tool


MAX_TOOL_CALLS = 5


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
2. Never claim that a tool was executed unless a
   tool result was actually provided.
3. Never request tools that are not listed above.
4. Never execute Python, PowerShell, shell commands,
   SQL, or arbitrary code through a tool.
5. Use calculator for arithmetic when precision matters.
6. Use private document tools when the user asks
   about uploaded documents.
7. Use GitHub tools when the user asks about a
   GitHub repository.
8. If a tool fails, explain the failure honestly.
9. Keep the final answer concise and useful.
10. Do not expose internal tool protocol details
    to the user.
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


def run_agent(messages: list[dict]) -> str:
    agent_messages = [
        {
            "role": "system",
            "content": _build_tool_instructions(),
        }
    ]

    agent_messages.extend(messages)

    tool_calls = 0

    while tool_calls < MAX_TOOL_CALLS:
        response = client.chat.completions.create(
            model=MODEL,
            messages=agent_messages,
            max_tokens=700,
        )

        content = response.choices[0].message.content

        if not content:
            return (
                "I wasn't able to generate a response. "
                "Please try again."
            )

        tool_request = _extract_tool_request(content)

        if tool_request is None:
            return content.strip()

        tool_calls += 1

        tool_name = tool_request["tool"]
        arguments = tool_request["arguments"]

        tool_result = execute_tool(
            tool_name=tool_name,
            arguments=arguments,
        )

        agent_messages.append(
            {
                "role": "assistant",
                "content": content,
            }
        )

        agent_messages.append(
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
                    "Continue answering the user's request "
                    "using this result."
                ),
            }
        )

    return (
        "I reached the maximum number of tool operations "
        "allowed for this request. Please try a more "
        "specific request."
    )