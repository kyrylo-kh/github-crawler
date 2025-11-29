import logging
from typing import Any

from selectolax.parser import HTMLParser

from github_crawler.config import selectors
from github_crawler.crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class GithubRepositoryCrawler(BaseCrawler):
    """Crawler for fetching detailed repository information."""

    async def get_details(self, url: str) -> dict[str, Any]:
        """
        Fetches details for a single repository.
        """
        owner = self._extract_owner(url)
        languages = {}

        async with self._get_client() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    languages = self._extract_languages(response.content)
                else:
                    logger.warning(f"Failed to fetch details for {url}. Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching details for {url}: {e}")

        return {"owner": owner, "language_stats": languages}

    def _extract_owner(self, url: str) -> str:
        """Extracts the owner from the repository URL."""
        # URL format: https://github.com/owner/repo
        parts = url.rstrip("/").split("/")
        if len(parts) >= 4:
            return parts[3]
        return ""

    def _extract_languages(self, html_content: bytes) -> dict[str, float]:
        """Parses language statistics from the repository page."""
        tree = HTMLParser(html_content)
        languages = {}

        selector = selectors.repository_details.get("languages")
        if not selector:
            return {}

        nodes = tree.css(selector)
        for node in nodes:
            spans = node.css("span")
            if len(spans) >= 2:
                name = spans[0].text(strip=True)
                percent_text = spans[1].text(strip=True).replace("%", "")
                try:
                    languages[name] = float(percent_text)
                except ValueError:
                    pass
            else:
                text = node.text(deep=True, separator=" ").strip()
                parts = text.split()
                if len(parts) >= 2:
                    try:
                        val = float(parts[-1].replace("%", ""))
                        key = " ".join(parts[:-1])
                        languages[key] = val
                    except ValueError:
                        pass

        return languages
