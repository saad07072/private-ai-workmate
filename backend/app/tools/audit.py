from datetime import datetime, timezone
from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parents[2]

AUDIT_DIR = BASE_DIR / "data"

AUDIT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

AUDIT_FILE = AUDIT_DIR / "tool_audit.jsonl"


def record_tool_call(
    tool_name: str,
    arguments: dict,
    success: bool,
    result_preview: str = "",
):
    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "success": success,
        "result_preview": result_preview[:500],
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