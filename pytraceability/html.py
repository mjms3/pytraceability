from typing import Generator
from html import escape

from pytraceability.data_definition import TraceabilitySummary


def render_traceability_summary_html(
    summary: TraceabilitySummary,
) -> Generator[str, None, None]:
    html = [
        '<table border="1" cellspacing="0" cellpadding="5">',
        """
        <thead>
            <tr>
                <th>Traceability Key</th>
                <th>Meta data</th>
                <th>File Path</th>
                <th>Function</th>
                <th>Line Range</th>
                <th>Contains Raw Code</th>
                <th>Source Code</th>
                <th>History (Commits)</th>
            </tr>
        </thead>
        <tbody>
    """,
    ]
    for report in summary.reports:
        line_range = (
            f"{report.line_number} to {report.end_line_number or report.line_number}"
        )
        contains_raw_code = "Yes" if report.contains_raw_source_code else "No"

        source_code_html = (
            f"<pre>{escape(report.source_code)}</pre>" if report.source_code else "None"
        )

        history_html = "<ul>"
        if report.history:
            for commit in report.history:
                history_html += f"<li>{escape(commit.commit)}</li>"
        else:
            history_html += "<li>No history</li>"
        history_html += "</ul>"

        html.append(f"""
            <tr>
                <td>{report.key}</td>
                <td>{escape(str(report.metadata))}</td>
                <td>{escape(str(report.file_path))}</td>
                <td>{escape(report.function_name)}</td>
                <td>{line_range}</td>
                <td>{contains_raw_code}</td>
                <td>{source_code_html}</td>
                <td>{history_html}</td>
            </tr>
        """)

    html.append("</tbody></table>")
    for r in html:
        yield r
