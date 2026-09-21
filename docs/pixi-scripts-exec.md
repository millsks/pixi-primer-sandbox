---
type: Tutorial
title: Single-File Scripts and pixi exec
description: Run tools without a workspace — pixi exec temporary environments, PEP 723 inline-metadata Python scripts with pixi init --script and pixi run --script, and the experimental conda-script block for other languages.
tags: [pixi, exec, pep723, scripts, temporary-environment, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-exec-help
    resource: cli:pixi/0.81.0/exec --help
    title: pixi exec --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-init-help
    resource: cli:pixi/0.81.0/init --help
    title: pixi init --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pep723
    resource: https://peps.python.org/pep-0723/
    title: PEP 723 — Inline script metadata
---

# Single-File Scripts and pixi exec

Verified against `pixi 0.81.0`. Two ways to run things with no `pixi.toml` in sight:

- `pixi exec` — a throwaway environment for one command (the `uvx` / `npx` shape).
- PEP 723 scripts — a Python file that carries its own dependency list; pixi resolves and
  caches an environment for it.

Both replace `uv run` / `uvx` / `pipx run`. Same rule as everywhere in this primer: pixi is
the only runner.

## Setup

```sh
mkdir -p sandbox/scripts-lab && cd sandbox/scripts-lab
```

No `pixi init` this time.

---

## 1. `pixi exec`

Run a tool by name; pixi guesses the package from the command:

```sh
pixi exec cowpy "hello from a temp env"
pixi exec ruff --version
```

Be explicit about the package, version, or extra packages:

```sh
pixi exec -s "python=3.14" python -c 'import sys; print(sys.version)'
pixi exec -s "python=3.12" python -c 'import sys; print(sys.version)'
pixi exec --with rich --with httpx python -c 'import rich, httpx; rich.print("[green]ok[/]")'
pixi exec -c bioconda -c conda-forge samtools --version
pixi exec --list python --version        # print the temp env's packages first
pixi exec -p linux-64 -n ...              # solve for another platform (dry-run only)
```

| Flag | Meaning |
|---|---|
| `-s, --spec` | MatchSpec(s) to install; command is not guessed |
| `-w, --with` | extra MatchSpec(s) in addition to the guessed package |
| `-c, --channel` | channel(s); default `conda-forge` |
| `--force-reinstall` | rebuild the temp env even if cached |
| `--list[=regex]` | list packages before running |

Temp environments are cached under the pixi cache dir and reused. Clear them:

```sh
pixi clean cache --exec
```

Use `pixi exec` for one-off tools (formatters on a foreign repo, `uv pip compile` during a
migration, a quick interpreter of a specific version). If you find yourself running the same
`pixi exec` daily, it belongs in `pixi global` (see [pixi-global-tools.md](pixi-global-tools.md)).

---

## 2. PEP 723 scripts

Create a script with an inline metadata block:

```sh
pixi init --script hello.py
cat hello.py
```

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

Add dependencies with the normal `pixi add`, pointing at the script:

```sh
pixi add --script hello.py rich
cat hello.py
```

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
#
# [tool.pixi.dependencies]
# rich = "*"
# ///
```

Note where it went: `rich` was added as a **conda** dependency under
`[tool.pixi.dependencies]`, consistent with conda-forge-first. Use `--pypi` to put it in the
standard PEP 723 `dependencies = [...]` list instead (useful if the script must also run under
`uv run` or `pipx run` elsewhere).

Append some code and run it:

```sh
cat >> hello.py <<'PY'
from rich import print
print("[bold green]hello from a pixi script[/bold green]")
PY
pixi run --script hello.py
```

`--script` (or `-s`) is required when there is no workspace in the current directory — a bare
`pixi run hello.py` looks for a `pixi.toml` and errors. Script arguments go after `--`, or
pixi tries to parse them as its own flags:

```sh
pixi run --script hello.py -- --flag value
```

### Shebang

Make the script directly executable:

```sh
sed -i '' '1i\
#!/usr/bin/env -S pixi run --script
' hello.py
chmod +x hello.py
./hello.py
./hello.py -- --flag value      # same `--` rule applies
```

### Lock and pre-install

```sh
pixi lock --script hello.py            # writes hello.py.pixi.lock next to the script
pixi install --script hello.py         # resolve and build the env without running
```

Once `hello.py.pixi.lock` exists, `pixi run --script` keeps it updated; without one pixi uses
its cached resolution. Commit the lock alongside the script when reproducibility matters.

### Where do the environments live?

Script environments are content-addressed in the cache, not in `.pixi/`. They are shared
between scripts with identical metadata and cleaned with `pixi clean cache`.

---

## 3. Non-Python scripts (experimental)

`pixi init --script tool.sh` (or `.R`, `.jl`, ...) writes a `/// conda-script` block instead
of PEP 723. Running requires `pixi run --experimental --script tool.sh`, or setting
`experimental.conda-script = true` in config (prints a warning per run). Treat as unstable; it
is not used elsewhere in this primer.

---

## 4. Cleanup

```sh
cd ../.. && rm -rf sandbox/scripts-lab
pixi clean cache --exec
```

---

## Key takeaways

- `pixi exec` = `uvx`/`npx`; `pixi run --script` = `uv run script.py`. Neither creates a `.venv`.
- `pixi add --script file.py <pkg>` edits the inline block for you; conda-forge is the default target.
- `--script` is mandatory when running a script outside a workspace.
- These are for throwaway or single-file work. Anything with tests, CI, or a second file gets a workspace.
