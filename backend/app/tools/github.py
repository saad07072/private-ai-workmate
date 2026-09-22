from app.github.client import (
    get_repository,
    list_repository_files,
    read_repository_file,
    search_repository_code,
    list_repository_issues,
    get_pull_request,
)


def github_repo_info(repository: str):
    return get_repository(repository)


def github_list_files(
    repository: str,
    path: str = "",
    ref: str | None = None,
):
    return list_repository_files(
        repository=repository,
        path=path,
        ref=ref,
    )


def github_read_file(
    repository: str,
    path: str,
    ref: str | None = None,
):
    return read_repository_file(
        repository=repository,
        path=path,
        ref=ref,
    )


def github_search_code(
    repository: str,
    query: str,
    limit: int = 10,
):
    return search_repository_code(
        repository=repository,
        query=query,
        limit=limit,
    )


def github_list_issues(
    repository: str,
    state: str = "open",
    limit: int = 10,
):
    return list_repository_issues(
        repository=repository,
        state=state,
        limit=limit,
    )


def github_pull_request(
    repository: str,
    pull_number: int,
):
    return get_pull_request(
        repository=repository,
        pull_number=pull_number,
    )