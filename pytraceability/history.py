import re

from pydriller import Repository

from pytraceability.config import PROJECT_NAME
from pytraceability.custom import pytraceability
from pytraceability.data_definition import ExtractionResult, TraceabilityGitHistory


@pytraceability(
    "PYTRACEABILITY-5",
    info=f"{PROJECT_NAME} can extract a history of the code decorated by a given key from git",
)
def get_line_based_history(
    extraction_result: ExtractionResult, config
) -> list[TraceabilityGitHistory]:
    function_name = extraction_result.function_name.split(".")[-1]
    function_regex = re.compile(rf"def\s+{function_name}\s*\(.*\):")
    history = []
    file_path_in_repo = str(extraction_result.file_path.relative_to(config.repo_root))
    for commit in Repository(
        str(config.repo_root), filepath=str(extraction_result.file_path)
    ).traverse_commits():
        for modified_file in commit.modified_files:
            if modified_file.filename == extraction_result.file_path.name:
                pass
            if (
                modified_file.old_path == file_path_in_repo
                or modified_file.new_path == file_path_in_repo
            ):
                if modified_file.diff and function_regex.search(modified_file.diff):
                    history.append(
                        TraceabilityGitHistory(
                            commit=commit.hash,
                            author_name=commit.author.name,
                            author_date=commit.author_date,
                            message=commit.msg.strip(),
                            diff=modified_file.diff,
                        )
                    )
    return history
