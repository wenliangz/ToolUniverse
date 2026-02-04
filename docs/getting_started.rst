Getting Started with ToolUniverse
===================================

This tutorial provides detailed, step-by-step instructions for using ToolUniverse effectively.

**Prerequisites**: You should have already completed the :doc:`quickstart` Tutorial and have ToolUniverse installed (see :doc:`installation`). This tutorial assumes basic Python knowledge and internet access for API calls.

🧪 Step-by-Step Tutorial
----------------

Understanding Basic Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ToolUniverse follows a simple but powerful pattern:

1. **Initialize once**: Create a ToolUniverse instance
2. **Load tools**: Load available tools from various databases
3. **Query tools**: Use standardized query format
4. **Get results**: Receive structured data

.. seealso::
   For full AI-Tool Interaction Protocol, see :doc:`guide/interaction_protocol`

Let's start with a simple example and build up complexity:

Step 1: Initialize ToolUniverse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a ToolUniverse instance and load scientific tools. This step sets up the foundation for accessing 1000+ tools across various scientific domains.

.. code-block:: python

   from tooluniverse import ToolUniverse

   # Initialize ToolUniverse
   tu = ToolUniverse()

   # Load all tools
   print("Loading scientific tools...")
   tu.load_tools()

   print(f"✅ Loaded {len(tu.all_tools)} scientific tools!")

.. seealso::
   For detailed tool loading options and configurations, see :doc:`guide/loading_tools`

Step 2: Explore Available Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List built-in tools in ToolUniverse: This method supports two different organization modes to help you understand tools from different perspectives.

.. code-block:: python

    # organize by config file categories
    stats = tu.list_built_in_tools(mode='config')
    # or organize by tool types
    stats = tu.list_built_in_tools(mode='type')

.. seealso::
   For comprehensive tool listing methods, see :doc:`guide/listing_tools`

To find tools by description, use the Find Tool operation. This feature helps you or your AI scientists discover relevant tools based on their descriptions.
We support three search methods: keyword search, LLM-based search, and embedding search.

.. code-block:: python

   # Search for specific tools
   protein_tools = tu.run({
       "name": "Tool_Finder_Keyword", # or Tool_Finder_LLM (LLM-API based) or Tool_Finder (Embedding-based)
       "arguments": {
           "description": "protein structure",
           "limit": 5
       }
   })
   print(f"Found {len(protein_tools)} protein-related tools")

.. seealso::
     For comprehensive tool search methods, see :doc:`tutorials/finding_tools`

Step 3: Load Tool Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inspect tool specifications to understand their parameters and capabilities before execution. This helps you or your AI scientists understand what arguments each tool expects and how to use them effectively.

.. code-block:: python

   # Get tool specification by name
   spec = tu.tool_specification("UniProt_get_function_by_accession")
   print("Tool specification:")
   print(f"Name: {spec['name']}")
   print(f"Description: {spec['description']}")
   print("Parameters:")
   for param_name, param_info in spec['parameters']['properties'].items():
       print(f"  - {param_name}: {param_info['type']} - {param_info['description']}")

   # Get multiple tool specifications
   specs = tu.get_tool_specification_by_names([
       "FAERS_count_reactions_by_drug_event",
       "OpenTargets_get_associated_targets_by_disease_efoId"
   ])
   print(specs)

.. seealso::
   For detailed tool specification schema and interaction protocols, see :doc:`guide/interaction_protocol`

Step 4: Execute Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Execute scientific tools using the standardized query format. All tools follow a consistent structure that makes it easy to work with different scientific databases and APIs.

All tools follow this consistent structure:

.. code-block:: python

   # Standardized tool execution across all 1000+ tools
   query = {
       "name": "action_description",  # Tool identifier
       "arguments": {                 # Tool parameters
           "parameter1": "value1",
           "parameter2": "value2"
       }
   }

   result = tu.run(query)

.. seealso::
   For detailed tool execution patterns and advanced usage, see :doc:`guide/tool_caller`


**Execute your First Scientific Tool Call**

