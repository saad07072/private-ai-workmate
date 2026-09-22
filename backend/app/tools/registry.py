from app.tools.builtin import (
    calculator,
    current_time,
    list_documents,
    search_documents,
    read_document,
)

from app.tools.github import (
    github_repo_info,
    github_list_files,
    github_read_file,
    github_search_code,
    github_list_issues,
    github_pull_request,
)


TOOLS = {
    "calculator": {
        "description": (
            "Perform a mathematical calculation. "
            "Use this instead of doing arithmetic yourself."
        ),
        "function": calculator,
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "A mathematical expression such as "
                        "25 * 4 + 10"
                    ),
                }
            },
            "required": ["expression"],
        },
    },

    "current_time": {
        "description": (
            "Get the current local date and time."
        ),
        "function": current_time,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    "list_documents": {
        "description": (
            "List documents uploaded to "
            "Private AI Workmate."
        ),
        "function": list_documents,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    "search_documents": {
        "description": (
            "Search the user's private uploaded "
            "documents using semantic search."
        ),
        "function": search_documents,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "What to search for in "
                        "private documents."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results, "
                        "between 1 and 10."
                    ),
                },
            },
            "required": ["query"],
        },
    },

    "read_document": {
        "description": (
            "Read the text of a specific uploaded "
            "document using its document ID."
        ),
        "function": read_document,
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": (
                        "The uploaded document ID."
                    ),
                }
            },
            "required": ["document_id"],
        },
    },

    # -------------------------------------------------
    # GitHub Developer Tools
    # -------------------------------------------------

    "github_repo_info": {
        "description": (
            "Inspect metadata about a GitHub repository. "
            "Use this when the user asks about a repository, "
            "its language, default branch, stars, forks, "
            "description, or issue count."
        ),
        "function": github_repo_info,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                }
            },
            "required": ["repository"],
        },
    },

    "github_list_files": {
        "description": (
            "List files and directories in a GitHub repository. "
            "Use this to understand a project's structure."
        ),
        "function": github_list_files,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                },
                "path": {
                    "type": "string",
                    "description": (
                        "Optional directory path to narrow the listing."
                    ),
                },
                "ref": {
                    "type": "string",
                    "description": (
                        "Optional branch, tag, or commit."
                    ),
                },
            },
            "required": ["repository"],
        },
    },

    "github_read_file": {
        "description": (
            "Read a source-code or text file from a GitHub repository. "
            "Use this when analyzing implementation details."
        ),
        "function": github_read_file,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                },
                "path": {
                    "type": "string",
                    "description": (
                        "Repository-relative file path."
                    ),
                },
                "ref": {
                    "type": "string",
                    "description": (
                        "Optional branch, tag, or commit."
                    ),
                },
            },
            "required": [
                "repository",
                "path",
            ],
        },
    },

    "github_search_code": {
        "description": (
            "Search source code inside a GitHub repository. "
            "Use this to locate functions, classes, imports, "
            "configuration, errors, or implementation patterns."
        ),
        "function": github_search_code,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                },
                "query": {
                    "type": "string",
                    "description": (
                        "Code search query."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results, "
                        "between 1 and 20."
                    ),
                },
            },
            "required": [
                "repository",
                "query",
            ],
        },
    },

    "github_list_issues": {
        "description": (
            "List issues from a GitHub repository. "
            "Use this to understand reported bugs, tasks, "
            "and project discussions."
        ),
        "function": github_list_issues,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "open",
                        "closed",
                        "all",
                    ],
                    "description": (
                        "Issue state filter."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of issues, "
                        "between 1 and 20."
                    ),
                },
            },
            "required": ["repository"],
        },
    },

    "github_pull_request": {
        "description": (
            "Inspect a GitHub pull request, including its "
            "title, branches, description, changed files, "
            "additions, deletions, commits, and mergeability."
        ),
        "function": github_pull_request,
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in owner/name format."
                    ),
                },
                "pull_number": {
                    "type": "integer",
                    "description": (
                        "Pull request number."
                    ),
                },
            },
            "required": [
                "repository",
                "pull_number",
            ],
        },
    },
}


def get_tool_definitions():
    definitions = []

    for name, tool in TOOLS.items():
        definitions.append(
            {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
        )

    return definitions