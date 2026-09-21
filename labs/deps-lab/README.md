# deps-lab

Lab for [Managing Dependencies](../../docs/pixi-dependencies.md). Ships a minimal `src/`
layout package so the editable-install step (`pixi add --pypi --editable "deps-lab @ ."`)
has something to install.

```sh
cp -r labs/deps-lab sandbox/ && cd sandbox/deps-lab
pixi init --format pixi .        # a pyproject.toml is present; force a separate pixi.toml
```

Files:

- `pyproject.toml` — hatchling build config for the `deps_lab` package (Python tool config only; pixi config stays in `pixi.toml`)
- `src/deps_lab/__init__.py` — one function to import after the editable install
