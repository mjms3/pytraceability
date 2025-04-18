from __future__ import annotations

import functools
import os
import sys
from datetime import datetime
from enum import Enum
from operator import attrgetter
from pathlib import Path
from types import SimpleNamespace

import click

from pytraceability.common import STANDARD_DECORATOR_NAME
from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    get_repo_root,
    GitHistoryMode,
    find_pyproject_file,
)
from pytraceability.discovery import collect_output_data
from pytraceability.logging import setup_logging  # Import logging setup


class OutputFormats(str, Enum):
    KEY_ONLY = "key-only"
    JSON = "json"


def strip_kwargs(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Strip everything except the context object
        ctx = args[0] if args else kwargs.get("ctx")
        return f(ctx)

    return wrapper


@click.command()
@click.option("--base-directory", type=Path, default=Path(os.getcwd()))
@click.option("--repo-root", type=Path, default=Path(os.getcwd()))
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
    params = SimpleNamespace(**ctx.params)
    setup_logging(params.verbosity)

    if click.get_text_stream("stdout").isatty():
        click.echo(f"Extracting traceability from {params.base_directory}")
        click.echo(f"Using project root: {params.base_directory}")

    pyproject_file_to_use = params.pyproject_file or find_pyproject_file(
        params.base_directory
    )

    if pyproject_file_to_use:
        config = PyTraceabilityConfig.from_pyproject_toml(pyproject_file_to_use)
    else:
        config = PyTraceabilityConfig(repo_root=get_repo_root(params.base_directory))
    config.decorator_name = params.decorator_name
    config.mode = params.mode
    config.git_history_mode = params.git_history_mode
    config.since = params.since
    config.repo_root = params.repo_root
    config.exclude_patterns = params.exclude_patterns

    for result in sorted(
        collect_output_data(
            params.base_directory,
            params.base_directory,
            config,
        ),
        key=attrgetter("key"),
    ):
        if params.output_format == OutputFormats.KEY_ONLY:
            click.echo(result.key)
        elif params.output_format == OutputFormats.JSON:
            click.echo(result.model_dump_json())
        else:  # pragma: no cover
            raise ValueError(f"Unknown output format: {params.output_format}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
