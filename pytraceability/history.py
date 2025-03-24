import ast
from pathlib import Path

from pydriller import Repository

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.config import PROJECT_NAME, PyTraceabilityConfig
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    TraceabilityGitHistory,
    TraceabilityReport,
    ExtractionResultsList,
)


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
            if modified_file.source_code is None or modified_file.new_path is None:
                continue
            tree = ast.parse(modified_file.source_code, filename=modified_file.new_path)
            extraction_results = TraceabilityVisitor(
                config,
                file_path=Path(modified_file.new_path),
                source_code=modified_file.source_code,
            ).visit(tree)
            for traceability_report in ExtractionResultsList(
                extraction_results
            ).flatten():
                if traceability_report.key not in history:
                    history[traceability_report.key] = []
                history[traceability_report.key].append(
                    TraceabilityGitHistory(
                        commit=commit.hash,
                        author_name=commit.author.name,
                        author_date=commit.author_date,
                        message=commit.msg.strip(),
                        source_code=traceability_report.source_code,
                    )
                )

    return history
