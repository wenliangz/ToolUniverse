FAQ - Frequently Asked Questions
==================================

Quick answers to the most common questions about ToolUniverse.

What is ToolUniverse?
---------------------

ToolUniverse is a collection of 1000+ scientific tools for AI agents, providing unified access to drug safety data, genomics, literature, clinical trials, and more.

.. code-block:: python

   from tooluniverse import ToolUniverse
   tu = ToolUniverse()
   tu.load_tools()

   result = tu.run({
      "name": "UniProt_get_function_by_accession",
      "arguments": {"accession": "P05067"}
   })

How do I install it?
--------------------

.. code-block:: bash

   pip install tooluniverse

Do I need API keys?
-------------------

Most tools work without API keys. For enhanced features, set these as environment variables:

.. code-block:: bash

   export OPENTARGETS_API_KEY=your_key_here
   export NCBI_API_KEY=your_ncbi_key

How do I use it with Claude?
-----------------------------

1. Start the MCP server: ``python -m tooluniverse.smcp_server``
2. Configure Claude Desktop with the MCP server
3. Ask Claude: "What tools are available from ToolUniverse?"

Need more help?
---------------

- **Troubleshooting**: :doc:`help/troubleshooting`
- **GitHub Issues**: `Report problems <https://github.com/mims-harvard/ToolUniverse/issues>`_
