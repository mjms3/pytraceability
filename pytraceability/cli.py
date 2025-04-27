from __future__ import annotations

import functools
import sys

import click
import cloup
from cloup.constraints import If, accept_none, IsSet

from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    OutputFormats,
    HistoryModeConfig,
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


@cloup.command()
@cloup.option_group(
    "Core options",
    cloup.option(
        "--pyproject-file",
        type=cloup.file_path(exists=True, readable=True, resolve_path=True),
        help="Path to a pyproject.toml file to load configuration from.",
    ),
    cloup.option(
        "--base-directory",
        type=cloup.dir_path(exists=True, readable=True, resolve_path=True),
    ),
    cloup.option(
        "--python-root",
        type=cloup.dir_path(exists=True, readable=True, resolve_path=True),
    ),
    cloup.option(
        "--decorator-name",
        type=str,
        help=f"Default value: {PyTraceabilityConfig.model_fields['decorator_name'].default}",
    ),
    cloup.option(
        "--output-format",
        type=click.Choice([o.value for o in OutputFormats]),
        help=f"Default value: {PyTraceabilityConfig.model_fields['output_format'].default}",
    ),
    cloup.option(
        "--mode",
        type=click.Choice([o.value for o in PyTraceabilityMode]),
        help=f"Default value: {PyTraceabilityConfig.model_fields['mode'].default}",
    ),
    cloup.option(
        "--exclude-pattern",
        "exclude_patterns",
        type=str,
        multiple=True,
    ),
    cloup.option(
        "--history/--no-history",
        default=False,
    ),
)
@cloup.option_group(
    "History options",
    cloup.option(
        "--git-branch",
        type=str,
        help=f"Default value: {HistoryModeConfig.model_fields['git_branch'].default}",
    ),
    cloup.option(
        "--commit-url-template",
        type=str,
        help="Template URL for commit links, e.g., 'http://github.com/projectname/{commit}'",
    ),
    constraint=If(~IsSet("history"), then=accept_none),
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

    for output_line in PyTraceabilityCollector(config).get_printable_output():
        click.echo(output_line)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
