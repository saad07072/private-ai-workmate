import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

TIMEOUT = 20.0


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def _request(
    method: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> Any:
    url = f"{GITHUB_API_BASE}{endpoint}"

    try:
        response = httpx.request(
            method=method,
            url=url,
            headers=_headers(),
            params=params,
            timeout=TIMEOUT,
        )
    except httpx.RequestError as exc:
        raise RuntimeError(
            f"GitHub connection failed: {exc}"
        ) from exc

    if response.status_code == 401:
        raise RuntimeError(
            "GitHub authentication failed. "
            "Check GITHUB_TOKEN."
        )

    if response.status_code == 403:
        raise RuntimeError(
            "GitHub API access was denied or rate limited."
        )

    if response.status_code == 404:
        raise RuntimeError(
            "GitHub repository or resource was not found."
        )

    if response.status_code >= 400:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"GitHub API error ({response.status_code}): {detail}"
        )

    return response.json()


def _validate_repo(repository: str) -> str:
    repository = repository.strip()

    parts = repository.split("/")

    if len(parts) != 2:
        raise ValueError(
            "Repository must use the format owner/name."
        )

    owner, name = parts

    if not owner or not name:
        raise ValueError(
            "Repository must use the format owner/name."
        )

    if len(repository) > 200:
        raise ValueError("Repository name is too long.")

    return repository


def get_repository(repository: str) -> dict:
    repository = _validate_repo(repository)

    data = _request(
        "GET",
        f"/repos/{repository}",
    )

    return {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "private": data.get("private"),
        "default_branch": data.get("default_branch"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "size_kb": data.get("size"),
        "html_url": data.get("html_url"),
    }


def list_repository_files(
    repository: str,
    path: str = "",
    ref: str | None = None,
) -> dict:
    repository = _validate_repo(repository)

    repo = get_repository(repository)

    branch = ref or repo["default_branch"]

    endpoint = (
        f"/repos/{repository}/git/trees/{branch}"
    )

    data = _request(
        "GET",
        endpoint,
        params={"recursive": "1"},
    )

    if data.get("truncated"):
        warning = (
            "GitHub truncated the repository tree because "
            "the repository contains many files."
        )
    else:
        warning = None

    files = []

    for item in data.get("tree", []):
        item_path = item.get("path", "")

        if path:
            normalized_path = path.strip("/")

            if not (
                item_path == normalized_path
                or item_path.startswith(
                    normalized_path + "/"
                )
            ):
                continue

        files.append(
            {
                "path": item_path,
                "type": item.get("type"),
                "size": item.get("size"),
            }
        )

    files = files[:300]

    return {
        "repository": repository,
        "ref": branch,
        "path": path,
        "files": files,
        "count": len(files),
        "warning": warning,
    }


def read_repository_file(
    repository: str,
    path: str,
    ref: str | None = None,
) -> dict:
    repository = _validate_repo(repository)

    path = path.strip("/")

    if not path:
        raise ValueError("File path is required.")

    if len(path) > 500:
        raise ValueError("File path is too long.")

    repo = get_repository(repository)

    branch = ref or repo["default_branch"]

    endpoint = (
        f"/repos/{repository}/contents/{path}"
    )

    data = _request(
        "GET",
        endpoint,
        params={"ref": branch},
    )

    if isinstance(data, list):
        raise ValueError(
            "The requested path is a directory, not a file."
        )

    content = data.get("content", "")
    encoding = data.get("encoding")

    if encoding != "base64":
        raise RuntimeError(
            "GitHub returned an unsupported file encoding."
        )

    import base64

    try:
        decoded = base64.b64decode(content)
        text = decoded.decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(
            "Unable to decode the GitHub file."
        ) from exc

    max_chars = 30000

    truncated = len(text) > max_chars

    if truncated:
        text = text[:max_chars]

    return {
        "repository": repository,
        "path": path,
        "ref": branch,
        "content": text,
        "truncated": truncated,
        "size": data.get("size"),
        "html_url": data.get("html_url"),
    }


def search_repository_code(
    repository: str,
    query: str,
    limit: int = 10,
) -> dict:
    repository = _validate_repo(repository)

    query = query.strip()

    if not query:
        raise ValueError("Search query is required.")

    if len(query) > 200:
        raise ValueError("Search query is too long.")

    limit = max(1, min(limit, 20))

    search_query = f"{query} repo:{repository}"

    data = _request(
        "GET",
        "/search/code",
        params={
            "q": search_query,
            "per_page": limit,
        },
    )

    results = []

    for item in data.get("items", []):
        results.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "html_url": item.get("html_url"),
                "repository": item.get(
                    "repository", {}
                ).get("full_name"),
            }
        )

    return {
        "repository": repository,
        "query": query,
        "results": results,
        "count": len(results),
    }


def list_repository_issues(
    repository: str,
    state: str = "open",
    limit: int = 10,
) -> dict:
    repository = _validate_repo(repository)

    state = state.lower()

    if state not in {"open", "closed", "all"}:
        raise ValueError(
            "State must be open, closed, or all."
        )

    limit = max(1, min(limit, 20))

    data = _request(
        "GET",
        f"/repos/{repository}/issues",
        params={
            "state": state,
            "per_page": limit,
        },
    )

    issues = []

    for item in data:
        # GitHub's issues endpoint can also return PRs.
        if item.get("pull_request"):
            continue

        issues.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "user": (
                    item.get("user") or {}
                ).get("login"),
                "labels": [
                    label.get("name")
                    for label in item.get("labels", [])
                ],
                "html_url": item.get("html_url"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }
        )

    return {
        "repository": repository,
        "state": state,
        "issues": issues,
        "count": len(issues),
    }


def get_pull_request(
    repository: str,
    pull_number: int,
) -> dict:
    repository = _validate_repo(repository)

    if pull_number <= 0:
        raise ValueError(
            "Pull request number must be positive."
        )

    data = _request(
        "GET",
        f"/repos/{repository}/pulls/{pull_number}",
    )

    return {
        "repository": repository,
        "number": data.get("number"),
        "title": data.get("title"),
        "state": data.get("state"),
        "draft": data.get("draft"),
        "user": (
            data.get("user") or {}
        ).get("login"),
        "base": (
            data.get("base") or {}
        ).get("ref"),
        "head": (
            data.get("head") or {}
        ).get("ref"),
        "body": (data.get("body") or "")[:10000],
        "changed_files": data.get("changed_files"),
        "additions": data.get("additions"),
        "deletions": data.get("deletions"),
        "commits": data.get("commits"),
        "mergeable": data.get("mergeable"),
        "html_url": data.get("html_url"),
    }