import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pytraceability.cli import main, OutputFormats

common_output = [
    "KEY-1",
    "KEY-2",
]

json_output = [
    '{{"file_path":"{base_dir}/file1.py","function_name":"foo","line_number":5,"end_line_number":6,"source_code":"def foo():\\n    pass","key":"KEY-1","metadata":{{}},"is_complete":true,"history":null}}',
    '{{"file_path":"{base_dir}/file2.py","function_name":"foo","line_number":5,"end_line_number":6,"source_code":"def foo():\\n    pass","key":"KEY-2","metadata":{{}},"is_complete":true,"history":null}}',
]


@pytest.mark.parametrize(
    "isatty, output_format, expected_output",
    [
        (
            True,
            OutputFormats.KEY_ONLY,
            [
                "Extracting traceability from {base_dir}",
                "Using project root: {base_dir}",
                *common_output,
            ],
        ),
        (False, OutputFormats.KEY_ONLY, common_output),
        (False, OutputFormats.JSON, json_output),
    ],
)
def test_cli(isatty, output_format, expected_output):
    base_dir = Path(__file__).parent / "examples/separate_directory"
    argv = [
        f"--base-directory={base_dir}",
        "--decorator-name=traceability",
        f"--output-format={output_format}",
    ]
    runner = CliRunner()
    with patch("click.get_text_stream") as mock_get_text_stream:
        mock_get_text_stream.return_value.isatty.return_value = isatty
        result = runner.invoke(main, argv)

    assert result.exit_code == 0, result.stderr
    assert result.output.strip().split(os.linesep) == [
        line.format(base_dir=base_dir) for line in expected_output
    ]
