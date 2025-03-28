import os
import sys
from enum import Enum
from pathlib import Path

import click

from pytraceability.common import STANDARD_DECORATOR_NAME
from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    get_repo_root,
)
from pytraceability.discovery import collect_traceability_from_directory


class OutputFormats(str, Enum):
    FULL = "full"
    KEY_ONLY = "key-only"


@click.command()
@click.option("--base-directory", type=Path, default=Path(os.getcwd()))
@click.option("--decorator-name", type=str, default=STANDARD_DECORATOR_NAME)
@click.option(
    "--output-format",
    type=click.Choice([o.value for o in OutputFormats]),
    default=OutputFormats.FULL,
)
@click.option(
    "--mode",
    type=click.Choice([o.value for o in PyTraceabilityMode]),
    default=PyTraceabilityMode.static_only,
)
def main(
    base_directory: Path,
    decorator_name: str,
    output_format: OutputFormats,
    mode: PyTraceabilityMode,
):
    click.echo(f"Extracting traceability from {base_directory}")
    click.echo(f"Using project root: {base_directory}")

    config = PyTraceabilityConfig(
        repo_root=get_repo_root(base_directory),
        decorator_name=decorator_name,
        mode=mode,
    )
    for result in collect_traceability_from_directory(
        base_directory,
        base_directory,
        config,
    ):
        if output_format == OutputFormats.FULL:  # pragma: no cover
            # This is temporary and for debugging only
            click.echo(result)
        elif output_format == OutputFormats.KEY_ONLY:
            click.echo(result.key)
        else:  # pragma: no cover
            raise ValueError(f"Unknown output format: {output_format}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
