import os
from unittest.mock import AsyncMock, patch

import orjson
import pytest

from github_crawler.cli import run


@pytest.fixture
def input_file(tmp_path):
    f = tmp_path / "input.json"
    data = {"keywords": ["test"], "proxies": ["1.2.3.4"], "item_type": "Repositories"}
    f.write_bytes(orjson.dumps(data))
    return str(f)


@pytest.fixture
def output_file(tmp_path):
    return str(tmp_path / "output.json")


@pytest.mark.asyncio
async def test_run_success(input_file, output_file):
    with patch("github_crawler.cli.GithubSearchCrawler") as MockCrawler:
        mock_instance = MockCrawler.return_value
        mock_instance.crawl = AsyncMock(return_value=[{"url": "http://test.com"}])

        await run(input_file, output_file)

        MockCrawler.assert_called_once()
        mock_instance.crawl.assert_called_once_with(["test"], "Repositories")

        assert os.path.exists(output_file)
        with open(output_file, "rb") as f:
            data = orjson.loads(f.read())
            assert len(data) == 1
            assert data[0]["url"] == "http://test.com"


@pytest.mark.asyncio
async def test_run_file_not_found(output_file):
    with pytest.raises(SystemExit) as e:
        await run("nonexistent.json", output_file)
    assert e.value.code == 1


@pytest.mark.asyncio
async def test_run_invalid_json(tmp_path, output_file):
    f = tmp_path / "invalid.json"
    f.write_bytes(b"{invalid")

    with pytest.raises(SystemExit) as e:
        await run(str(f), output_file)
    assert e.value.code == 1


@pytest.mark.asyncio
async def test_run_no_keywords(tmp_path, output_file):
    f = tmp_path / "nokeywords.json"
    f.write_bytes(orjson.dumps({"proxies": []}))

    with pytest.raises(SystemExit) as e:
        await run(str(f), output_file)
    assert e.value.code == 1


def test_main(input_file, output_file):
    with patch("sys.argv", ["crawler", input_file, output_file]):
        with patch("github_crawler.cli.run", new_callable=AsyncMock) as mock_run:
            from github_crawler.cli import main

            main()
            mock_run.assert_called_once_with(input_file, output_file)
