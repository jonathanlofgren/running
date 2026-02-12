# Contributing

## Setup

Clone the repo and install in editable mode with dev and test dependencies:

```
git clone https://github.com/jonathanlofgren/running.git
cd running
pip install -e .[dev,test]
pre-commit install
```

This installs a pre-commit hook that runs ruff linting and formatting checks automatically on each commit.

## Running tests

```
pytest
```

## Linting and formatting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

Check for issues:

```
ruff check .
ruff format --check .
```

Auto-fix and format:

```
ruff check --fix .
ruff format .
```

## Project structure

The project is a single module (`running.py`) with tests in `tests/`.

## Releasing

Releases are published to PyPI via CI. To trigger a release:

1. Update the version in `pyproject.toml`
2. Merge to `main`
3. Go to Actions > CI > "Run workflow" to trigger the publish
