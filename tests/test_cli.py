import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pytraceability.cli import main, OutputFormats
from pytraceability.config import PyTraceabilityConfig

common_output = [
    "KEY-1",
    "KEY-2",
]

json_output = [
    '{{"file_path":"{base_dir}/file1.py","function_name":"foo","line_number":2,"end_line_number":3,"source_code":"def foo():\\n    pass","key":"KEY-1","metadata":{{}},"history":null,"is_complete":true}}',
    '{{"file_path":"{base_dir}/file2.py","function_name":"foo","line_number":2,"end_line_number":3,"source_code":"def foo():\\n    pass","key":"KEY-2","metadata":{{}},"history":null,"is_complete":true}}',
]


@pytest.mark.parametrize(
    "isatty, output_format, expected_output",
    [
        (
            True,
            OutputFormats.KEY_ONLY,
            [
                "Extracting traceability from {base_dir}",
                "Using python root: {base_dir}",
                *common_output,
            ],
        ),
        (False, OutputFormats.KEY_ONLY, common_output),
        (False, OutputFormats.JSON, json_output),
    ],
)
def test_cli(isatty, output_format, expected_output, directory_with_two_files):
    base_dir = directory_with_two_files
    argv = [
        f"--base-directory={base_dir}",
        f"--output-format={output_format.value}",
    ]
    runner = CliRunner()
    with patch("click.get_text_stream") as mock_get_text_stream:
        mock_get_text_stream.return_value.isatty.return_value = isatty
        result = runner.invoke(main, argv)

    assert result.exit_code == 0, result.output
    assert result.output.strip().split(os.linesep) == [
        line.format(base_dir=base_dir) for line in expected_output
    ]


def test_all_config_options_can_be_set_with_cli():
    cli_args = {p.name for p in main.params}
    config_fields = set(PyTraceabilityConfig.model_fields)
    assert config_fields <= cli_args