Run your scientific tool call to use tools. This demonstrates how to access drug safety, gene information, literature, and disease data through standardized tool calls.


Retrieve comprehensive protein and gene information from UniProt database. Get protein sequences, functions, annotations, and related biological data.

.. code-block:: python

   # Get comprehensive gene information
   gene_query = tu.run({
      "name": "UniProt_get_function_by_accession",
      "arguments": {"accession": "P05067"}
   })
   gene_info = tu.run(gene_query)
   print(gene_info)


Analyze drug safety profiles using FDA adverse event reporting data. Identify potential side effects and safety concerns for pharmaceutical compounds.

.. code-block:: python

   # Check drug adverse events
   safety_query = {
       "name": "FAERS_count_reactions_by_drug_event",
       "arguments": {"medicinalproduct": "aspirin"}
   }
   safety_data = tu.run(safety_query)
   print(safety_data)


Explore disease-target relationships using OpenTargets platform. Discover therapeutic targets associated with specific diseases and their evidence scores.

.. code-block:: python

   # Find targets associated with a disease
   disease_query = {
       "name": "OpenTargets_get_associated_targets_by_disease_efoId",
       "arguments": {"efoId": "EFO_0000685"}  # Rheumatoid arthritis
   }
   targets = tu.run(disease_query)

   print(targets)


Search scientific literature across multiple databases with entity recognition. Find relevant papers, abstracts, and citations for your research topics.

.. code-block:: python

   # Search scientific literature
   literature_query = {
       "name": "PubTator_search_publications",
       "arguments": {
           "query": "CRISPR cancer therapy",
           "limit": 10
       }
   }
   papers = tu.run(literature_query)

   print(papers)


.. seealso::
   ToolUniverse support the building of complex scientific workflows. For advanced workflow patterns and tool composition, see :doc:`guide/scientific_workflows`

MCP Server Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect ToolUniverse to AI assistants through the Model Context Protocol (MCP). This enables AI agents to discover and execute scientific tools automatically, creating powerful AI-scientist workflows.

.. code-block:: bash

   # Start ToolUniverse MCP server with HTTP transport
   tooluniverse-smcp

   # Start ToolUniverse MCP server with STDIO transport
   tooluniverse-smcp-stdio


.. code-block:: python

   # Python MCP server setup
   from tooluniverse.smcp import SMCP

   # Create MCP server
   server = SMCP(
       name="Scientific Research Server",
       tool_categories=["uniprot", "opentarget", "ChEMBL"],
       search_enabled=True
   )

   # Start server
   server.run_simple(transport="http", host="localhost", port=7000)

.. seealso::
   For complete MCP server setup, configuration, and integration, see :doc:`guide/mcp_support`

.. seealso::
   For complete MCP integration with LLMs/Reasoning models/AI Agents like Claude, ChatGPT, Gemini, and Qwen, see :doc:`guide/building_ai_scientists/index`

ToolUniverse Features
----------------------

💡 **For Python API documentation**, see the dedicated :doc:`api/modules` section.

📖 Building AI Scientists
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Building AI Scientists Overview** → :doc:`guide/building_ai_scientists/index` - Transform any LLM into a powerful research scientist

  * **Claude Desktop** → :doc:`guide/building_ai_scientists/claude_desktop` - Integrate ToolUniverse with Claude Desktop App through MCP
  * **Claude Code** → :doc:`guide/building_ai_scientists/claude_code` - Build AI scientists using Claude Code environment
  * **Gemini CLI** → :doc:`guide/building_ai_scientists/gemini_cli` - Command-line based scientific research with Gemini CLI
  * **Qwen Code** → :doc:`guide/building_ai_scientists/qwen_code` - AI scientist integration with Qwen Code environment
  * **Codex CLI** → :doc:`guide/building_ai_scientists/codex_cli` - Terminal-based AI scientist with Codex CLI
  * **ChatGPT API** → :doc:`guide/building_ai_scientists/chatgpt_api` - Programmatic scientific research with ChatGPT function calling

