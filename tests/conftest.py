"""Shared test fixtures for all test modules."""

import pytest

from github_crawler.crawlers import GithubRepositoryCrawler, GithubSearchCrawler


@pytest.fixture
def search_crawler():
    return GithubSearchCrawler(proxies=["1.2.3.4:8080"])


@pytest.fixture
def search_crawler_no_proxy():
    return GithubSearchCrawler(proxies=[])


@pytest.fixture
def repo_crawler():
    return GithubRepositoryCrawler(proxies=["1.2.3.4:8080"])


@pytest.fixture
def repo_crawler_no_proxy():
    return GithubRepositoryCrawler(proxies=[])
