Claude Code
=============================

**Building AI Scientists with Claude Code and ToolUniverse**

Overview
--------

Claude Code integration enables powerful IDE- or terminal-based scientific research through the Model Context Protocol (MCP). This approach provides a developer-friendly interface for research while leveraging Claude's advanced reasoning and ToolUniverse's 1000+ scientific tools.

.. code-block:: text

   ┌─────────────────┐
   │   Claude Code   │ ← IDE/CLI Interface & Reasoning
   │                 │
   └─────────┬───────┘
             │ MCP Protocol
             │
   ┌─────────▼───────┐
   │ ToolUniverse     │ ← MCP Server
   │   MCP Server     │
   └─────────┬───────┘
             │
   ┌─────────▼───────┐
   │ 1000+ Scientific │ ← Scientific Tools Ecosystem
   │     Tools       │
   └─────────────────┘

**Benefits of Claude Code Integration**:

- **Developer Workflow**: Use Claude inside VS Code/JetBrains or terminal
- **Advanced Reasoning**: Claude's strong multi-step reasoning
- **Comprehensive Tools**: Access to 1000+ ToolUniverse tools
- **Automated Execution**: Natural-language to tools, directly in your editor
- **Batch & Iteration**: Run multi-step research loops effectively

Prerequisites
-------------

Before setting up Claude Code integration, ensure you have:

- **Claude Code**: Installed in your IDE or CLI
- **ToolUniverse**: Installed
- **UV Package Manager**: For running the MCP server
- **System Requirements**: macOS, Windows, or Linux with Python 3.10+
- **API Keys**: For specific tools or optional hooks (e.g., Azure OpenAI for summarization)

Installation and Setup
----------------------

Step 0: Install Claude Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install Claude Code in your terminal (any OS with Node.js 18+):

.. code-block:: bash

   # Standard (recommended)
   npm install -g @anthropic-ai/claude-code

Verify and diagnose your installation:

.. code-block:: bash

   claude doctor

Native installer (beta) alternatives:

.. code-block:: bash

   # macOS/Linux/WSL: stable
   curl -fsSL https://claude.ai/install.sh | bash
   # latest
   curl -fsSL https://claude.ai/install.sh | bash -s latest

On Windows PowerShell:

.. code-block:: powershell

   irm https://claude.ai/install.ps1 | iex

After installation, you can start Claude Code in a project:

.. code-block:: bash

   cd your-project
   claude

For details, see: `Anthropic — Set up Claude Code <https://docs.anthropic.com/en/docs/claude-code/setup>`_.

For Windows installation, see: `Anthropic — Windows setup <https://docs.anthropic.com/en/docs/claude-code/setup#windows-setup>`_.

Step 1: Install uv and ToolUniverse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install uv package manager:

.. code-block:: bash

   # macOS/Linux: official installer
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Verify installation
   uv --version

For Windows installation and other methods, see: `uv installation Tutorial <https://docs.astral.sh/uv/getting-started/installation/>`_.

Set up a dedicated uv environment and install ToolUniverse:

.. code-block:: bash

   # Create working directory for ToolUniverse
   # uv will automatically create and manage a virtual environment (.venv) inside this directory
   mkdir -p /path/to/tooluniverse-env

   # Install ToolUniverse into that uv environment
   uv --directory /path/to/tooluniverse-env pip install tooluniverse

   # Verify installation
   uv --directory /path/to/tooluniverse-env run python -c "import tooluniverse; print('ToolUniverse installed successfully')"

Step 2: Test ToolUniverse MCP server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test that the ToolUniverse MCP server works:

.. code-block:: bash

   # Test the MCP server command
   uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio --help

Step 3: Add ToolUniverse MCP server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Claude Code's built-in command to add ToolUniverse as an MCP server:

.. code-block:: bash

   # Add ToolUniverse MCP server with local scope (recommended for personal use)
   claude mcp add tooluniverse --scope local --env AZURE_OPENAI_API_KEY=your-key --env AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio

**Alternative scope options:**

- ``--scope local`` (default): Available only in current project directory
- ``--scope project``: Shared across project team via ``.claude/.mcp.json``
- ``--scope user``: Available across all your projects

**Environment variables (optional):**

Add ``--env`` flags only if you need summarization hooks or tools requiring API keys:

.. code-block:: bash

   # Minimal setup (no API keys needed for most tools)
   claude mcp add tooluniverse --scope local -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio

**Optimized Configuration for Research Users (Recommended):**

.. code-block:: bash

   # Add ToolUniverse with optimized settings for research
   claude mcp add tooluniverse --scope local --env AZURE_OPENAI_API_KEY=your-key --env AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio --exclude-tool-types PackageTool --hook-type SummarizationHook

**Configuration Benefits:**

- ``--exclude-tool-types PackageTool``: Removes package management tools to save context window space if you don't have coding needs
- ``--hook-type SummarizationHook``: Provides summary of the output that is too long to fit in the context window
- ``AZURE_OPENAI_API_KEY`` and ``AZURE_OPENAI_ENDPOINT``: Required for SummarizationHook functionality

**Verify the server was added:**

.. code-block:: bash

   # List all MCP servers
   claude mcp list

   # Get details about ToolUniverse server
   claude mcp get tooluniverse

See: `Claude Code MCP documentation <https://docs.anthropic.com/en/docs/claude-code/mcp>`_ for advanced configuration options.

