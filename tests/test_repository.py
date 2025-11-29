import pytest
import respx
from httpx import Response


@pytest.mark.asyncio
async def test_repo_details_extraction(repo_crawler):
    """Test extraction of owner and languages."""
    url = "https://github.com/owner/repo"
    html_content = """
    <div class="Layout-sidebar">
        <div class="BorderGrid-cell">
            <ul class="list-style-none">
                <li>
                    <span>Rust</span>
                    <span>80.5%</span>
                </li>
                 <li>
                    <span>Python</span>
                    <span>19.5%</span>
                </li>
            </ul>
        </div>
    </div>
    """

    async with respx.mock:
        respx.get(url).mock(return_value=Response(200, content=html_content))

        details = await repo_crawler.get_details(url)

        assert details["owner"] == "owner"
        assert details["language_stats"] == {"Rust": 80.5, "Python": 19.5}


@pytest.mark.asyncio
async def test_repo_details_extraction_fallback(repo_crawler):
    """Test fallback extraction of languages (text-based parsing)."""
    url = "https://github.com/owner/repo"
    html_content = """
    <div class="Layout-sidebar">
        <div class="BorderGrid-cell">
            <ul class="list-style-none">
                <li>
                    Rust 100.0%
                </li>
            </ul>
        </div>
    </div>
    """

    async with respx.mock:
        respx.get(url).mock(return_value=Response(200, content=html_content))

        details = await repo_crawler.get_details(url)

        assert details["owner"] == "owner"
        assert details["language_stats"] == {"Rust": 100.0}


@pytest.mark.asyncio
async def test_get_details_http_error(repo_crawler_no_proxy):
    """Test get_details handles HTTP errors gracefully."""
    url = "https://github.com/owner/repo"

    async with respx.mock:
        respx.get(url).mock(return_value=Response(404, content=b"Not Found"))

        details = await repo_crawler_no_proxy.get_details(url)

        assert details["owner"] == "owner"
        assert details["language_stats"] == {}


@pytest.mark.asyncio
async def test_get_details_network_exception(repo_crawler_no_proxy):
    """Test get_details handles network exceptions."""
    url = "https://github.com/owner/repo"

    async with respx.mock:
        respx.get(url).mock(side_effect=Exception("Network error"))

        details = await repo_crawler_no_proxy.get_details(url)

        assert details["owner"] == "owner"
        assert details["language_stats"] == {}


def test_extract_owner_malformed_url(repo_crawler):
    """Test _extract_owner with malformed URLs."""
    assert repo_crawler._extract_owner("https://github.com") == ""
    assert repo_crawler._extract_owner("https://github.com/") == ""
    assert repo_crawler._extract_owner("invalid") == ""


def test_extract_languages_no_selector(repo_crawler):
    """Test _extract_languages when selector is missing from config."""
    from github_crawler.config import selectors

    original = selectors.repository_details.get("languages")
    selectors.repository_details.pop("languages", None)

    try:
        html = b"<html><body></body></html>"
        result = repo_crawler._extract_languages(html)
        assert result == {}
    finally:
        if original:
            selectors.repository_details["languages"] = original


def test_extract_languages_invalid_percentage(repo_crawler):
    """Test _extract_languages with invalid percentage values."""
    html = b"""
    <div class="Layout-sidebar">
        <div class="BorderGrid-cell">
            <ul class="list-style-none">
                <li>
                    <span>Python</span>
                    <span>invalid%</span>
                </li>
            </ul>
        </div>
    </div>
    """

    result = repo_crawler._extract_languages(html)
    assert result == {}


def test_extract_languages_fallback_invalid_value(repo_crawler):
    """Test _extract_languages fallback with invalid value."""
    html = b"""
    <div class="Layout-sidebar">
        <div class="BorderGrid-cell">
            <ul class="list-style-none">
                <li>Python invalid</li>
            </ul>
        </div>
    </div>
    """

    result = repo_crawler._extract_languages(html)
    assert result == {}
