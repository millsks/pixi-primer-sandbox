"""Report the working directory and MODE variable a pixi task ran with."""

import os

import structlog

log = structlog.get_logger()
log.info("task_context", cwd=os.getcwd(), mode=os.environ.get("MODE"))
