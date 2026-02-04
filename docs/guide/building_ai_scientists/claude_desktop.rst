Claude Desktop
=================================

**Building AI Scientists with Claude Desktop App and ToolUniverse**

Overview
--------

Claude Desktop Integration enables seamless connection between Claude Desktop App and ToolUniverse's scientific tools ecosystem through the Model Context Protocol (MCP). This approach provides a user-friendly interface for scientific research while leveraging Claude's advanced reasoning capabilities and ToolUniverse's comprehensive scientific tools.

.. code-block:: text

   ┌─────────────────┐
   │ Claude Desktop  │ ← User Interface & Reasoning
   │      App        │
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

**Benefits of Claude Desktop Integration**:

- **Intuitive Interface**: Natural conversation-based interaction with scientific tools
- **Advanced Reasoning**: Claude's sophisticated reasoning for complex scientific problems
- **Comprehensive Tools**: Access to 1000+ scientific tools across multiple domains
- **Real-time Execution**: Direct tool execution within Claude conversations
- **Context Awareness**: Claude maintains context across multiple tool interactions

Example Integration
-------------------

For a practical example of using ToolUniverse-MCP with Claude Desktop, see the following demonstration:

.. image:: /_static/claude_desktop.jpg
   :alt: Claude Desktop Integration Example
   :align: center
   :width: 800px

.. note::
   **Image Source**: This example shows Claude Desktop using ToolUniverse tools for scientific research. To view the full interactive example, visit the `Claude MCP Integration Example <https://claude.ai/share/ab797b7f-6e6b-46f6-b1d5-5a790b90f42d>`_.

Prerequisites
-------------

Before setting up Claude Desktop integration, ensure you have:

- **Claude Desktop App**: Installed and running on your system
- **UV Package Manager**: For running the MCP server

Installation and Setup
----------------------

Step 1: Install ToolUniverse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install ToolUniverse using pip (uv is recommended):

.. code-block:: bash

   uv pip install tooluniverse

Verify installation:

.. code-block:: bash

   python -c "import tooluniverse; print('ToolUniverse installed successfully')"

Step 2: Locate Claude Desktop Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open Claude Desktop App and navigate to the configuration:

1. **Open Claude Desktop App**
2. **Go to Settings** → **Developer** → **Edit Config**
3. **Note the configuration file location** (typically in your user directory)

The configuration file will be opened in your default text editor.

Step 3: Configure ToolUniverse MCP Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the ToolUniverse MCP server configuration to your Claude Desktop config:

.. code-block:: json

   {
     "mcpServers": {
       "tooluniverse": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory: uv manages .venv here
           "run",
           "tooluniverse-smcp-stdio"
         ]
       }
     }
   }

**Important Configuration Notes**:

- Replace `/path/to/tooluniverse-env` with your actual ToolUniverse working directory
- The working directory is where uv will create and manage the virtual environment (`.venv`)
- Use absolute paths for better reliability
- Install ToolUniverse first: ``uv --directory /path/to/tooluniverse-env pip install tooluniverse``

**Example Configuration**:

.. code-block:: json

   {
     "mcpServers": {
       "tooluniverse": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-smcp-stdio"
         ]
       }
     }
   }

Step 4: Restart Claude Desktop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After saving the configuration:

1. **Completely quit Claude Desktop App**
2. **Restart Claude Desktop App**
3. **Verify the MCP server is loaded** (check the developer console if needed)

Step 5: Verify Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test the integration by asking Claude to:

1. **List available tools**:
   - "What scientific tools are available?"
   - "Show me the tools for drug discovery"

2. **Execute a simple tool**:
   - "Search for information about Alzheimer's disease"
   - "Find protein information for BRCA1"

3. **Perform complex research**:
   - "Analyze the safety profile of aspirin"
   - "Find potential drug targets for diabetes"

Scientific Research Capabilities
--------------------------------

Drug Discovery and Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Claude Desktop with ToolUniverse enables comprehensive drug discovery workflows:

**Target Identification**:
- Disease analysis and EFO ID lookup
- Target discovery and validation
- Literature-based target assessment

**Drug Analysis**:
- Drug information retrieval from multiple databases
- Safety profile analysis
- Drug interaction checking
- Clinical trial data access

**Example Workflow**:

.. code-block:: text

   User: "I want to discover potential drug targets for Alzheimer's disease"

   Claude: "I'll help you identify potential drug targets for Alzheimer's disease. Let me start by gathering comprehensive information about the disease and its associated targets."

   [Claude uses ToolUniverse tools to:]
   1. Get disease information and EFO ID
   2. Find associated targets
   3. Analyze target evidence
   4. Search literature for validation
   5. Identify existing drugs for top targets
   6. Provide comprehensive analysis

Genomics and Molecular Biology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

**Example Workflow**:

.. code-block:: text

   User: "Analyze the BRCA1 gene and its role in cancer"

   Claude: "I'll perform a comprehensive analysis of BRCA1 and its role in cancer development. Let me gather information about the gene, protein, and its interactions."

   [Claude uses ToolUniverse tools to:]
   1. Get BRCA1 gene information
   2. Analyze protein structure and function
   3. Find protein interactions
   4. Identify cancer-related pathways
   5. Search for therapeutic targets
   6. Provide detailed analysis

Literature Research and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive literature search and analysis capabilities:

