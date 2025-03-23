import os
from pathlib import Path

from click.testing import CliRunner

from pytraceability.cli import main


def test_cli():
    base_dir = Path(__file__).parent / "examples/separate_directory"
    argv = [
        f"--base-directory={base_dir}",
        "--decorator-name=traceability",
        "--output-format=key-only",
    ]
    runner = CliRunner()
    result = runner.invoke(main, argv)

    assert result.exit_code == 0
    assert result.output.strip().split(os.linesep) == [
        f"Extracting traceability from {base_dir}",
        f"Using project root: {base_dir}",
        "KEY-1",
        "KEY-2",
    ]
