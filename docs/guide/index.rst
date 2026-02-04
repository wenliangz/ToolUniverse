Tutorial Navigation
===================


This comprehensive tutorial takes you from basic concepts to advanced AI scientist workflows, with everything you need to democratize AI agents for scientific discovery.

Choose the section that matches your current needs:

💡 **For Python API documentation**, see the dedicated :doc:`../api/index` section.

💡 **For MCP integration and server setup**, see the comprehensive :doc:`mcp_support` guide.

Core Concepts
-------------

* **⚙️ Loading Tools** → :doc:`loading_tools` - Complete tutorial to loading tools with Python API and MCP terminal commands
* **📋 Listing Tools** → :doc:`listing_tools` - Discover and filter tools by capability, domain, and IO
* **🔧 Tool Caller** → :doc:`tool_caller` - Primary execution engine with dynamic loading, validation, and MCP server integration
* **🔗 Tool Composition** → :doc:`tool_composition` - Chain ToolUniverse's 1000+ tools into powerful scientific workflows using Tool Composer
* **🐍 Coding API** → :doc:`coding_api` - Import and call tools like normal Python functions with type safety
* **🔬 Scientific Workflows** → :doc:`scientific_workflows` - Real-world research scenarios: drug discovery, safety analysis, literature review
* **📡 MCP Support** → :doc:`mcp_support` - Model Context Protocol integration and server setup
* **✂️ MCP Name Shortening** → :doc:`mcp_name_shortening` - Automatic tool name shortening for MCP 64-character limit compatibility
* **📦 MCPB Support** → :doc:`mcpb_introduction` - Standalone executable bundle for Claude Desktop and other clients
* **🌐 HTTP API** → :doc:`http_api` - Remote access via HTTP/REST with auto-updating server and minimal client dependencies
* **📦 Compact Mode** → :doc:`compact_mode` - Optimize context window usage by exposing only core tools (4 tools) while maintaining full functionality
* **🔊 Streaming Tools** → :doc:`streaming_tools` - Real-time streaming output and custom tool integration
* **📝 Logging** → :doc:`logging` - Comprehensive logging configuration and debugging
* **🗃️ Result Caching** → :doc:`cache_system` - Configure in-memory and persistent caches for tool results
* **🔗 Interaction Protocol** → :doc:`interaction_protocol` - Understanding tool interaction patterns

Tool Discovery & Usage
----------------------

* **🔍 Tool Discovery** → :doc:`../tutorials/finding_tools` - Tutorial to ToolUniverse's three tool finder methods: keyword, LLM, and embedding search
* **📚 Tools Overview** → :doc:`tools` - Comprehensive overview of all available tools

Building AI Scientists
----------------------

* **🤖 Building AI Scientists** → :doc:`building_ai_scientists/index` - Create AI research assistants from LLMs, reasoning models, and agentic systems

  * **🖥️ Claude Desktop** → :doc:`building_ai_scientists/claude_desktop` - Integrate ToolUniverse with Claude Desktop App through MCP
  * **💻 Claude Code** → :doc:`building_ai_scientists/claude_code` - Build AI scientists using Claude Code environment
  * **🔮 Gemini CLI** → :doc:`building_ai_scientists/gemini_cli` - Command-line based scientific research with Gemini CLI
  * **🧠 Qwen Code** → :doc:`building_ai_scientists/qwen_code` - AI scientist integration with Qwen Code environment
  * **⚡ Codex CLI** → :doc:`building_ai_scientists/codex_cli` - Terminal-based AI scientist with Codex CLI
  * **🎯 ChatGPT API** → :doc:`building_ai_scientists/chatgpt_api` - Programmatic scientific research with ChatGPT function calling

LLM Providers
-------------

* **🚀 vLLM Support** → :doc:`vllm_support` - Use self-hosted LLM models with vLLM for high-performance inference
* **🌐 OpenRouter Support** → :doc:`openrouter_support` - Access multiple LLM providers through OpenRouter API

Advanced Features
-----------------

* **🔗 Hooks System** → :doc:`hooks/index` - Intelligent output processing with AI-powered hooks

  * **🤖 SummarizationHook** → :doc:`hooks/summarization_hook` - AI-powered output summarization
  * **💾 FileSaveHook** → :doc:`hooks/file_save_hook` - File-based output processing and archiving
  * **⚙️ Hook Configuration** → :doc:`hooks/hook_configuration` - Advanced configuration and customization
  * **🖥️ Server & Stdio Hooks** → :doc:`hooks/server_stdio_hooks` - Using hooks with server and stdio interfaces

.. note::
   **New to ToolUniverse?** Start with the :doc:`../quickstart` Tutorial for a 5-minute introduction, then come back here for in-depth learning.

Tool Collections
----------------

Specialized tool collections for specific research domains:

* **🏥 Clinical Guidelines** → :doc:`clinical_guidelines_tools` - Search and extract clinical practice guidelines from NICE, WHO, PubMed, and 5 other authoritative sources
* **📖 Literature Search** → :doc:`../tutorials/literature_search_tools_tutorial` - Comprehensive literature search across PubMed, arXiv, bioRxiv, and academic databases
* **⚙️ Space Configurations** → :doc:`toolspace` - Pre-configured tool collections for protein research, genomics, bioinformatics, structural biology, cheminformatics, disease research, drug discovery, literature search, and clinical research. Load directly from GitHub or customize for your needs.
