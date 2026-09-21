---
type: Tutorial
title: Building Conda Packages with pixi-build (preview)
description: Turn a workspace into a buildable conda package with the pixi-build preview — the [package] table, pixi-build-python backend, host/run dependencies, depending on your own package by path, and producing a .conda artifact with pixi build.
tags: [pixi, pixi-build, conda-package, packaging, preview, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2026-12-21T00:00:00Z
sources:
  - id: pixi-build-help
    resource: cli:pixi/0.81.0/build --help
    title: pixi build --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-build-python
    resource: https://pixi.prefix.dev/latest/build/python/
    title: pixi — building a Python package
  - id: pixi-build-backends
    resource: https://github.com/prefix-dev/pixi-build-backends
    title: prefix-dev/pixi-build-backends
---

# Building Conda Packages with pixi-build (preview)

Verified against `pixi 0.81.0` with `pixi-build-python`. **This is a preview feature** —
the manifest schema and backend versions move faster than the rest of pixi, which is why this
document has a shorter `stale_after`. Re-run the lab before trusting it after a pixi upgrade.

Until now the workspace has *consumed* packages. pixi-build lets the workspace also *be* a
package: pixi builds it into a `.conda` file, and other workspaces (or your own) can depend on
it by path, git, or channel. For pure-Python code this is an alternative to publishing wheels
to an internal PyPI index.

## Setup

```sh
mkdir -p sandbox && cd sandbox
pixi init build-lab && cd build-lab
mkdir -p src/build_lab
printf 'def hello() -> str:\n    return "hello from build_lab"\n' > src/build_lab/__init__.py
```

A standard `pyproject.toml` — this is what the Python build backend (hatchling) reads:

```sh
cat > pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "build-lab"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["src/build_lab"]
TOML
```

---

## 1. Enable the preview and describe the package

```sh
pixi workspace preview add pixi-build
pixi add "python=3.14.*"
```

Append the package tables to `pixi.toml` (no CLI writes these yet):

```sh
cat >> pixi.toml <<'TOML'

[package]
name = "build-lab"
version = "0.1.0"

[package.build]
backend = { name = "pixi-build-python", version = "*" }

[package.host-dependencies]
hatchling = "*"
python = "3.14.*"

[package.run-dependencies]
python = "3.14.*"
TOML
```

| Table | Meaning |
|---|---|
| `[package]` | name/version of the conda package (may differ from `[workspace]`) |
| `[package.build] backend` | which pixi-build backend compiles the source; `pixi-build-python` wraps PEP 517 (hatchling, setuptools, ...). Others: `pixi-build-cmake`, `pixi-build-rust`, `pixi-build-rattler-build` |
| `[package.host-dependencies]` | needed at build time in the target env (the PEP 517 backend, Python itself) |
| `[package.run-dependencies]` | what the built package declares as runtime `depends:` |
| `[package.build-dependencies]` | build-machine tools (compilers) — not needed for pure Python |

Backends are fetched from `https://prefix.dev/pixi-build-backends` automatically; pin
`version = "0.*"` once you rely on it.

---

## 2. Depend on your own package

```sh
pixi add build-lab --path .
grep build-lab pixi.toml
```

```toml
[dependencies]
python = "3.14.*"
build-lab = { path = "" }
```

(`pixi add --path .` writes `path = ""`; `path = "."` is equivalent and what the docs show.)

Now `pixi install` / `pixi run` builds the package from source and installs the result into
the environment, instead of an editable install:

```sh
pixi run python -c 'import build_lab; print(build_lab.hello())'
pixi list build-lab          # kind: conda, source: path
```

Edit `src/build_lab/__init__.py` and run again — pixi detects the change and rebuilds.
(For day-to-day development an editable PyPI install is still faster; the path dependency is
for verifying the *packaged* form.)

---

## 3. Produce the artifact

```sh
pixi build
ls *.conda                   # build-lab-0.1.0-pyh<hash>_0.conda
pixi build -o dist/
pixi build -t linux-64       # pure-Python packages are noarch, so this succeeds anywhere
```

Inspect what went in (a `.conda` file is a zip of zstd tarballs; `cph` unpacks it):

```sh
pixi exec -s conda-package-handling cph extract build-lab-0.1.0-*.conda --dest out
find out -maxdepth 2
cat out/info/index.json
```

Flags worth knowing: `-c/--clean` (discard incremental build dir), `-b/--build-dir`,
`--path <manifest>` (build a package elsewhere in a monorepo).

---

## 4. Consuming the package from another workspace

By path (monorepo):

```sh
cd .. && pixi init consumer && cd consumer
pixi workspace preview add pixi-build
pixi add "python=3.14.*"
pixi add build-lab --path ../build-lab
pixi run python -c 'import build_lab; print(build_lab.hello())'
```

By git (`pixi add build-lab --git https://github.com/org/build-lab.git --branch main`) or by
uploading the `.conda` to a channel (`pixi upload` / `pixi publish`) and adding that channel —
after which it is an ordinary `pixi add build-lab`.

---

## 5. Cleanup

```sh
cd .. && rm -rf build-lab consumer
pixi clean cache --build --build-backends
```

---

## Key takeaways

- `preview = ["pixi-build"]` + `[package]` + `[package.build] backend` turns a workspace into a package.
- `pixi-build-python` delegates to whatever PEP 517 backend `pyproject.toml` names; keep `pyproject.toml` as the packaging source of truth.
- `pixi add <name> --path .` makes the workspace consume its own built package — the truest local integration test of packaging.
- Preview means preview: pin backend versions and re-run this lab after every pixi upgrade.
