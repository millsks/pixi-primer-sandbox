---
type: Playbook
title: Importing Existing Environments into Pixi
description: Step-by-step procedures for importing conda, pip, PEP 621, Poetry, uv, PDM, and Pipenv dependency specs into a pixi workspace, pinning python=3.14.* in [dependencies] for every PyPI-derived format.
tags: [pixi, conda, pypi, migration, runbook]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T00:34:40Z }
verified: { by: human:millsks, at: 2026-09-21T00:34:40Z }
stale_after: 2027-03-20T00:00:00Z
sources:
  - id: pixi-import-help
    resource: cli:pixi/0.81.0/import --help
    title: pixi import --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-import
    resource: https://pixi.sh/latest/reference/cli/pixi/import/
    title: pixi import — CLI reference
  - id: pixi-docs-pyproject
    resource: https://pixi.sh/latest/python/pyproject_toml/
    title: pixi — pyproject.toml manifest support
---

# Importing Existing Environments into Pixi

Verified against `pixi 0.81.0`. `pixi import` supports exactly two formats:

```
--format <FORMAT>   [possible values: conda-env, pypi-txt]
```

Every other ecosystem (Poetry, uv, PDM, Pipenv, PEP 621 `pyproject.toml`) is
imported by first exporting it to a `requirements.txt` and then running the
`pypi-txt` flow. Only the `conda-env` format carries a Python pin across; for
every PyPI-derived format you must add `python=3.14.*` yourself so it lands in
`[dependencies]` (conda-forge), not `[pypi-dependencies]`.

Conventions used below:

- All commands run from the workspace root (the directory containing `pixi.toml`).
- `pixi init` is always used to create the manifest — never hand-write `pixi.toml`.
- Pixi config stays in `pixi.toml`; `pyproject.toml` is for Python tool config only.
- `<feature>` is optional. Omit `-f <feature>` everywhere to write into the default environment.

---

## 1. Conda `environment.yml` (`--format conda-env`)

The only format that maps both conda and pip sections natively.

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Import the file:
   ```sh
   pixi import --format conda-env environment.yml
   # or into a named feature/environment:
   pixi import --format conda-env -f <feature> environment.yml
   ```
   - Top-level conda entries go to `[dependencies]` (or `[feature.<feature>.dependencies]`).
   - A nested `pip:` list goes to `[pypi-dependencies]`.
   - `channels:` are appended to `[workspace].channels`.
3. Check the Python pin. If the YAML pinned an older Python (e.g. `python=3.13`), bump it:
   ```sh
   pixi add python=3.14.*
   # or: pixi add -f <feature> python=3.14.*
   ```
   If the YAML had no `python` entry at all, the same command adds it.
4. Remove the `pip = "*"` entry the import carries over — pixi installs PyPI deps with uv, so `pip` is not needed:
   ```sh
   pixi remove pip
   ```
5. Solve and install:
   ```sh
   pixi install
   ```
6. Review `pixi.toml` and `pixi.lock`; commit both.

---

## 2. pip `requirements.txt` (`--format pypi-txt`)

The base flow every other PyPI format funnels into.

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Add Python **before** importing, so the solver has an interpreter to resolve PyPI wheels against:
   ```sh
   pixi add python=3.14.*
   # or: pixi add -f <feature> python=3.14.*
   ```
3. Flatten the requirements file if it uses `-r other.txt` includes or `--index-url` options — `pypi-txt` does not honor them:
   ```sh
   pixi exec uv pip compile requirements.txt --no-header --no-annotate -o requirements.flat.txt
   ```
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   # or: pixi import --format pypi-txt -f <feature> requirements.flat.txt
   ```
   Everything lands in `[pypi-dependencies]`; nothing is remapped to conda-forge.
5. Move packages that exist on conda-forge into `[dependencies]` (conda-forge first). For each package:
   ```sh
   pixi remove --pypi <pkg>
   pixi add <pkg>
   ```
   `pixi add` fails fast if the package is not on conda-forge — leave those in `[pypi-dependencies]`.
6. Solve and install:
   ```sh
   pixi install
   ```
7. Review `pixi.toml` and `pixi.lock`; commit both.

---

## 3. PEP 621 `pyproject.toml` (`[project.dependencies]`)

Not an import format. Export the dependency list to `requirements.txt` and follow §2.

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
   Do **not** use `pixi init --pyproject` — that embeds pixi config into `pyproject.toml`.
2. Add Python:
   ```sh
   pixi add python=3.14.*
   ```
3. Export `[project.dependencies]` (and optional extras) to a flat requirements file:
   ```sh
   pixi exec uv pip compile pyproject.toml --no-header --no-annotate -o requirements.flat.txt
   # include extras with: --extra dev --extra docs
   ```
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   ```
5. Add the project itself as an editable install:
   ```sh
   pixi add --pypi --editable "<package_name> @ ."
   ```
