from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RepoResult:
    """Represents a single result from the GitHub search."""

    url: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class InputData:
    """Represents the input data structure for the crawler."""

    keywords: list[str]
    proxies: list[str]
    item_type: str = "Repositories"
