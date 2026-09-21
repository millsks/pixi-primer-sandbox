"""Package built into a .conda artifact by the build lab."""


def hello() -> str:
    """Return a greeting proving the built package is importable."""
    return "hello from build_lab"
