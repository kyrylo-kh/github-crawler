import random

import httpx

from github_crawler.config import settings


class BaseCrawler:
    """Base class for GitHub crawlers providing shared functionality."""

    def __init__(self, proxies: list[str]):
        self.proxies = proxies

    def _get_random_proxy(self) -> str | None:
        """Selects a random proxy from the list."""
        if not self.proxies:
            return None
        return f"http://{random.choice(self.proxies)}"

    def _get_random_user_agent(self) -> str:
        """Returns a random User-Agent from the configuration."""
        return random.choice(settings.user_agents)

    def _get_client(self) -> httpx.AsyncClient:
        """Creates and returns a configured AsyncClient."""
        proxy_url = self._get_random_proxy()
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
        }
        return httpx.AsyncClient(
            proxy=proxy_url, http2=True, timeout=settings.request_timeout, follow_redirects=True, headers=headers
        )
