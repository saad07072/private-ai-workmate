ALLOWED_TOOLS = {
    "calculator",
    "current_time",
    "list_documents",
    "search_documents",
    "read_document",

    # GitHub developer tools
    "github_repo_info",
    "github_list_files",
    "github_read_file",
    "github_search_code",
    "github_list_issues",
    "github_pull_request",
}


def is_tool_allowed(tool_name: str) -> bool:
    return tool_name in ALLOWED_TOOLS