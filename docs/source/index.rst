Welcome to pytraceability's documentation!
==========================================

.. warning::
    This project is still a work in flux. Although the core functionality is largely there,
    the API is not stable and some parts will definitely change in the future.

    Caveat utilitor!

**pytraceability** is a Python library that helps you link code to requirements.

Problem Statement
-----------------

There is often a tension between working in an agile environment and the need to track the link
between requirements and implementation, especially in a heavily regulated industry.

Part of this problem can be solved using a requirements management tool, but these tools
generally work better for the requirements side of the equation than the implementation side and don't integrate
well with the codebase.

Solution
--------

**pytraceability** is designed to help bridge this gap by providing a way to annotate code with traceability information
in a way that is lightweight and easy to integrate into existing workflows.

The core design is to provide a decorator with ``key`` that can be used to annotate functions, classes,
and methods with traceability information stored in a ``metadata`` dictionary.

It provides a command line interface (CLI) and a Python API for extracting all the tagged traceability information
from the codebase and generating a report in a variety of formats.

History Tracking
----------------

Most importantly, it can search through git history to track changes to the code that is marked as implementing a
specific requirement (based on a specific decorator). Because this tracking is based on the decorator ``key``, it can
do this in a much more comprehensive way that is possible with git line or function history alone.
This is particularly useful in a heavily regulated environment where you need to be able to demonstrate
that a requirement has been implemented and that - although the file containing the code might have changed with
eg dependency upgrades, the core implementation of the functionality has not changed.


Have a look at the :doc:`sample_report` for an example.

.. note::
    This report is generated from some decorators in the pytraceability codebase itself. This is not how you would
    use the library in practice, but it provides a good example of the sort of information that can be extracted.

    Note also, that this report is a simplified example and will be improved in future releases.

For further information, check out the :doc:`quickstart` guide or more detailed docs below.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   sample_report
