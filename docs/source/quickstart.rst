Quickstart
==========================================

The basic implementation is a decorator that accepts arbitrary keyword arguments:

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

What sort of things might you want to do with this?

*  Enforce specific formats for the traceability keys
*  Enforce specific information in the metadata (eg JIRA ticket numbers, etc)
*  Enforce a 'category' tag and ensure it takes one of a fixed set of values

Once you've defined your custom decorator, you can start using them in the codebase.

.. literalinclude:: ../../example/example.py

You can then extract this decorator either programmatically

.. invisible-code-block: python
   import json
   from pprint import pprint

>>> from pytraceability.collector import PyTraceabilityCollector
>>> from pytraceability.config import PyTraceabilityConfig
>>> config = PyTraceabilityConfig(base_directory='example', output_format='json')
>>> pprint(json.loads(list(PyTraceabilityCollector(config).get_printable_output())[0]))
{'reports': [{'contains_raw_source_code': False,
              'end_line_number': 11,
              'file_path': 'example/example.py',
              'function_name': 'example',
              'history': None,
              'key': 'EXAMPLE-1',
              'line_number': 10,
              'metadata': {'info': 'As an example, I might want to track the '
                                   'implementation of this function, and link '
                                   'it to a requirement.',
                           'requirement': 'JIRA-1234'},
              'source_code': 'def example():\n    return "An exciting value"'}]}

Or via the command line:

.. code-block:: bash

  $ pytraceability --base-directory example --output-format key-only --decorator-name=traceability
  EXAMPLE-1
