# import-lab

Fixtures for [Importing Existing Environments into Pixi](../../docs/pixi-import-guide.md).
One subdirectory per source format, each describing the *same* small project (Python,
`rich`, `httpx`, `structlog`, plus `pytest` as a dev dependency) so you can compare the
resulting `pixi.toml` across formats.

```sh
cp -r labs/import-lab sandbox/ && cd sandbox/import-lab/<format>
pixi init --format pixi .        # where a pyproject.toml exists this skips the "add to pyproject?" prompt
# then follow the guide section for that format
```

| Directory | Format | Guide section |
|---|---|---|
| `conda/` | `environment.yml` with a `pip:` section | §1 `--format conda-env` |
| `pip/` | `requirements.txt` with a `-r` include (must be flattened first) | §2 `--format pypi-txt` |
| `pep621/` | `pyproject.toml` with `[project.dependencies]` and an extra | §3 |
| `poetry/` | `pyproject.toml` with `[tool.poetry]` | §4 |
| `uv/` | `pyproject.toml` with `[dependency-groups]` and `[tool.uv]` | §5 |
| `pdm/` | `pyproject.toml` with `[tool.pdm]` | §6 |
| `pipenv/` | `Pipfile` | §7 |

The Poetry, uv, PDM, and Pipenv flows call those tools to export a flat requirements file.
Run them through pixi rather than a bare install: `pixi exec poetry ...`, `pixi exec uv ...`,
`pixi exec pdm ...`, `pixi exec pipenv ...`.

Lockfiles (`poetry.lock`, `uv.lock`, `pdm.lock`, `Pipfile.lock`) are deliberately absent;
the export commands resolve from the manifest.
