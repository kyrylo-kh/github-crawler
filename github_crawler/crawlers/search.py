import asyncio
import logging
from dataclasses import asdict

from selectolax.parser import HTMLParser

from github_crawler.config import selectors
from github_crawler.crawlers.base import BaseCrawler
from github_crawler.crawlers.repository import GithubRepositoryCrawler
from github_crawler.schemas import RepoResult

logger = logging.getLogger(__name__)


class GithubSearchCrawler(BaseCrawler):
    """Asynchronous crawler for GitHub search results."""

    BASE_URL = "https://github.com/search"

    async def search(self, keywords: list[str], search_type: str) -> list[dict]:
        """
        Performs a search on GitHub for the given keywords and search type.
        """
        query = "+".join(keywords)
        params = {"q": query, "type": search_type}

        async with self._get_client() as client:
            try:
                logger.info(f"Searching for '{query}' (Type: {search_type})")
                response = await client.get(self.BASE_URL, params=params)

                if response.status_code != 200:
                    logger.error(f"Failed to fetch. Status: {response.status_code}")
                    return []

                return self._parse_search_results(response.content, search_type)

            except Exception as e:
                logger.exception(f"Unexpected error during search: {e}")
                return []

    def _parse_search_results(self, html_content: bytes, search_type: str) -> list[dict]:
        """Parses the HTML content to extract search results using configured selectors."""
        results = []
        tree = HTMLParser(html_content)

        selectors_list = selectors.search_results.get(search_type, selectors.search_results["Repositories"])
        nodes = []

        for selector in selectors_list:
            nodes = tree.css(selector)
            if nodes:
                break

        if not nodes:
            logger.warning(f"No results found for type '{search_type}'.")
            return []

        for node in nodes:
            href = node.attributes.get("href")
            if href:
                full_url = f"https://github.com{href}"
                result_obj = RepoResult(url=full_url)
                results.append(asdict(result_obj))

        return results

    async def crawl(self, keywords: list[str], search_type: str, max_pages: int = 1) -> list[dict]:
        """Main entry point for crawling."""
        results = await self.search(keywords, search_type)

        if search_type != "Repositories" or not results:
            return results

        logger.info(f"Fetching details for {len(results)} repositories...")
        repo_crawler = GithubRepositoryCrawler(self.proxies)

        tasks = [repo_crawler.get_details(r["url"]) for r in results]
        details_list = await asyncio.gather(*tasks)

        for result, details in zip(results, details_list, strict=True):
            result["extra"].update(details)

        return results
