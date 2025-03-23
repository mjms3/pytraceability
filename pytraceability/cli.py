import os
import sys
from enum import Enum
from pathlib import Path

from tap import Tap

from pytraceability.config import PyTraceabilityConfig
from pytraceability.discovery import collect_traceability_from_directory


class OutputFormats(str, Enum):
    FULL = "full"
    KEY_ONLY = "key-only"


class CliArgs(Tap):
    base_directory: Path = Path(os.getcwd())
    decorator_name: str = "traceability"
    exclude_patterns: list[str]
    output_format: OutputFormats = OutputFormats.FULL

    def configure(self) -> None:
        self.add_argument("--exclude_patterns", default=[])


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
        if args.output_format == OutputFormats.FULL:  # pragma: no cover
            # This is temporary and for debugging only
            print(result)
        elif args.output_format == OutputFormats.KEY_ONLY:
            for traceability in result.traceability_data:
                print(traceability.key)
        else:  # pragma: no cover
            raise ValueError(f"Unknown output format: {args.output_format}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
