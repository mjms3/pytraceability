import os
import sys
from pathlib import Path

from tap import Tap

from pytraceability.data_definition import PyTraceabilityConfig
from pytraceability.discovery import collect_traceability_from_directory


class CliArgs(Tap):
    base_directory: Path = Path(os.getcwd()).parent  # TODO - undo this change
    decorator_name: str = "pytraceability"  # TODO - undo this change
    exclude_patterns: list[str]

    def configure(self) -> None:
        self.add_argument("--exclude-patterns", default=["*test*"])


def main(argv: list[str]) -> int:
    args = CliArgs().parse_args(argv)
    print(f"Extracting traceability from {args.base_directory}")
    print(f"Using project root: {args.base_directory}")

    config = PyTraceabilityConfig(
        exclude_patterns=args.exclude_patterns,
        decorator_name=args.decorator_name,
    )
    for result in collect_traceability_from_directory(
        args.base_directory,
        args.base_directory,
        config,
    ):
        print(result)
    return 0


if __name__ == "__main__":
    result = main(sys.argv[1:])
    sys.exit(result)
