tu — ToolUniverse CLI
=====================

``tu`` is the command-line interface for ToolUniverse. It mirrors the compact-mode MCP tools so you can discover and call tools directly from your shell.

.. code-block:: bash

   tu <command> [options]

Output is human-readable by default. Add ``--json`` for pretty JSON or ``--raw`` for compact JSON (pipe-friendly).

---

Commands
--------

list
~~~~

List available tools. Default view shows category counts; add ``--categories`` to list tools within a category.

.. code-block:: bash

   tu list                               # category overview
   tu list --categories uniprot          # tools in a category (case-insensitive)
   tu list --mode basic --limit 20       # names + descriptions
   tu list --mode custom --fields name type category

Modes: ``names``, ``categories`` (default), ``basic``, ``by_category``, ``summary``, ``custom``

grep
~~~~

Search tools by text or regex.

.. code-block:: bash

   tu grep protein                       # substring search in names
   tu grep protein --field description
   tu grep '^UniProt' --mode regex
   tu grep drug --limit 20

Fields: ``name`` (default), ``description``, ``type``, ``category``

find
~~~~

Find tools by natural-language query (keyword scoring, no API key needed).

.. code-block:: bash

   tu find 'protein structure analysis'
   tu find 'search for drug targets' --limit 5
   tu find 'gene expression' --categories GTEx ENCODE

info
~~~~

Show the schema for one or more tools.

.. code-block:: bash

   tu info UniProt_get_entry_by_accession
   tu info UniProt_get_entry_by_accession --detail description
   tu info UniProt_get_entry_by_accession ChEMBL_get_molecule

run
~~~

Execute a tool. Arguments can be ``key=value`` pairs or a JSON string.

.. code-block:: bash

   tu run UniProt_get_entry_by_accession accession=P12345
   tu run list_tools mode=categories limit=5
   tu run list_tools '{"mode": "categories"}'   # JSON also works

test
~~~~

Test a tool with example inputs and report pass/fail. Optionally provide custom input as a JSON string.

.. code-block:: bash

   tu test Dryad_search_datasets              # use built-in example inputs
   tu test MyAPI_search '{"q": "test"}'       # custom input

status
~~~~~~

Show how many tools are loaded and the top categories.

.. code-block:: bash

   tu status

build
~~~~~

Regenerate the static tool registry and the coding-API wrapper files (``tools/*.py``). Run this after adding or modifying built-in tools.

By default the wrapper files are written to ``.tooluniverse/coding_api/`` in the current directory — the installed package in ``site-packages`` is never touched. Use ``--output`` to override.

.. code-block:: bash

   tu build                              # → .tooluniverse/coding_api/
   tu build --output ./my_tools          # → ./my_tools/
   tu build --output src/tooluniverse/tools  # developer: update source tree

serve
~~~~~

Start the MCP stdio server — identical to ``tooluniverse``.

.. code-block:: bash

   tu serve

---

Output flags
------------

All commands accept ``--json`` (pretty JSON) and ``--raw`` (compact JSON):

.. code-block:: bash

   tu list --json                        # pretty JSON
   tu status --raw | jq '.top_categories'

---

See Also
--------

- :doc:`toolspace` — configure which tools load via ``profile.yaml``
- :doc:`building_ai_scientists/compact_mode` — compact mode in MCP