Tools
~~~~~

* **Tools Configuration Index** → :doc:`tools/tools_config_index` - Complete index of all available tools
* **Remote Tools Setup** → :doc:`tools/remote_tools` - Setup and configuration for remote tools


📖 Use ToolUniverse
~~~~~~~~~~~~~~~~~~~

* **Guide Overview** → :doc:`guide/index` - Comprehensive guide to using ToolUniverse
* **Interaction Protocol** → :doc:`guide/interaction_protocol` - AI-Tool interaction standards and protocols
* **Loading Tools** → :doc:`guide/loading_tools` - Complete tutorial to loading tools with Python API and MCP terminal commands
* **Listing Tools** → :doc:`guide/listing_tools` - Discover and filter tools by capability, domain, and IO
* **Tool Discovery** → :doc:`tutorials/finding_tools` - Tutorial to ToolUniverse's three tool finder methods: keyword, LLM, and embedding search
* **Tool Caller** → :doc:`guide/tool_caller` - Primary execution engine with dynamic loading, validation, and MCP server integration
* **Case Study** → :doc:`tutorials/tooluniverse_case_study` - End-to-end hypercholesterolemia drug discovery workflow with Gemini 2.5 Pro
* **Agentic Tools** → :doc:`tutorials/agentic_tools_tutorial` - Build and use AI-powered tools with LLMs for tasks requiring reasoning and creativity
* **Tool Composition** → :doc:`guide/tool_composition` - Chain ToolUniverse's 1000+ tools into powerful scientific workflows using Tool Composer
* **Scientific Workflows** → :doc:`guide/scientific_workflows` - Real-world research scenarios: drug discovery, safety analysis, literature review
* **Expert Feedback** → :doc:`tutorials/expert_feedback` - Human-in-the-loop consultation platform for AI systems with web interface
* **Embedding Tools** → :doc:`tools/embedding_tools` - Setup and configuration for embedding storage
* **Hooks System** → :doc:`guide/hooks/index` - Intelligent output processing with AI-powered hooks

  * **SummarizationHook** → :doc:`guide/hooks/summarization_hook` - AI-powered output summarization
  * **FileSaveHook** → :doc:`guide/hooks/file_save_hook` - File-based output processing and archiving
  * **Hook Configuration** → :doc:`guide/hooks/hook_configuration` - Advanced configuration and customization
  * **Server & Stdio Hooks** → :doc:`guide/hooks/server_stdio_hooks` - Using hooks with server and stdio interfaces

🛠️ Add Tools to ToolUniverse
~~~~~~~~~~~~~~~~~~~~~~~

* **Tool Development Overview** → :doc:`expand_tooluniverse/index` - Learn how to extend ToolUniverse with your own custom tools
* **Quick Start** → :doc:`expand_tooluniverse/quick_start` - 5-minute tutorial to create your first tool
* **Local Tools** → :doc:`expand_tooluniverse/local_tools/index` - Create tools that run within ToolUniverse
* **Remote Tools** → :doc:`expand_tooluniverse/remote_tools/index` - Integrate external services and APIs
* **Contributing** → :doc:`expand_tooluniverse/contributing/index` - Submit your custom tools to the ToolUniverse repository
* **Tool Comparison** → Review the tool type comparison table in :doc:`expand_tooluniverse/contributing/index`
* **Architecture** → :doc:`expand_tooluniverse/architecture` - ToolUniverse's code architecture and extension points
* **Deployment** → :doc:`deployment` - Deployment guide for production environments
* **Contributing** → :doc:`contributing` - How to contribute to ToolUniverse development

📚 API & Reference
~~~~~~~~~~~~~~~~~~~

* **API Modules** → :doc:`api/modules` - Complete API reference documentation
* **Reference Index** → :doc:`reference/index` - Reference documentation and specifications
* **Help & Support** → :doc:`help/index` - Help resources and troubleshooting guides

.. seealso::
   For complete tool reference and capabilities, see :doc:`guide/tools`