# build-lab

Lab for [Building Conda Packages with pixi-build](../../docs/pixi-build-packages.md).

```sh
cp -r labs/build-lab sandbox/ && cd sandbox/build-lab
pixi init --format pixi .        # a pyproject.toml is present; force a separate pixi.toml
```

Files:

- `pyproject.toml` — hatchling config the `pixi-build-python` backend delegates to
- `src/build_lab/__init__.py` — the package being built
- `package.toml` — the `[package]` tables to append to `pixi.toml` (`cat package.toml >> pixi.toml`); kept separate because `pixi init` must generate the `[workspace]` half first
