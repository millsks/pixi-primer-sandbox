# Multi-stage: solve and install with pixi, ship only the environment.
FROM ghcr.io/prefix-dev/pixi:0.81.0 AS build
WORKDIR /app
COPY pixi.toml pixi.lock ./
RUN pixi install --locked -e prod
COPY . .
RUN pixi shell-hook -e prod -s bash > /shell-hook.sh \
 && echo 'exec "$@"' >> /shell-hook.sh

FROM ubuntu:24.04 AS runtime
WORKDIR /app
COPY --from=build /app/.pixi/envs/prod /app/.pixi/envs/prod
COPY --from=build /shell-hook.sh /shell-hook.sh
COPY --from=build /app/src /app/src
ENTRYPOINT ["/bin/bash", "/shell-hook.sh"]
CMD ["python", "-m", "myapp"]
