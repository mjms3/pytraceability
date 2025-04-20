from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        PythonCodeBlockParser(future_imports=["print_function"]),
    ],
    pattern="*.rst",
).pytest()
