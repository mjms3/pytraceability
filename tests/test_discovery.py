from pytraceability.discovery import discover_traceability


def test_discover_traceability():
    assert discover_traceability() is None