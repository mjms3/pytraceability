from __future__ import annotations

import functools
import sys
from pathlib import Path

import click

from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    GitHistoryMode,
    OutputFormats,
)
from pytraceability.collector import PyTraceabilityCollector
from pytraceability.logging import setup_logging


def strip_kwargs(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Strip everything except the context object
        ctx = args[0] if args else kwargs.get("ctx")
        return f(ctx)

    return wrapper


@click.command()
@click.option("--base-directory", type=Path, default=None)
@click.option("--decorator-name", type=str)
@click.option(
    "--output-format",
    type=click.Choice([o.value for o in OutputFormats]),
)
@click.option(
    "--mode",
    type=click.Choice([o.value for o in PyTraceabilityMode]),
)
@click.option("--python-root", type=Path, default=None)
@click.option(
    "--git-history-mode",
    type=click.Choice([o.value for o in GitHistoryMode]),
)
@click.option(
    "--pyproject-file",
    type=Path,
    help="Path to a pyproject.toml file to load configuration from.",
)
@click.option(
    "--exclude-pattern",
    "exclude_patterns",
    type=str,
    multiple=True,
)
@click.option(
    "--git-branch",
    type=str,
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Set verbosity level. Use -v for INFO, -vv for DEBUG",
)
@click.version_option()
@click.pass_context
@strip_kwargs
def main(ctx):
    setup_logging(ctx.params["verbosity"])
    config = PyTraceabilityConfig.from_command_line_arguments(ctx.params)

    if click.get_text_stream("stdout").isatty():
        click.echo(f"Extracting traceability from {config.base_directory}")
        click.echo(f"Using python root: {config.python_root}")

    for output_line in PyTraceabilityCollector(config).get_printable_output():
        click.echo(output_line)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
