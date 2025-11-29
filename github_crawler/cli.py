import argparse
import asyncio
import logging
import sys

import orjson

from github_crawler.crawlers import GithubSearchCrawler
from github_crawler.schemas import InputData

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def run(input_file: str, output_file: str):
    """
    Reads input, runs the crawler, and writes output.
    """
    try:
        with open(input_file, "rb") as f:
            raw_data = orjson.loads(f.read())

        input_data = InputData(
            keywords=raw_data.get("keywords", []),
            proxies=raw_data.get("proxies", []),
            item_type=raw_data.get("item_type", "Repositories"),
        )

        if not input_data.keywords:
            logger.error("No keywords provided in input file.")
            sys.exit(1)

        crawler = GithubSearchCrawler(input_data.proxies)

        logger.info(f"Starting crawl for keywords: {input_data.keywords}")
        results = await crawler.crawl(input_data.keywords, input_data.item_type)

        with open(output_file, "wb") as f:
            f.write(orjson.dumps(results, option=orjson.OPT_INDENT_2))

        logger.info(f"Successfully wrote {len(results)} results to {output_file}")

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    except orjson.JSONDecodeError:
        logger.error(f"Invalid JSON in input file: {input_file}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Github Crawler CLI")
    parser.add_argument("input_file", help="Path to the JSON input file")
    parser.add_argument("output_file", help="Path to the JSON output file")

    args = parser.parse_args()

    asyncio.run(run(args.input_file, args.output_file))


if __name__ == "__main__":
    main()
