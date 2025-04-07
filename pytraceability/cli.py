import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

import click

from pytraceability.common import STANDARD_DECORATOR_NAME
from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    get_repo_root,
    GitHistoryMode,
)
from pytraceability.discovery import collect_output_data


class OutputFormats(str, Enum):
    KEY_ONLY = "key-only"
    JSON = "json"


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
@click.option(
    "--git-history-mode",
    type=click.Choice([o.value for o in GitHistoryMode]),
    default=GitHistoryMode.NONE,
)
@click.option(
    "--since",
    type=datetime.fromisoformat,
)
def main(
    base_directory: Path,
    decorator_name: str,
    output_format: OutputFormats,
    mode: PyTraceabilityMode,
    git_history_mode: GitHistoryMode,
    since: datetime,
):
    if click.get_text_stream("stdout").isatty():
        click.echo(f"Extracting traceability from {base_directory}")
        click.echo(f"Using project root: {base_directory}")

    config = PyTraceabilityConfig(
        repo_root=get_repo_root(base_directory),
        decorator_name=decorator_name,
        mode=mode,
        git_history_mode=git_history_mode,
        since=since,
    )

    for result in collect_output_data(
        base_directory,
        base_directory,
        config,
    ):
        if output_format == OutputFormats.KEY_ONLY:
            click.echo(result.key)
        elif output_format == OutputFormats.JSON:
            click.echo(result.model_dump_json())
        else:  # pragma: no cover
            raise ValueError(f"Unknown output format: {output_format}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
