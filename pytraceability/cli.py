from __future__ import annotations

import functools
import os
import sys
from datetime import datetime
from operator import attrgetter
from pathlib import Path

import click

from pytraceability.common import STANDARD_DECORATOR_NAME
from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    GitHistoryMode,
    OutputFormats,
)
from pytraceability.discovery import collect_output_data
from pytraceability.logging import setup_logging  # Import logging setup


def strip_kwargs(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Strip everything except the context object
        ctx = args[0] if args else kwargs.get("ctx")
        return f(ctx)

    return wrapper


@click.command()
@click.option("--base-directory", type=Path, default=Path(os.getcwd()))
@click.option("--decorator-name", type=str, default=STANDARD_DECORATOR_NAME)
@click.option(
    "--output-format",
    type=click.Choice([o.value for o in OutputFormats]),
    default=OutputFormats.KEY_ONLY,
)
@click.option(
    "--mode",
    type=click.Choice([o.value for o in PyTraceabilityMode]),
    default=PyTraceabilityMode.static_only,
)
@click.option("--python-root", type=Path, default=None)
@click.option(
    "--git-history-mode",
    type=click.Choice([o.value for o in GitHistoryMode]),
    default=GitHistoryMode.NONE,
)
@click.option(
    "--since",
    type=datetime.fromisoformat,
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

    for result in sorted(
        collect_output_data(config),
        key=attrgetter("key"),
    ):
        if config.output_format == OutputFormats.KEY_ONLY:
            click.echo(result.key)
        elif config.output_format == OutputFormats.JSON:
            click.echo(result.model_dump_json())
        else:  # pragma: no cover
            raise ValueError(f"Unknown output format: {config.output_format}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
