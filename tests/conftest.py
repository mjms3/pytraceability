from pathlib import Path
from textwrap import dedent

import pytest
from git import Repo


@pytest.fixture
def git_repo(tmp_path: Path) -> Repo:
    return Repo.init(tmp_path, initial_branch="main")


@pytest.fixture()
def pyproject_file(tmp_path: Path) -> Path:
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(
        dedent("""\
        [tool.pytraceability]
        decorator_name = "traceability"
        """)
    )
    return pyproject_file


def write_traceability_file(file_path: Path, idx: int):
    file_path.write_text(
        dedent(f"""\
        @traceability("KEY-{idx}")
        def foo():
            pass
            """)
    )


@pytest.fixture
def directory_with_two_files(
    git_repo: Repo, tmp_path: Path, pyproject_file: Path
) -> Path:
    for idx in range(1, 3):
        file_path = tmp_path / f"file{idx}.py"
        write_traceability_file(file_path, idx)
        git_repo.index.add([str(file_path)])
    git_repo.index.commit("initial commit")
    return tmp_path


@pytest.fixture
def directory_with_duplicate_keys(
    git_repo: Repo, tmp_path: Path, pyproject_file: Path
) -> Path:
    write_traceability_file(tmp_path / "file1.py", 1)
    write_traceability_file(tmp_path / "file2.py", 1)
    return tmp_path
