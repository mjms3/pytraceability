import re

from pydriller import Repository

from pytraceability.config import PROJECT_NAME, PyTraceabilityConfig
from pytraceability.custom import pytraceability
from pytraceability.data_definition import TraceabilityGitHistory, TraceabilityReport


@pytraceability(
    "PYTRACEABILITY-5",
    info=f"{PROJECT_NAME} can extract a history of the code decorated by a given key from git",
)
def get_line_based_history(
    traceability_reports: list[TraceabilityReport], config: PyTraceabilityConfig
) -> dict[str, list[TraceabilityGitHistory]]:
    current_file_for_key: dict[str, str] = {}

    for traceability_report in traceability_reports:
        if traceability_report.key in current_file_for_key:
            # TODO: Add a test for when the key is duplicated / enforce this more widely
            raise ValueError(f"Key {traceability_report.key} is duplicated")
        current_file_for_key[traceability_report.key] = str(
            traceability_report.file_path.relative_to(config.repo_root)
        )

    history: dict[str, list[TraceabilityGitHistory]] = {}
    for commit in Repository(str(config.repo_root), order="reverse").traverse_commits():
        files_of_interest = set(current_file_for_key.values())
        relevant_files = {
            f for f in commit.modified_files if f.new_path in files_of_interest
        }
        for modified_file in relevant_files:
            if (
                modified_file.diff
            ):  # TODO: Add a test for modified_file.diff being none.
                for traceability_key in current_file_for_key:
                    decorator_regex = (
                        f"@{config.decorator_name}\(\s*['\"]{traceability_key}"
                    )
                    if re.search(decorator_regex, modified_file.diff):
                        if traceability_key not in history:
                            history[traceability_key] = []
                        history[traceability_key].append(
                            TraceabilityGitHistory(
                                commit=commit.hash,
                                author_name=commit.author.name,
                                author_date=commit.author_date,
                                message=commit.msg.strip(),
                                diff=modified_file.diff,
                            )
                        )

    return history
