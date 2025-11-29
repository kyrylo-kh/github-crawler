from dataclasses import dataclass, field

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configurable via environment variables."""

    model_config = ConfigDict(env_prefix="GITHUB_CRAWLER_")

    request_timeout: float = 10.0
    user_agents: list[str] = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]


@dataclass(slots=True)
class SelectorConfig:
    """CSS selectors for scraping GitHub pages."""

    search_results: dict[str, list[str]] = field(
        default_factory=lambda: {
            "Repositories": [
                "div[data-testid='results-list'] h3 a",
                "div.search-title > a",
                "a.v-align-middle",
                "li.repo-list-item h3 a",
            ],
            "Issues": [
                'div[data-testid="results-list"] h3 a[href*="/issues/"]',
                'div.issue-list-item h3 a[href*="/issues/"]',
            ],
            "Wikis": [
                "div.search-title > a",
                "h3.mb-1 > a",
            ],
        }
    )

    repository_details: dict[str, str] = field(
        default_factory=lambda: {
            "languages": "div.Layout-sidebar .BorderGrid-cell ul.list-style-none li",
        }
    )


settings = Settings()
selectors = SelectorConfig()
