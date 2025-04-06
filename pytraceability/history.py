import ast
from pathlib import Path
from typing import Dict

from pydriller import Repository, ModifiedFile
from typing_extensions import Self

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.config import PROJECT_NAME, PyTraceabilityConfig
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    TraceabilityGitHistory,
    TraceabilityReport,
    ExtractionResultsList,
)


class CurrentFileForKey(Dict[str, str | None]):
    @classmethod
    def from_traceability_reports(
        cls,
        traceability_reports: list[TraceabilityReport],
        config: PyTraceabilityConfig,
    ) -> Self:
        current_file_for_key = cls()

        for traceability_report in traceability_reports:
            if traceability_report.key in current_file_for_key:
                # TODO: Add a test for when the key is duplicated / enforce this more widely
                raise ValueError(f"Key {traceability_report.key} is duplicated")
            current_file_for_key[traceability_report.key] = str(
                traceability_report.file_path.relative_to(config.repo_root)
            )
        return current_file_for_key

    def reset_keys_for_relevant_files(self, relevant_files: list[ModifiedFile]):
        relevant_paths = {f.new_path for f in relevant_files}
        for k, v in self.items():
            if v in relevant_paths:
                self[k] = None


@pytraceability(
    "PYTRACEABILITY-5",
    info=f"{PROJECT_NAME} can extract a history of the code decorated by a given key from git",
)
def get_line_based_history(
    traceability_reports: list[TraceabilityReport], config: PyTraceabilityConfig
) -> dict[str, list[TraceabilityGitHistory]]:
    current_file_for_key = CurrentFileForKey.from_traceability_reports(
        traceability_reports, config
    )

    history: dict[str, list[TraceabilityGitHistory]] = {}
    for commit in Repository(str(config.repo_root), order="reverse").traverse_commits():
        relevant_files = list(
            {
                f
                for f in commit.modified_files
                if f.new_path in current_file_for_key.values()
            }
        )
        other_files = list(
            {
                f
                for f in commit.modified_files
                if f.new_path not in current_file_for_key.values()
            }
        )
        current_file_for_key.reset_keys_for_relevant_files(relevant_files + other_files)
        for modified_file in relevant_files + other_files:
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
                current_file_for_key[traceability_report.key] = modified_file.new_path

            if all(current_file_for_key.values()):
                break
        else:
            raise ValueError(
                f"Some traceabbility keys not found: {current_file_for_key}"
            )

    return history
