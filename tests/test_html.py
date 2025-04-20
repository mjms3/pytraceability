from pytraceability.collector import PyTraceabilityCollector
from pytraceability.config import PyTraceabilityConfig, OutputFormats


def test_html(directory_with_two_files):
    config = PyTraceabilityConfig(
        base_directory=directory_with_two_files, output_format=OutputFormats.HTML
    )
    html_report = []
    for segment in PyTraceabilityCollector(config).get_printable_output():
        html_report.extend(
            [line.strip() for line in segment.splitlines() if line.strip()]
        )

    assert html_report == [
        line.strip()
        for line in f"""\
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
               <tr>
                   <td>KEY-1</td>
                   <td>{{}}</td>
                   <td>{directory_with_two_files}/file1.py</td>
                   <td>foo</td>
                   <td>2 to 3</td>
                   <td>No</td>
                   <td><pre>def foo():
       pass</pre></td>
                   <td><ul><li>No history</li></ul></td>
               </tr>
               <tr>
                   <td>KEY-2</td>
                   <td>{{}}</td>
                   <td>{directory_with_two_files}/file2.py</td>
                   <td>foo</td>
                   <td>2 to 3</td>
                   <td>No</td>
                   <td><pre>def foo():
       pass</pre></td>
                   <td><ul><li>No history</li></ul></td>
               </tr>
   </tbody></table>""".splitlines()
    ]
