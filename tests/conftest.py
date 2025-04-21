from pathlib import Path
from textwrap import dedent

import pytest
from git import Repo


@pytest.fixture
def git_repo(tmp_path: Path) -> Repo:
    return Repo.init(tmp_path, initial_branch="main")


@pytest.fixture
def directory_with_two_files(git_repo: Repo, tmp_path: Path) -> Path:
    for idx in range(1, 3):
        file = tmp_path / f"file{idx}.py"
        file.write_text(
            dedent(f"""\
        @traceability("KEY-{idx}")
        def foo():
            pass
            """)
        )
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(
        dedent("""\
        [tool.pytraceability]
        decorator_name = "traceability"
        """)
    )
    return tmp_path
