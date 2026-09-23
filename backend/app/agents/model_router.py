import os
import re

from dotenv import load_dotenv


load_dotenv()


FAST_MODEL = os.getenv(
    "NEBIUS_FAST_MODEL",
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
)

REASONING_MODEL = os.getenv(
    "NEBIUS_REASONING_MODEL",
    "nvidia/Nemotron-3-Ultra-550b-a55b",
)


# Keywords and patterns that usually indicate a more
# demanding reasoning, coding, architecture, or analysis task.
COMPLEX_PATTERNS = [
    r"\banaly[sz]e\b",
    r"\banalysis\b",
    r"\barchitecture\b",
    r"\barchitect\b",
    r"\bdebug\b",
    r"\bdebugging\b",
    r"\brefactor\b",
    r"\brefactoring\b",
    r"\boptimi[sz]e\b",
    r"\boptimization\b",
    r"\bdesign\b",
    r"\bimplement\b",
    r"\bimplementation\b",
    r"\breview\b",
    r"\bcode review\b",
    r"\broot cause\b",
    r"\bwhy is\b",
    r"\bwhy does\b",
    r"\bcompare\b",
    r"\btrade[- ]?off\b",
    r"\bcomplex\b",
    r"\bmulti[- ]?step\b",
    r"\breason\b",
    r"\breasoning\b",
    r"\bexplain.*code\b",
    r"\bexplain.*architecture\b",
    r"\bfind.*bug\b",
    r"\bfix.*bug\b",
    r"\bsecurity\b",
    r"\bperformance\b",
    r"\bGitHub\b",
    r"\brepository\b",
    r"\bsource code\b",
    r"\bpull request\b",
]


def _latest_user_message(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "")

            if isinstance(content, str):
                return content.strip()

    return ""


def _contains_complex_pattern(text: str) -> bool:
    for pattern in COMPLEX_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def _has_code_or_long_context(text: str) -> bool:
    if len(text) > 1800:
        return True

    code_markers = [
        "```",
        "def ",
        "class ",
        "import ",
        "from ",
        "async ",
        "await ",
        "SELECT ",
        "CREATE TABLE",
        "function ",
        "const ",
        "=>",
        "Traceback",
        "Exception",
    ]

    lowered = text.lower()

    return any(
        marker.lower() in lowered
        for marker in code_markers
    )


def classify_request(messages: list[dict]) -> str:
    """
    Classify the current request as either:

    - fast
    - reasoning

    The classifier is intentionally deterministic so that
    routing remains predictable and easy to evaluate.
    """

    text = _latest_user_message(messages)

    if not text:
        return "fast"

    if _contains_complex_pattern(text):
        return "reasoning"

    if _has_code_or_long_context(text):
        return "reasoning"

    return "fast"


def select_model(messages: list[dict]) -> str:
    """
    Select the appropriate Nebius model for the request.
    """

    route = classify_request(messages)

    if route == "reasoning":
        return REASONING_MODEL

    return FAST_MODEL


def get_route_name(model: str) -> str:
    if model == REASONING_MODEL:
        return "reasoning"

    return "fast"