6. Move conda-forge-available packages to `[dependencies]` (see §2 step 5).
7. Solve and install:
   ```sh
   pixi install
   ```
8. Strip runtime deps from `pyproject.toml` if the project convention is "tool config only"; otherwise leave `[project]` as the packaging source of truth.

---

## 4. Poetry (`[tool.poetry.dependencies]`, `poetry.lock`)

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Add Python:
   ```sh
   pixi add python=3.14.*
   ```
3. Export from Poetry (requires the `poetry-plugin-export` plugin on Poetry ≥ 1.2):
   ```sh
   poetry export -f requirements.txt --without-hashes -o requirements.flat.txt
   # include groups with: --with dev --with docs
   ```
   `poetry export` already resolves `poetry.lock`, so the output is flat and pinned.
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   ```
5. Add the project itself as an editable install:
   ```sh
   pixi add --pypi --editable "<package_name> @ ."
   ```
6. Move conda-forge-available packages to `[dependencies]` (see §2 step 5).
7. Solve and install:
   ```sh
   pixi install
   ```
8. Remove `poetry.lock` and the `[tool.poetry]` / `[build-system] requires = ["poetry-core"]` tables once the pixi environment is verified. Switch `[build-system]` to `hatchling` or `setuptools`.

---

## 5. uv (`uv.lock`, `[dependency-groups]`, `[tool.uv]`)

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Add Python:
   ```sh
   pixi add python=3.14.*
   ```
3. Export from uv (resolves `uv.lock`, so the output is flat and pinned):
   ```sh
   uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.flat.txt
   # include dependency groups with: --group dev --group docs
   ```
   `--no-emit-project` keeps the local project out of the list; it is added as editable in step 5.
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   ```
5. Add the project itself as an editable install:
   ```sh
   pixi add --pypi --editable "<package_name> @ ."
   ```
6. Move conda-forge-available packages to `[dependencies]` (see §2 step 5).
7. Solve and install:
   ```sh
   pixi install
   ```
8. Delete `uv.lock` and `.venv/` and remove `[tool.uv]` once the pixi environment is verified. Two lockfiles in one repo drift silently.

---

## 6. PDM (`pdm.lock`, `[tool.pdm]`)

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Add Python:
   ```sh
   pixi add python=3.14.*
   ```
3. Export from PDM:
   ```sh
   pdm export -f requirements --without-hashes -o requirements.flat.txt
   # include groups with: -G dev -G docs
   ```
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   ```
5. Add the project itself as an editable install:
   ```sh
   pixi add --pypi --editable "<package_name> @ ."
   ```
6. Move conda-forge-available packages to `[dependencies]` (see §2 step 5).
7. Solve and install:
   ```sh
   pixi install
   ```
8. Delete `pdm.lock` and `.pdm-python` and remove `[tool.pdm]` once verified.

---

## 7. Pipenv (`Pipfile`, `Pipfile.lock`)

1. Create the workspace if it does not exist:
   ```sh
   pixi init .
   ```
2. Add Python:
   ```sh
   pixi add python=3.14.*
   ```
3. Export from Pipenv:
   ```sh
   pipenv requirements > requirements.flat.txt
   # include dev packages with: --dev
   ```
4. Import:
   ```sh
   pixi import --format pypi-txt requirements.flat.txt
   ```
5. Move conda-forge-available packages to `[dependencies]` (see §2 step 5).
6. Solve and install:
   ```sh
   pixi install
   ```
7. Delete `Pipfile` and `Pipfile.lock` once verified.

---

## Post-import checklist (all formats)

- [ ] `python = "3.14.*"` is present in `[dependencies]` (or `[feature.<feature>.dependencies]`), not `[pypi-dependencies]`.
- [ ] `[workspace].platforms` lists every target platform (`pixi workspace platform add linux-64` etc.).
- [ ] `pip` is not in `[dependencies]` unless something genuinely needs it at runtime.
- [ ] Packages available on conda-forge live in `[dependencies]`; only the remainder is in `[pypi-dependencies]`.
- [ ] Old lockfiles (`poetry.lock`, `uv.lock`, `pdm.lock`, `Pipfile.lock`) and virtualenvs (`.venv/`) are removed.
- [ ] `.pixi/` and `requirements.flat.txt` are in `.gitignore`.
- [ ] Standard tasks (`fmt`, `lint`, `check`, `test`, `cov`, `ci`, …) are added to `[tasks]`.
- [ ] `pixi install` succeeds and `pixi.lock` is committed alongside `pixi.toml`.
