Welcome to pytraceability's documentation!
==========================================

**pytraceability** is a Python library that helps you link code to requirements.
It provides a command line interface (CLI) and a Python API for tracing the
relationships between code and requirements.

And, more importantly, it can search through git history to track changes to the code
that is marked as implementing a specific requirement.
Have a look at the :doc:`sample_report` for an example.

It defines a decorator that can be used to annotate functions, classes, and methods with traceability information,
linking back to requirements and other relevant documentation.

.. code-block:: python

  from pytraceability.common import traceability

  @traceability('REQUIREMENTS_ID',something_else='value')
  def my_function():
      pass

.. invisible-code-block: python
  from pytraceability.data_definition import Traceability
  assert my_function.__traceability__ == [Traceability(key='REQUIREMENTS_ID', metadata={'something_else': 'value'})]

You can define custom decorators to implement your own traceability requirements.

.. literalinclude:: ../../pytraceability/custom.py

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   sample_report
