from dataclasses import dataclass
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
