---
type: Tutorial
title: Pixi Tasks
description: Define, chain, parameterise, and cache tasks with pixi task add and the [tasks] table — depends-on, args with defaults, cwd, env, clean-env, inputs/outputs caching, aliases, hidden tasks, and the standard task set for Python projects.
tags: [pixi, tasks, task-runner, deno-task-shell, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-task-add-help
    resource: cli:pixi/0.81.0/task add --help
    title: pixi task add --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-run-help
    resource: cli:pixi/0.81.0/run --help
    title: pixi run --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-advanced-tasks
    resource: https://pixi.prefix.dev/latest/workspace/advanced_tasks/
    title: pixi — advanced tasks
---

# Pixi Tasks

Verified against `pixi 0.81.0`. Tasks replace Makefiles, `tox.ini`, `justfile`, and ad-hoc
shell scripts. They run inside the environment, through `deno_task_shell`, so the same task
line works on Linux, macOS, and Windows.

## Setup

```sh
mkdir -p sandbox && cd sandbox
pixi init tasks-lab && cd tasks-lab
pixi add "python=3.14.*"
```

---

## 1. Add and run a task

```sh
pixi task add hello 'echo hello from pixi'
pixi run hello
pixi task list
```

`pixi task add` writes to `[tasks]`. The simple string form is used when there are no options:

```toml
[tasks]
hello = "echo hello from pixi"
```

Add `--description` so `pixi task list` is self-documenting. `pixi task add` refuses to
overwrite an existing name, so remove first:

```sh
pixi task remove hello
pixi task add hello 'echo hello from pixi' --description "Smoke test"
pixi task list
```

`pixi run` also accepts arbitrary commands — anything on the environment's `PATH`:

```sh
pixi run python --version
pixi run -x python --version   # -x: treat as executable even if a task has the same name
pixi run -n hello              # dry run: print the resolved command, execute nothing
```

---

## 2. Chaining with `depends-on`

```sh
pixi task add fmt  'echo formatting'
pixi task add lint 'echo linting'
pixi task add test 'echo testing'
pixi task add ci   'echo ci passed' --depends-on fmt --depends-on lint --depends-on test
pixi run ci
```

Dependencies run in order, each once, before the task's own `cmd`. A task with only
`depends-on` and no `cmd` is a pure aggregator — the standard pattern for `ci`:

```toml
[tasks]
ci = { depends-on = ["fmt", "lint", "check", "cov"] }
```

Skip the chain when iterating: `pixi run --skip-deps ci`.

---

## 3. Arguments

`--arg` on the CLI writes a required positional argument:

```sh
pixi task add shout 'echo {{ word }}' --arg word
pixi run shout hey
```

Defaults need the table form — edit `pixi.toml`:

```toml
[tasks]
greet = { cmd = "echo Hello {{ name }}", args = [{ arg = "name", default = "world" }] }
```

```sh
pixi run greet          # Hello world
pixi run greet Kevin    # Hello Kevin
```

Templates use MiniJinja, so filters and conditionals work: `{{ name | upper }}`,
`{% if pixi.is_win %}...{% endif %}`. Built-in variables: `pixi.platform`,
`pixi.environment.name`, `pixi.manifest_path`, `pixi.version`, `pixi.is_win/unix/linux/osx`.

Pass extra, un-templated arguments after `--`:

```toml
[tasks]
test = { cmd = "pytest {{ target }} -v", args = [{ arg = "target", default = "tests/unit" }] }
```

```sh
pixi run test tests/integration -- --tb=short --maxfail=1
```

Dependencies can pass arguments too:

```toml
[tasks]
test-all = { depends-on = [{ task = "test", args = ["tests/unit"] }, { task = "test", args = ["tests/integration"] }] }
```

---

## 4. `cwd`, `env`, `clean-env`

```sh
mkdir -p scripts && printf 'import os\nprint("cwd:", os.getcwd())\nprint("MODE:", os.environ.get("MODE"))\n' > scripts/where.py
pixi task add where 'python where.py' --cwd scripts --env MODE=dev
pixi run where
```

```toml
[tasks]
where = { cmd = "python where.py", cwd = "scripts", env = { MODE = "dev" } }
```

`--clean-env` (or `clean-env = true`) strips the parent shell's environment so the task sees
only what pixi provides plus a minimal set (`HOME`, `USER`, `TMPDIR`, ...). Use it for
reproducibility checks:

```sh
export LEAK=oops
pixi run 'echo LEAK=$LEAK'                  # LEAK=oops
pixi run --clean-env 'echo LEAK=$LEAK'      # LEAK=
```

---

## 5. Caching with `inputs` / `outputs`

Pixi skips a task when its inputs, outputs, command, and environment are unchanged since the
last successful run. Edit `pixi.toml`:

```toml
[tasks]
gen = { cmd = "python -c \"open('out.txt','w').write(open('in.txt').read().upper())\"", inputs = ["in.txt"], outputs = ["out.txt"] }
```

```sh
echo hello > in.txt
pixi run gen          # runs
pixi run gen          # cached, skipped
echo again > in.txt
pixi run gen          # runs again
```

Globs are allowed (`src/**/*.py`). Cache state lives under `.pixi/`; `pixi clean` resets it.

---

## 6. Aliases, hidden tasks, per-environment defaults

```sh
pixi task alias t test            # t = [{ task = "test" }]
```

Tasks whose name starts with `_` are hidden from `pixi task list` but still runnable — use
them for internal helpers.

A task can declare which environment it runs in when `-e` is not given:

```toml
[tasks]
cov = { cmd = "pytest --cov", default-environment = "test" }
```

And features can carry their own tasks, available only in environments that include them:

```sh
pixi task add -f docs serve 'mkdocs serve'
```

---

## 7. Platform-specific tasks

```toml
[tasks]
open = "open ."

[target.win-64.tasks]
open = "start ."
```

Via CLI, add the platform-specific variants **before** the default one — `pixi task add`
refuses to add a name that already exists at the default level — and use concrete subdirs
(`win-64`, not the `win` family; families are hand-edit only):

```sh
pixi task add --platform win-64 open 'start .'
pixi task add open 'open .'
```

The most specific target wins.

---

## 8. Multi-line tasks and the shell

`deno_task_shell` supports `&&`, `||`, `;`, pipes, redirects, `$VAR`, `$(cmd)`, globs, and
cross-platform builtins (`cp`, `mv`, `rm`, `mkdir`, `cat`, `echo`, `sleep`). Multi-line:

```toml
[tasks]
release = """
set -e
python -m build
ls dist/
"""
```

Do not rely on bash-isms (`[[ ]]`, arrays, `source`). If you need them, put the logic in a
script and call the script from the task.

---

## 9. The standard task set (Python projects)

```toml
[tasks]
bootstrap = "pre-commit install"
fmt = "ruff format ."
lint = "ruff check ."
check = "mypy src/"
test = "pytest tests/unit/"
test-integration = "pytest tests/integration/"
cov = "pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90"
build = "python -m build"
changelog = "git cliff -o CHANGELOG.md"
ci = { depends-on = ["fmt", "build", "check", "lint", "cov"] }
```

Add them with `pixi task add` one at a time, or paste the block and run `pixi task list` to
confirm it parsed.

---

## 10. Cleanup

```sh
cd .. && rm -rf tasks-lab
```

---

## Key takeaways

- One task = one manifest entry; `depends-on` composes them. `ci` is an aggregator with no `cmd`.
- `args` + `{{ }}` templating replaces most shell-script argument parsing.
- `inputs`/`outputs` give you Make-style incremental builds for free.
- `--clean-env` and `-n` are the two debugging flags to remember.