For MCP scope management, see: `MCP installation scopes <https://docs.anthropic.com/en/docs/claude-code/mcp#mcp-installation-scopes>`_.

Step 4: Verify in IDE/CLI
~~~~~~~~~~~~~~~~~~~~~~~~~

After saving the configuration, verify connectivity:

- Terminal (Claude Code CLI)
  - Launch in your project:

    .. code-block:: bash

       cd /path/to/your-project
       claude

  - In the chat, ask: "What ToolUniverse tools are available?"
  - If issues occur, run diagnostics:

    .. code-block:: bash

       claude doctor

  - For terminal configuration, see: `Claude Code CLI reference <https://docs.anthropic.com/en/docs/claude-code/cli-reference>`_

- VS Code
  - Restart VS Code, then open Command Palette and run: "Claude: Open Chat"
  - Ask: "What ToolUniverse tools are available?"
  - If tools don't appear, check `.claude/settings.local.json` and reload window
  - For VS Code setup, see: `Add Claude Code to your IDE <https://docs.anthropic.com/en/docs/claude-code/add-claude-code-to-your-ide>`_

- JetBrains (IntelliJ/PyCharm/etc.)
  - Restart IDE → open the Claude tool window
  - Ask: "What ToolUniverse tools are available?"
  - If tools don't appear, review Tools → Claude Code → MCP Servers settings
  - For JetBrains setup, see: `Add Claude Code to your IDE <https://docs.anthropic.com/en/docs/claude-code/add-claude-code-to-your-ide>`_

Scientific Research Capabilities
--------------------------------

Drug Discovery and Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Claude Code with ToolUniverse enables comprehensive drug discovery workflows:

**Target Identification**:
- Disease analysis and EFO ID lookup
- Target discovery and validation
- Literature-based target assessment

**Drug Analysis**:
- Drug information retrieval from multiple databases
- Safety profile analysis
- Drug interaction checking
- Clinical trial data access

Genomics and Molecular Biology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Access comprehensive genomics tools for molecular research:

**Gene Analysis**:
- Gene information from UniProt
- Protein structure analysis
- Expression pattern analysis
- Pathway involvement

**Molecular Interactions**:
- Protein-protein interactions
- Drug-target interactions
- Pathway analysis
- Functional annotation

Literature Research and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive literature search and analysis capabilities:

**Literature Search**:
- PubMed, Europe PMC, and Semantic Scholar
- Citation analysis and trend detection

**Content Analysis**:
- Abstract summarization
- Key finding extraction
- Gap identification

Multi-Step Research Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Claude Code excels at complex, multi-step research workflows:

**Hypothesis-Driven Research**:
1. Formulate a hypothesis
2. Design an approach and select tools
3. Gather supporting evidence
4. Validate findings
5. Generate conclusions

Settings and Configuration
--------------------------

Tool Selection Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~

Optimize tool usage for better performance:

**Selective Tool Loading**:
- Load only relevant tools for specific research domains
- Reduce context usage and improve response times

**Example Tool Selection**:

.. code-block:: bash

   # Add ToolUniverse with specific tool filtering
   claude mcp add tooluniverse-research --scope local -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio --include-tools EuropePMC_search_articles,ChEMBL_search_similar_molecules,openalex_literature_search,search_clinical_trials

   # Verify the server configuration
   claude mcp get tooluniverse-research

Multiple MCP Servers
~~~~~~~~~~~~~~~~~~~~

Run multiple ToolUniverse instances for different purposes:

.. code-block:: bash

   # Add research-focused instance
   claude mcp add tooluniverse-research --scope local -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio --include-tools EuropePMC_search_articles,openalex_literature_search

   # Add analysis-focused instance
   claude mcp add tooluniverse-analysis --scope local -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio --include-tools ChEMBL_search_similar_molecules,search_clinical_trials

   # List all configured servers
   claude mcp list

   # Remove a server if needed
   claude mcp remove tooluniverse-research

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**MCP Server Not Loading**:
- Verify ToolUniverse installation path and absolute paths
- Check UV package manager installation
- Run `claude mcp list` to see current servers
- Check server logs with `claude mcp get tooluniverse`
- For troubleshooting, see: `Claude Code troubleshooting <https://docs.anthropic.com/en/docs/claude-code/troubleshooting>`_

**No Tools Discovered**:
- Verify the ToolUniverse MCP server command runs locally
- Check if your tool filters are too restrictive
- Ensure all ToolUniverse dependencies are installed
- Use `claude doctor` for system diagnostics

**Tools Not Executing**:
- Provide required API keys via `--env` flags when adding the server
- Verify network connectivity to external APIs
- Check MCP output limits, see: `MCP output limits <https://docs.anthropic.com/en/docs/claude-code/mcp#mcp-output-limits-and-warnings>`_

Tips
----

**Tool Selection**: Use `--include-tools` to load only the tools you need for better performance.

**Status Check**: Use `claude mcp list` and `claude mcp get <server>` to inspect MCP servers.

**Keep Paths Absolute**: Avoid relative paths in MCP config to prevent resolution issues.

**Authentication**: For OAuth-based MCP servers, use `/mcp` command in Claude Code chat for secure authentication.

**Resources**: Reference external resources with `@server:protocol://path` syntax in your prompts.

For comprehensive documentation, see: `Claude Code documentation <https://docs.anthropic.com/en/docs/claude-code/>`_.