**Literature Search**:
- PubMed searches
- Semantic Scholar integration
- Europe PMC access
- Citation analysis

**Content Analysis**:
- Abstract summarization
- Key finding extraction
- Trend analysis
- Gap identification

**Example Workflow**:

.. code-block:: text

   User: "Find recent research on CRISPR gene editing in cancer therapy"

   Claude: "I'll search for recent research on CRISPR gene editing applications in cancer therapy. Let me gather comprehensive literature and analyze the findings."

   [Claude uses ToolUniverse tools to:]
   1. Search PubMed for recent papers
   2. Analyze abstracts and key findings
   3. Identify research trends
   4. Find clinical trials
   5. Assess therapeutic potential
   6. Provide comprehensive review

Clinical Research and Trials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Access clinical trial data and regulatory information:

**Clinical Trials**:
- ClinicalTrials.gov searches
- Trial status and results
- Patient population analysis
- Outcome assessment

**Regulatory Information**:
- FDA drug approvals
- Safety warnings
- Labeling information
- Adverse event reports

**Example Workflow**:

.. code-block:: text

   User: "Find clinical trials for immunotherapy in lung cancer"

   Claude: "I'll search for clinical trials investigating immunotherapy treatments for lung cancer. Let me gather information about ongoing and completed trials."

   [Claude uses ToolUniverse tools to:]
   1. Search ClinicalTrials.gov
   2. Filter by immunotherapy and lung cancer
   3. Analyze trial designs and outcomes
   4. Check FDA approvals
   5. Assess safety profiles
   6. Provide comprehensive overview

Drug Discovery Workflow
~~~~~~~~~~~~~~~~~~~~~~~

Complete drug discovery workflow using Claude Desktop:

.. code-block:: text

   User: "Help me discover new drug targets for Parkinson's disease"

   Claude: "I'll help you discover potential drug targets for Parkinson's disease. Let me start by analyzing the disease and identifying associated targets."

   [Step 1: Disease Analysis]
   - Get Parkinson's disease information and EFO ID
   - Analyze disease characteristics and symptoms
   - Identify key pathological processes

   [Step 2: Target Discovery]
   - Find genes associated with Parkinson's disease
   - Analyze protein-protein interactions
   - Identify druggable targets

   [Step 3: Literature Validation]
   - Search for recent research on identified targets
   - Analyze therapeutic potential
   - Check for existing drug development

   [Step 4: Drug Analysis]
   - Find existing drugs for top targets
   - Analyze mechanisms of action
   - Assess safety profiles

   [Step 5: Recommendations]
   - Prioritize targets based on evidence
   - Suggest next steps for validation
   - Provide comprehensive analysis

Genomics Research Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive genomics analysis workflow:

.. code-block:: text

   User: "Analyze the TP53 gene and its role in cancer development"

   Claude: "I'll perform a comprehensive analysis of TP53 and its role in cancer. Let me gather information about the gene, protein, and its interactions."

   [Step 1: Gene Analysis]
   - Get TP53 gene information from UniProt
   - Analyze gene structure and variants
   - Check expression patterns

   [Step 2: Protein Analysis]
   - Analyze protein structure and function
   - Identify functional domains
   - Check post-translational modifications

   [Step 3: Interaction Analysis]
   - Find protein-protein interactions
   - Analyze protein-DNA interactions
   - Identify regulatory networks

   [Step 4: Cancer Analysis]
   - Find cancer-related mutations
   - Analyze mutation hotspots
   - Check therapeutic implications

   [Step 5: Literature Review]
   - Search for recent TP53 research
   - Analyze therapeutic approaches
   - Identify research gaps

Settings and Configuration
--------------------------

Tool Selection Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~


**Selective Tool Loading**:
- Load only relevant tools for specific research domains
- Reduce context window usage
- Improve response times

**Example Tool Selection**:

.. code-block:: json

   {
     "mcpServers": {
       "tooluniverse": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-mcp-stdio",
           "--tools",
           "drug_discovery,genomics,literature"
         ]
       }
     }
   }

**Custom Tool Sets**

Create custom tool sets for specific research domains:

.. code-block:: json

   {
     "mcpServers": {
       "tooluniverse-drug-discovery": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-mcp-stdio",
           "--toolset",
           "drug_discovery"
         ]
       },
       "tooluniverse-genomics": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-smcp-stdio",
           "--toolset",
           "genomics"
         ]
       }
     }
   }

Multiple MCP Servers
~~~~~~~~~~~~~~~~~~~~

Run multiple ToolUniverse instances for different purposes:

.. code-block:: json

   {
     "mcpServers": {
       "tooluniverse-research": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-smcp-stdio",
           "--mode",
           "research"
         ]
       },
       "tooluniverse-analysis": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/tooluniverse-env",  # Working directory
           "run",
           "tooluniverse-smcp-stdio",
           "--mode",
           "analysis"
         ]
       }
     }
   }


Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**MCP Server Not Loading**:
- Verify uv environment
- Check UV package manager installation
- Ensure proper JSON syntax in configuration
- Check Claude Desktop logs for errors

**Too Many Tools Loaded**:
- Use selective tool loading
- Reduce the number of enabled tools
- Implement tool filtering

**Performance Issues**:
- Implement caching strategies
- Use selective tool loading
- Optimize query patterns

**Connection Issues**:
- Verify network connectivity
- Check firewall settings
- Ensure proper MCP server configuration
