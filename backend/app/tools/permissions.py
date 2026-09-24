import os
import re


TOOL_MODE = os.getenv(
    "WORKMATE_TOOL_MODE",
    "read_only",
).strip().lower()


# ---------------------------------------------------------
# Tool capabilities
# ---------------------------------------------------------

TOOL_POLICIES = {
    "calculator": {
        "capability": "local_compute",
        "risk": "low",
        "mode": "read_only",
    },
    "current_time": {
        "capability": "local_time",
        "risk": "low",
        "mode": "read_only",
    },
    "list_documents": {
        "capability": "private_document_read",
        "risk": "private",
        "mode": "read_only",
    },
    "search_documents": {
        "capability": "private_document_search",
        "risk": "private",
        "mode": "read_only",
    },
    "read_document": {
        "capability": "private_document_read",
        "risk": "private",
        "mode": "read_only",
    },
    "github_repo_info": {
        "capability": "github_read",
        "risk": "network_read",
        "mode": "read_only",
    },
    "github_list_files": {
        "capability": "github_read",
        "risk": "network_read",
        "mode": "read_only",
    },
    "github_read_file": {
        "capability": "github_read",
        "risk": "network_read",
        "mode": "read_only",
    },
    "github_search_code": {
        "capability": "github_search",
        "risk": "network_read",
        "mode": "read_only",
    },
    "github_list_issues": {
        "capability": "github_read",
        "risk": "network_read",
        "mode": "read_only",
    },
    "github_pull_request": {
        "capability": "github_read",
        "risk": "network_read",
        "mode": "read_only",
    },
}


ALLOWED_TOOLS = set(TOOL_POLICIES)


REPOSITORY_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)


def is_tool_allowed(
    tool_name: str,
) -> bool:
    if TOOL_MODE != "read_only":
        return False

    return tool_name in ALLOWED_TOOLS


def get_tool_policy(
    tool_name: str,
) -> dict | None:
    return TOOL_POLICIES.get(
        tool_name
    )


def _validate_repository(
    repository: str,
):
    if not isinstance(
        repository,
        str,
    ):
        raise ValueError(
            "Repository must be a string."
        )

    if len(repository) > 200:
        raise ValueError(
            "Repository name is too long."
        )

    if not REPOSITORY_PATTERN.fullmatch(
        repository
    ):
        raise ValueError(
            "Repository must use owner/name format."
        )


def _validate_path(
    path: str,
):
    if not isinstance(
        path,
        str,
    ):
        raise ValueError(
            "Path must be a string."
        )

    if len(path) > 500:
        raise ValueError(
            "Path is too long."
        )

    if "\x00" in path:
        raise ValueError(
            "Path contains an invalid character."
        )

    normalized = path.replace(
        "\\",
        "/",
    )

    if normalized.startswith("/"):
        raise ValueError(
            "Absolute paths are not allowed."
        )

    parts = normalized.split("/")

    if ".." in parts:
        raise ValueError(
            "Path traversal is not allowed."
        )


def validate_tool_arguments(
    tool_name: str,
    arguments: dict,
):
    if not isinstance(
        arguments,
        dict,
    ):
        raise ValueError(
            "Tool arguments must be a JSON object."
        )

    # -----------------------------------------------------
    # Calculator
    # -----------------------------------------------------

    if tool_name == "calculator":
        expression = arguments.get(
            "expression"
        )

        if not isinstance(
            expression,
            str,
        ):
            raise ValueError(
                "Calculator expression must be a string."
            )

        if not expression.strip():
            raise ValueError(
                "Calculator expression cannot be empty."
            )

        if len(expression) > 200:
            raise ValueError(
                "Calculator expression is too long."
            )

    # -----------------------------------------------------
    # Document tools
    # -----------------------------------------------------

    elif tool_name == "search_documents":
        query = arguments.get(
            "query"
        )

        if not isinstance(
            query,
            str,
        ):
            raise ValueError(
                "Document search query must be a string."
            )

        if len(query) > 1000:
            raise ValueError(
                "Document search query is too long."
            )

        limit = arguments.get(
            "limit",
            5,
        )

        if not isinstance(
            limit,
            int,
        ):
            raise ValueError(
                "Document search limit must be an integer."
            )

        if not 1 <= limit <= 10:
            raise ValueError(
                "Document search limit must be between 1 and 10."
            )

    elif tool_name == "read_document":
        document_id = arguments.get(
            "document_id"
        )

        if not isinstance(
            document_id,
            int,
        ):
            raise ValueError(
                "Document ID must be an integer."
            )

        if document_id <= 0:
            raise ValueError(
                "Document ID must be positive."
            )

    # -----------------------------------------------------
    # GitHub tools
    # -----------------------------------------------------

    elif tool_name.startswith(
        "github_"
    ):
        repository = arguments.get(
            "repository"
        )

        _validate_repository(
            repository
        )

        if tool_name == "github_list_files":
            path = arguments.get(
                "path",
                "",
            )

            _validate_path(
                path
            )

            ref = arguments.get(
                "ref"
            )

            if ref is not None:
                if not isinstance(
                    ref,
                    str,
                ):
                    raise ValueError(
                        "GitHub ref must be a string."
                    )

                if len(ref) > 200:
                    raise ValueError(
                        "GitHub ref is too long."
                    )

        elif tool_name == "github_read_file":
            path = arguments.get(
                "path"
            )

            if path is None:
                raise ValueError(
                    "GitHub file path is required."
                )

            _validate_path(
                path
            )

            ref = arguments.get(
                "ref"
            )

            if ref is not None:
                if not isinstance(
                    ref,
                    str,
                ):
                    raise ValueError(
                        "GitHub ref must be a string."
                    )

                if len(ref) > 200:
                    raise ValueError(
                        "GitHub ref is too long."
                    )

        elif tool_name == "github_search_code":
            query = arguments.get(
                "query"
            )

            if not isinstance(
                query,
                str,
            ):
                raise ValueError(
                    "GitHub search query must be a string."
                )

            if not query.strip():
                raise ValueError(
                    "GitHub search query cannot be empty."
                )

            if len(query) > 500:
                raise ValueError(
                    "GitHub search query is too long."
                )

            limit = arguments.get(
                "limit",
                10,
            )

            if not isinstance(
                limit,
                int,
            ):
                raise ValueError(
                    "GitHub search limit must be an integer."
                )

            if not 1 <= limit <= 20:
                raise ValueError(
                    "GitHub search limit must be between 1 and 20."
                )

        elif tool_name == "github_list_issues":
            state = arguments.get(
                "state",
                "open",
            )

            if state not in {
                "open",
                "closed",
                "all",
            }:
                raise ValueError(
                    "Invalid GitHub issue state."
                )

            limit = arguments.get(
                "limit",
                10,
            )

            if not isinstance(
                limit,
                int,
            ):
                raise ValueError(
                    "GitHub issue limit must be an integer."
                )

            if not 1 <= limit <= 20:
                raise ValueError(
                    "GitHub issue limit must be between 1 and 20."
                )

        elif tool_name == "github_pull_request":
            pull_number = arguments.get(
                "pull_number"
            )

            if not isinstance(
                pull_number,
                int,
            ):
                raise ValueError(
                    "Pull request number must be an integer."
                )

            if pull_number <= 0:
                raise ValueError(
                    "Pull request number must be positive."
                )