from pytraceability.common import traceability


@traceability(
    "EXAMPLE-1",
    info="As an example, I might want to track the implementation "
    "of this function, and link it to a requirement.",
    requirement="JIRA-1234",
)
def example():
    return "An exciting value"
