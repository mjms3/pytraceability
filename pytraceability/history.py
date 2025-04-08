import ast
import logging
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

_log = logging.getLogger(__name__)


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
        # TODO - handle timezones correctly
        if (
            config.since is not None
            and commit.committer_date.timestamp() < config.since.timestamp()
        ):
            _log.info(
                "Ending processing as committer date %s is older than %s",
                commit.committer_date,
                config.since,
            )
            break
        current_file_set = set(current_file_for_key.values())
        relevant_files_first = sorted(
            commit.modified_files,
            key=lambda f: f.new_path in current_file_set,
        )

        current_file_for_key.reset_keys_for_relevant_files(relevant_files_first)
        for modified_file in relevant_files_first:
            if (
                modified_file.source_code is None
                or modified_file.new_path is None
                or not modified_file.new_path.endswith("py")
            ):
                continue
            _log.debug("Processing file %s", modified_file.new_path)
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
                _log.info("All traceability decorators located for commit")
                break
    return history
