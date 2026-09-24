import json

from app.tools.registry import TOOLS

from app.tools.permissions import (
    is_tool_allowed,
    get_tool_policy,
    validate_tool_arguments,
)

from app.tools.audit import (
    record_tool_call,
    record_security_event,
)

from app.tools.security import (
    scan_for_prompt_injection,
)


def _validate_schema(
    tool_name: str,
    arguments: dict,
):
    tool = TOOLS[tool_name]

    schema = tool.get(
        "parameters",
        {},
    )

    properties = schema.get(
        "properties",
        {},
    )

    required = schema.get(
        "required",
        [],
    )

    for required_name in required:
        if required_name not in arguments:
            raise ValueError(
                f"Missing required argument: "
                f"{required_name}"
            )

    unknown_arguments = (
        set(arguments)
        - set(properties)
    )

    if unknown_arguments:
        raise ValueError(
            "Unknown tool arguments: "
            + ", ".join(
                sorted(unknown_arguments)
            )
        )

    for name, value in arguments.items():
        definition = properties.get(
            name,
            {},
        )

        expected_type = definition.get(
            "type"
        )

        if expected_type == "string":
            if not isinstance(
                value,
                str,
            ):
                raise ValueError(
                    f"Argument '{name}' must be a string."
                )

        elif expected_type == "integer":
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise ValueError(
                    f"Argument '{name}' must be an integer."
                )

        elif expected_type == "object":
            if not isinstance(
                value,
                dict,
            ):
                raise ValueError(
                    f"Argument '{name}' must be an object."
                )

        allowed_values = definition.get(
            "enum"
        )

        if (
            allowed_values
            and value not in allowed_values
        ):
            raise ValueError(
                f"Invalid value for argument "
                f"'{name}'."
            )


def execute_tool(
    tool_name: str,
    arguments: dict,
):
    policy = get_tool_policy(
        tool_name
    )

    if policy is None:
        record_security_event(
            "unknown_tool",
            {
                "tool": tool_name,
            },
        )

        raise PermissionError(
            f"Tool '{tool_name}' is not registered."
        )

    if not is_tool_allowed(
        tool_name
    ):
        record_security_event(
            "tool_denied",
            {
                "tool": tool_name,
                "capability": policy.get(
                    "capability"
                ),
            },
        )

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

    # Schema validation
    _validate_schema(
        tool_name,
        arguments,
    )

    # Security-specific validation
    validate_tool_arguments(
        tool_name,
        arguments,
    )

    # Detect suspicious instruction-like content
    # without allowing it to bypass deterministic
    # permission checks.
    argument_text = json.dumps(
        arguments,
        ensure_ascii=False,
        default=str,
    )

    scan = scan_for_prompt_injection(
        argument_text
    )

    if scan["suspicious"]:
        record_security_event(
            "prompt_injection_signal",
            {
                "tool": tool_name,
                "categories": scan[
                    "categories"
                ],
            },
        )

    tool = TOOLS[
        tool_name
    ]

    try:
        result = tool["function"](
            **arguments
        )

        result_text = json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

        result_scan = scan_for_prompt_injection(
            result_text
        )

        if result_scan["suspicious"]:
            record_security_event(
                "untrusted_tool_output_signal",
                {
                    "tool": tool_name,
                    "categories": result_scan[
                        "categories"
                    ],
                },
            )

        record_tool_call(
            tool_name=tool_name,
            arguments=arguments,
            success=True,
            result_preview=result,
        )

        return {
            "success": True,
            "tool": tool_name,
            "result": result,
            "security": {
                "untrusted_data": True,
                "instruction_like_content_detected": (
                    result_scan["suspicious"]
                ),
            },
        }

    except Exception as exc:
        error = str(exc)

        record_tool_call(
            tool_name=tool_name,
            arguments=arguments,
            success=False,
            result_preview={
                "error": error,
            },
        )

        return {
            "success": False,
            "tool": tool_name,
            "error": error,
        }