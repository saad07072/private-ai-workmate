import json

from app.tools.registry import TOOLS
from app.tools.permissions import (
    is_tool_allowed,
)
from app.tools.audit import (
    record_tool_call,
)


def execute_tool(
    tool_name: str,
    arguments: dict,
):
    if not is_tool_allowed(
        tool_name
    ):
        raise PermissionError(
            f"Tool '{tool_name}' is not allowed."
        )

    if tool_name not in TOOLS:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    if not isinstance(
        arguments,
        dict,
    ):
        raise ValueError(
            "Tool arguments must be a JSON object."
        )

    tool = TOOLS[tool_name]

    try:
        result = tool["function"](
            **arguments
        )

        result_text = json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

        record_tool_call(
            tool_name=tool_name,
            arguments=arguments,
            success=True,
            result_preview=result_text,
        )

        return {
            "success": True,
            "tool": tool_name,
            "result": result,
        }

    except Exception as exc:

        error = str(exc)

        record_tool_call(
            tool_name=tool_name,
            arguments=arguments,
            success=False,
            result_preview=error,
        )

        return {
            "success": False,
            "tool": tool_name,
            "error": error,
        }