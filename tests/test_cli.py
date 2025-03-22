import os
from pathlib import Path

from pytraceability.cli import main


def test_cli(capsys):
    base_dir = Path(__file__).parent / "examples/separate_directory"
    argv = [
        f"--base_directory={base_dir}",
        "--decorator_name=traceability",
        "--output_format=key-only",
    ]
    main(argv)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert [line for line in captured.out.split(os.linesep) if line] == [
        f"Extracting traceability from {base_dir}",
        f"Using project root: {base_dir}",
        "A key",
    ]
