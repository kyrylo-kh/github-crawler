# Github Crawler

A robust, asynchronous Python crawler for Github.

## Features

- **Efficient**: Uses `httpx` for async HTTP requests and `selectolax` for fast HTML parsing.
- **Robust**: Handles network errors, rotates User-Agents, and uses fallback CSS selectors to adapt to GitHub UI changes.
- **Configurable**: Centralized configuration for selectors and proxies.
- **Type-Safe**: Uses `dataclasses` for structured data and `mypy` for static type checking.
- **CLI**: Easy-to-use command-line interface.

## Installation

This project uses `uv` for dependency management.

1.  Install `uv` (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  Install dependencies:
    ```bash
    make install
    ```

## Usage

### Input Format

Create a JSON file (e.g., `input.json`) with the following structure:

```json
{
  "keywords": ["openstack", "nova", "css"],
  "proxies": [],
  "item_type": "Repositories"
}
```

Supported types: `Repositories`, `Issues`, `Wikis`.

### Running the Crawler

Simply run:

```bash
uv run crawler example.json output.json
```

### Output

The results will be saved to `output.json`:

```json
[
  {
    "url": "https://github.com/example/repo",
    "extra": {}
  }
]
```

## Development

### Running Tests

```bash
make test
```

### Linting and Formatting

```bash
make lint
make format
```

## Maintenance

### Updating Selectors

If GitHub changes its UI and the crawler stops finding results, update the CSS selectors in `github_crawler/config.py`.

```python
# github_crawler/config.py
search_results = {
    "Repositories": [
        "div[data-testid='results-list'] h3 a",
        "div.search-title > a",
        "new.selector > a",
    ]
}
```

### CI/CD

This project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs linting and tests on every push.
