import pytest
import respx
from httpx import Response


@pytest.mark.asyncio
async def test_search_repositories_success(search_crawler):
    html_content = """
    <html>
        <body>
            <div class="search-title">
                <a href="/user/repo">Repo Name</a>
            </div>
        </body>
    </html>
    """

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=html_content))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 1
        assert results[0]["url"] == "https://github.com/user/repo"


@pytest.mark.asyncio
async def test_search_fallback_selector(search_crawler):
    """Test fallback selector mechanism."""
    html_content = """
    <html>
        <body>
            <a class="v-align-middle" href="/user/fallback">Fallback Repo</a>
        </body>
    </html>
    """

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=html_content))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 1
        assert results[0]["url"] == "https://github.com/user/fallback"


@pytest.mark.asyncio
async def test_crawl_wrapper(search_crawler):
    """Test full crawl with repository details."""
    search_html = """
    <div class="search-title"><a href="/user/repo">Repo</a></div>
    """
    repo_html = """
    <div class="Layout-sidebar">
        <div class="BorderGrid-cell">
            <ul class="list-style-none">
                <li>
                    <span>Python</span>
                    <span>100%</span>
                </li>
            </ul>
        </div>
    </div>
    """

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=search_html))
        respx.get("https://github.com/user/repo").mock(return_value=Response(200, content=repo_html))

        results = await search_crawler.crawl(["test"], "Repositories", max_pages=1)

        assert len(results) == 1
        assert results[0]["url"] == "https://github.com/user/repo"
        assert results[0]["extra"]["owner"] == "user"
        assert results[0]["extra"]["language_stats"] == {"Python": 100.0}


@pytest.mark.asyncio
async def test_search_empty_results(search_crawler):
    """Test search with no results."""
    html_content = "<html><body></body></html>"

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=html_content))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_network_error(search_crawler):
    """Test network exception handling."""
    async with respx.mock:
        respx.get("https://github.com/search").mock(side_effect=Exception("Network Error"))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_timeout_error(search_crawler):
    """Test timeout exception handling."""
    import httpx

    async with respx.mock:
        respx.get("https://github.com/search").mock(side_effect=httpx.TimeoutException("Request timeout"))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_http_error(search_crawler):
    """Test HTTP error status codes."""
    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(500, content=b"Server Error"))

        results = await search_crawler.search(["test"], "Repositories")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_crawl_non_repository_search(search_crawler_no_proxy):
    """Test crawl with non-Repository search types (Issues, Wikis)."""
    html = """
    <div data-testid="results-list">
        <h3><a href="/repo/name/issues/1">Issue Title</a></h3>
    </div>
    """

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=html))

        results = await search_crawler_no_proxy.crawl(["bug"], "Issues")

        assert len(results) == 1
        assert "issues/1" in results[0]["url"]
        assert "language_stats" not in results[0].get("extra", {})


@pytest.mark.asyncio
async def test_crawl_empty_results(search_crawler_no_proxy):
    """Test crawl with empty search results."""
    html = "<html><body></body></html>"

    async with respx.mock:
        respx.get("https://github.com/search").mock(return_value=Response(200, content=html))

        results = await search_crawler_no_proxy.crawl(["nonexistent"], "Repositories")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_no_proxy_crawler(search_crawler_no_proxy):
    """Test crawler without proxies."""
    assert search_crawler_no_proxy._get_random_proxy() is None


@pytest.mark.asyncio
async def test_proxy_selection(search_crawler):
    """Test proxy selection."""
    proxy = search_crawler._get_random_proxy()
    assert proxy == "http://1.2.3.4:8080"
