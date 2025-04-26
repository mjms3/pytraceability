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
from pytraceability.logging import setup_logging, get_display_logger


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
    "--commit-url-template",
    type=str,
    help="Template URL for commit links, e.g., 'http://github.com/projectname/{commit}'",
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
    _log = get_display_logger(__name__)
    config = PyTraceabilityConfig.from_command_line_arguments(ctx.params)

    _log.display(f"Extracting traceability from {config.base_directory}")
    _log.display(f"Using python root: {config.python_root}")

    for output_line in PyTraceabilityCollector(config).get_printable_output():
        click.echo(output_line)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
