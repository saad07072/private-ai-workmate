from datetime import datetime, timezone
from pathlib import Path
import json
import re


BASE_DIR = Path(__file__).resolve().parents[2]

AUDIT_DIR = BASE_DIR / "data"

AUDIT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

AUDIT_FILE = AUDIT_DIR / "tool_audit.jsonl"


SECRET_KEY_PATTERN = re.compile(
    r"(api[_-]?key|access[_-]?token|"
    r"auth[_-]?token|password|passwd|"
    r"secret|credential|authorization)",
    re.IGNORECASE,
)


PRIVATE_RESULT_KEYS = {
    "content",
    "text",
    "pages",
    "code",
    "diff",
    "body",
    "document",
    "documents",
    "results",
}


def _redact_value(
    value,
    key: str | None = None,
):
    if key and SECRET_KEY_PATTERN.search(
        key
    ):
        return "[REDACTED]"

    if isinstance(
        value,
        dict,
    ):
        return {
            str(item_key): _redact_value(
                item_value,
                str(item_key),
            )
            for item_key, item_value in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            _redact_value(item)
            for item in value[:20]
        ]

    if isinstance(
        value,
        str,
    ):
        if len(value) > 300:
            return value[:300] + "...[TRUNCATED]"

        return value

    return value


def _safe_result_summary(
    result,
):
    if isinstance(
        result,
        dict,
    ):
        summary = {}

        for key, value in result.items():
            if key in PRIVATE_RESULT_KEYS:
                summary[key] = "[PRIVATE_CONTENT_OMITTED]"
            else:
                summary[key] = _redact_value(
                    value,
                    str(key),
                )

        return summary

    if isinstance(
        result,
        list,
    ):
        return {
            "type": "list",
            "items": len(result),
        }

    return {
        "type": type(result).__name__,
    }


def record_tool_call(
    tool_name: str,
    arguments: dict,
    success: bool,
    result_preview="",
):
    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "event": "tool_call",
        "tool": tool_name,
        "arguments": _redact_value(
            arguments
        ),
        "success": success,
        "result_summary": _safe_result_summary(
            result_preview
        ),
    }

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )


def record_security_event(
    event_type: str,
    details: dict | None = None,
):
    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "event": "security",
        "event_type": event_type,
        "details": _redact_value(
            details or {}
        ),
    }

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )