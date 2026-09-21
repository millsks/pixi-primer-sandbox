# envs-lab

Lab for [Features and Environments](../../docs/pixi-features-environments.md).

```sh
cp -r labs/envs-lab sandbox/ && cd sandbox/envs-lab
pixi init .
```

Files:

- `tests/test_smoke.py` — a test that reports which interpreter ran it, so `pixi run -e <env> pytest` shows the matrix working
