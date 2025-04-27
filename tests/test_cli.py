import os

import pytest
from click.testing import CliRunner

from pytraceability.cli import main, OutputFormats
from pytraceability.config import PyTraceabilityConfig, HistoryModeConfig

common_output = [
    "Extracting traceability from {base_dir}",
    "Using python root: {base_dir}",
]

json_output = [
    "{",
    '  "reports": [',
    "    {",
    '      "key": "KEY-1",',
    '      "metadata": {},',
    '      "file_path": "{base_dir}/file1.py",',
    '      "function_name": "foo",',
    '      "line_number": 2,',
    '      "end_line_number": 3,',
    '      "source_code": "def foo():\\n    pass",',
    '      "history": null,',
    '      "contains_raw_source_code": false',
    "    },",
    "    {",
    '      "key": "KEY-2",',
    '      "metadata": {},',
    '      "file_path": "{base_dir}/file2.py",',
    '      "function_name": "foo",',
    '      "line_number": 2,',
    '      "end_line_number": 3,',
    '      "source_code": "def foo():\\n    pass",',
    '      "history": null,',
    '      "contains_raw_source_code": false',
    "    }",
    "  ]",
    "}",
]


@pytest.mark.parametrize(
    "output_format, expected_output",
    [
        (
            OutputFormats.KEY_ONLY,
            [
                "KEY-1",
                "KEY-2",
            ],
        ),
        (OutputFormats.JSON, json_output),
    ],
)
def test_cli(output_format, expected_output, directory_with_two_files):
    base_dir = directory_with_two_files
    argv = [
        f"--base-directory={base_dir}",
        f"--output-format={output_format.value}",
    ]
    runner = CliRunner()

    result = runner.invoke(main, argv)

    assert result.exit_code == 0, result.output

    assert result.output.strip().split(os.linesep) == [
        line.format(base_dir=base_dir) if "base_dir" in line else line
        for line in expected_output
    ]


def test_all_config_options_can_be_set_with_cli():
    cli_args = {p.name for p in main.params}
    config_fields = (set(PyTraceabilityConfig.model_fields) - {"history_config"}) | set(
        HistoryModeConfig.model_fields
    )
    assert config_fields <= cli_args
