import asyncio
from dataclasses import dataclass
from typing import Any
from aiohttp import ClientSession
from settings import settings
from aiochclient import ChClient
from datetime import datetime


@dataclass
class RepositoryAuthorCommitsNum:
    author: str
    commits_num: int


@dataclass
class Repository:
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str
    updated: datetime
    authors_commits_num_today: list[RepositoryAuthorCommitsNum]


class GithubReposScrapper:
    def __init__(self, access_token: str) -> None:
        self._session = ClientSession(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
            }
        )
        self._semaphore = asyncio.Semaphore(5)  # Максимальное количество одновременных запросов
        self._requests_per_second = 2  # Ограничение по запросам в секунду
        self._clickhouse_client = ChClient(host=settings.CLICKHOUSE_HOST, database=settings.CLICKHOUSE_DATABASE)
        self._batch_size = 100  # Размер батча для вставки данных

    async def _make_request(self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None) -> Any:
        async with self._session.request(
            method, f"{settings.GITHUB_API_BASE_URL}/{endpoint}", params=params) as response:
            return await response.json()

    async def _get_top_repositories(self, limit: int = 100) -> list[dict[str, Any]]:
        data = await self._make_request(
            endpoint="search/repositories",
            params={"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit},
        )
        return data["items"]

    async def _get_repository_commits(self, owner: str, repo: str) -> list[dict[str, Any]]:
        async with self._semaphore:
            commits = await self._make_request(
                f"repos/{owner}/{repo}/commits", params={"since": "2023-01-01T00:00:00Z"})  # Дата за последний день
            await asyncio.sleep(1 / self._requests_per_second)  # Ограничение по запросам в секунду
            return commits

    async def _insert_into_clickhouse(self, repositories: list[Repository]) -> None:
        repo_batch_data = []
        commits_batch_data = []
        positions_batch_data = []
        current_date = datetime.now().date()

        for repo in repositories:
            # Подготовка данных для таблицы repositories
            repo_batch_data.append((
                repo.name, repo.owner, repo.stars, repo.watchers, repo.forks, repo.language, repo.updated))

            # Подготовка данных для таблицы repositories_authors_commits
            commits_batch_data = [
                (current_date, repo.name, author_commit.author,
                 author_commit.commits_num) for author_commit in repo.authors_commits_num_today]

            # Подготовка данных для таблицы repositories_positions
            positions_batch_data.append((current_date, repo.name, repo.position))

            if len(repo_batch_data) >= self._batch_size:
                await self._clickhouse_client.insert("repositories", repo_batch_data)
                await self._clickhouse_client.insert("repositories_authors_commits", commits_batch_data)
                await self._clickhouse_client.insert("repositories_positions", positions_batch_data)
                repo_batch_data.clear()
                commits_batch_data.clear()
                positions_batch_data.clear()

        if repo_batch_data:
            await self._clickhouse_client.insert("repositories", repo_batch_data)
        if commits_batch_data:
            await self._clickhouse_client.insert("repositories_authors_commits", commits_batch_data)
        if positions_batch_data:
            await self._clickhouse_client.insert("repositories_positions", positions_batch_data)

    async def get_repositories(self) -> list[Repository]:
        repos_data = await self._get_top_repositories()
        repositories = []

        for position, repo_data in enumerate(repos_data):
            owner = repo_data["owner"]["login"]
            repo_name = repo_data["name"]
            stars = repo_data["stargazers_count"]
            watchers = repo_data["watchers_count"]
            forks = repo_data["forks_count"]
            language = repo_data["language"]
            updated = datetime.now()  # Устанавливаем текущее время обновления

            commits = await self._get_repository_commits(owner, repo_name)
            authors_commits_num_today: dict = {}

            for commit in commits:
                author = commit["commit"]["author"]["name"]
                authors_commits_num_today[author] = authors_commits_num_today.get(author, 0) + 1

            authors_commits_list = [RepositoryAuthorCommitsNum(
                author=author, commits_num=num) for author, num in authors_commits_num_today.items()]

            repository = Repository(
                name=repo_name,
                owner=owner,
                position=position,
                stars=stars,
                watchers=watchers,
                forks=forks,
                language=language,
                updated=updated,
                authors_commits_num_today=authors_commits_list,
            )

            repositories.append(repository)

        await self._insert_into_clickhouse(repositories)  # Вставка данных в ClickHouse

        return repositories

    async def close(self) -> None:
        await self._session.close()
