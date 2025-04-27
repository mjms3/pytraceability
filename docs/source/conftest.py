from subprocess import check_output
from textwrap import dedent

from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.rest import CodeBlockParser


class BashCodeBlockParser(CodeBlockParser):
    language = "bash"

    def evaluate(self, example):
        command, expected = dedent(example.parsed).strip().split("\n")
        actual = check_output(command[2:].split()).strip().decode("ascii")
        assert actual == expected, repr(actual) + " != " + repr(expected)


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        BashCodeBlockParser(),
        PythonCodeBlockParser(future_imports=["print_function"]),
    ],
    pattern="*.rst",
).pytest()
