# ci-lab

Files for [Pixi in CI with GitHub Actions](../../docs/pixi-ci-github-actions.md). This lab
is not run locally end to end — the workflow needs a GitHub repository and the Dockerfile
needs a container runtime. Copy the pieces into a real project:

```sh
cp -r labs/ci-lab sandbox/ && cd sandbox/ci-lab
pixi init .
pixi add "python=3.14.*"
pixi task add ci 'echo placeholder gate'     # replace with the real depends-on chain
```

Files:

- `.github/workflows/ci.yml` — two-tier workflow (fast `unit` job, `full` gate) over a matrix of pixi environments, plus a standalone `lock` drift check
- `Dockerfile` — multi-stage image: install with pixi, ship only the environment, activate with `pixi shell-hook`

Both assume the workspace defines `py312` / `py313` / `py314` environments (see the
[Features and Environments](../../docs/pixi-features-environments.md) guide, §4) and a `prod`
environment for the container.
