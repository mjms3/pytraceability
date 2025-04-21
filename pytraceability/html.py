from typing import Generator
from html import escape
from jinja2 import Template

from pytraceability.data_definition import TraceabilitySummary

HTML_TEMPLATE = """
<table border="1" cellspacing="0" cellpadding="5">
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
        {% for report in reports %}
        <tr>
            <td>{{ report.key }}</td>
            <td>{{ report.metadata | escape }}</td>
            <td>{{ report.file_path | escape }}</td>
            <td>{{ report.function_name | escape }}</td>
            <td>{{ report.line_range }}</td>
            <td>{{ "Yes" if report.contains_raw_source_code else "No" }}</td>
            <td>
                {% if report.source_code %}
                <pre>{{ report.source_code | escape }}</pre>
                {% else %}
                None
                {% endif %}
            </td>
            <td>
                <ul>
                    {% if report.history %}
                        {% for commit in report.history %}
                        <li>{{ commit.commit | escape }}</li>
                        {% endfor %}
                    {% else %}
                        <li>No history</li>
                    {% endif %}
                </ul>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
"""


def render_traceability_summary_html(
    summary: TraceabilitySummary,
) -> Generator[str, None, None]:
    template = Template(HTML_TEMPLATE)
    reports = [
        {
            "key": report.key,
            "metadata": str(report.metadata),
            "file_path": str(report.file_path),
            "function_name": report.function_name,
            "line_range": f"{report.line_number} to {report.end_line_number or report.line_number}",
            "contains_raw_source_code": report.contains_raw_source_code,
            "source_code": report.source_code,
            "history": report.history,
        }
        for report in summary.reports
    ]

    rendered_html = template.render(reports=reports, escape=escape)
    for line in rendered_html.splitlines():
        yield line
