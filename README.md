# typemap-test

Demo testing repo for the PEP 827 prototypes:
- [typemap runtime](https://github.com/vercel/python-typemap)
- [mypy prototype](https://github.com/msullivan/mypy-typemap)

## Setup

Requires [uv](https://docs.astral.sh/uv/).

Since everything is under active development, the pyproject.toml
depends on unpinned github repos, and `uv.lock` is gitignored.

```bash
uv sync --upgrade
```

To try out the test program:
```bash
uv run mypy fastapilike.py
```

```bash
uv run python3 fastapilike.py
```
