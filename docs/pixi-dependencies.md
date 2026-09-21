---
type: Tutorial
title: Managing Dependencies
description: Add, pin, inspect, and remove conda and PyPI dependencies; understand MatchSpec syntax, pinning strategies, editable installs, and the conda-forge-first rule.
tags: [pixi, conda, pypi, dependencies, matchspec, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-add-help
    resource: cli:pixi/0.81.0/add --help
    title: pixi add --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-deps
    resource: https://pixi.prefix.dev/latest/workspace/lockfile/
    title: pixi — dependencies and lockfile
  - id: conda-matchspec
    resource: https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications
    title: conda — package match specifications
---

# Managing Dependencies

Verified against `pixi 0.81.0`. Pixi resolves two ecosystems in one lock: conda packages
(`[dependencies]`, solved by rattler) and PyPI packages (`[pypi-dependencies]`, solved by uv on
top of the conda solution). The rule in this primer is **conda-forge first**: reach for
`--pypi` only when the package is not on conda-forge.

## Setup

```sh
cp -r labs/deps-lab sandbox/ && cd sandbox/deps-lab
pixi init --format pixi .        # a pyproject.toml is present; force a separate pixi.toml
pixi add "python=3.14.*"
```

The lab ships a `pyproject.toml` and `src/deps_lab/` for the editable-install step in §3.

---

## 1. MatchSpec basics (conda)

```sh
pixi add numpy                 # latest, pinned by strategy -> numpy = ">=2.x,<3"
pixi add "pandas>=2.2,<3"      # explicit range kept verbatim
pixi add "scipy=1.16.*"        # wildcard minor
pixi search polars             # check what versions exist before pinning
pixi search "polars>=1.30" -l 5
```

Common MatchSpec forms:

| Spec | Meaning |
|---|---|
| `numpy` | any version |
| `numpy=2.3` | `2.3.*` (conda "fuzzy" equals) |
| `numpy==2.3.1` | exactly 2.3.1 |
| `numpy>=2.3,<3` | range |
| `numpy=2.3.*=*py314*` | version + build-string glob |
| `pytorch::pytorch` | `channel::name` |

Quote anything containing `*`, `<`, `>`, or `|` so zsh/bash do not interpret it.

Inspect the result:

```sh
grep -A6 '^\[dependencies\]' pixi.toml
pixi list numpy
pixi tree numpy
```

---

## 2. Pinning strategies

When you give no version, `pixi add` writes a range derived from the solved version. The
default strategy is `semver`. Override per command with `--pinning-strategy` or persistently in
config (see [pixi-config.md](pixi-config.md)).

```sh
pixi add --pinning-strategy minor  rich      # rich = ">=14.3.2,<14.4"
pixi add --pinning-strategy exact-version httpx   # httpx = "==0.28.1"
pixi add --pinning-strategy no-pin  attrs    # attrs = "*"
```

| Strategy | `1.2.3` becomes | `0.1.0` becomes |
|---|---|---|
| `semver` (default) | `>=1.2.3,<2` | `>=0.1.0,<0.2` |
| `minor` | `>=1.2.3,<1.3` | `>=0.1.0,<0.2` |
| `major` | `>=1.2.3,<2` | `>=0.1.0,<1` |
| `latest-up` | `>=1.2.3` | `>=0.1.0` |
| `exact-version` | `==1.2.3` | `==0.1.0` |
| `no-pin` | `*` | `*` |

Python, Rust, Node, R, GCC and a few others are always minor-pinned regardless of strategy
because they do not follow semver.

---

## 3. PyPI dependencies

```sh
pixi add --pypi structlog
pixi add --pypi "httpx[http2]>=0.28"
grep -A4 '^\[pypi-dependencies\]' pixi.toml
```

Rules of thumb:

- `[dependencies]` must already contain `python` or the add fails.
- Conda and PyPI cannot both provide the same package in one environment; if `numpy` is in
  `[dependencies]`, uv will treat it as satisfied and will not fetch a wheel.
- Conda-forge first. Check with `pixi search <name>` before using `--pypi`. If it exists on
  conda-forge, move it: `pixi remove --pypi <name> && pixi add <name>`.

### Editable install of the workspace package

The lab is a `src/` layout project with a `pyproject.toml`, so the workspace itself can be
installed editable:

```sh
pixi add --pypi --editable "deps-lab @ ."
pixi run python -c "import deps_lab; print(deps_lab.hello())"
```

Writes `deps-lab = { path = ".", editable = true }` into `[pypi-dependencies]`. This is how
the project's own code becomes importable inside the environment.

### Git and local path PyPI deps

```sh
pixi add --pypi "cowsay @ git+https://github.com/VaasuDevanS/cowsay-python.git"
pixi add --pypi mylib --path ../mylib
```

---

## 4. Platform-, feature-, and role-scoped adds

```sh
pixi add --platform linux-64 patchelf          # -> [target.linux-64.dependencies]
pixi add -f test pytest pytest-cov             # -> [feature.test.dependencies]
pixi add --build cmake                         # -> [build-dependencies]   (pixi-build only)
pixi add --host "python=3.14.*"                # -> [host-dependencies]    (pixi-build only)
```

When you add to a feature that is not yet part of any environment, pixi writes `name = "*"`
and tells you to run `pixi upgrade --feature test <pkg>` to pin once the feature is in an
environment. See [pixi-features-environments.md](pixi-features-environments.md).

---

## 5. Removing

```sh
pixi remove numpy
pixi remove --pypi structlog
pixi remove -f test pytest-cov
pixi remove --platform linux-64 patchelf
```

`pixi remove` re-solves and reinstalls so the environment matches the manifest immediately.

---

## 6. Upgrading vs updating

Two different operations — confuse them and you will either fail to get a new major version or
accidentally loosen every pin.

| Command | Touches `pixi.toml`? | Touches `pixi.lock`? | Use when |
|---|---|---|---|
| `pixi update [pkg]` | No | Yes | Refresh locked versions *within* the ranges the manifest already allows |
| `pixi upgrade [pkg]` | Yes | Yes | Raise the manifest range itself to allow a newer version |

```sh
pixi update --dry-run            # what would change inside current ranges
pixi update rich                 # only rich (and what it forces)
pixi upgrade --dry-run           # what manifest ranges would be raised
pixi upgrade rich                # loosen rich's range, re-solve, rewrite both files
pixi upgrade -f test             # only the test feature
pixi upgrade --exclude python    # everything except python
```

Both accept `--json` for scripting.

---

## 7. Inspecting what you have

```sh
pixi list                          # default env, current platform
pixi list --sort-by size           # what is eating disk
pixi list --fields name,version,kind,source
pixi list -e test --platform linux-64
pixi tree                          # full tree
pixi tree -i openssl               # who depends on openssl?
pixi list --json | jq '.[] | select(.is_explicit) | .name'
```

Explicit (manifest-declared) packages are highlighted in `pixi list` and green in `pixi tree`.

---

## 8. Cleanup

```sh
cd .. && rm -rf deps-lab
```

---

## Key takeaways

- `pixi add` is the only way you should be editing `[dependencies]`; it validates the spec, solves, locks, and installs in one step.
- `--pypi` is a fallback, not a default. Search conda-forge first.
- `update` = new lock within existing ranges. `upgrade` = new ranges. Read `--dry-run` output before either.
- Quote your MatchSpecs.
