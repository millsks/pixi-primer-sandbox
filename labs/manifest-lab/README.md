# manifest-lab

Companion to [pixi.toml Manifest Reference](../../docs/pixi-manifest-reference.md). The
`pixi.toml` here uses every table the reference describes, in one solvable manifest.

```sh
cp -r labs/manifest-lab sandbox/ && cd sandbox/manifest-lab
pixi lock --dry-run          # parses and solves without writing
pixi info                    # environments, features, channels
pixi task list
pixi run -e test test
```

Edit it while reading the reference; `pixi lock --dry-run` tells you immediately whether a
change still parses and solves.
