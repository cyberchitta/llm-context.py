---
description: Context for updating README and user guide with latest architectural changes
overview: full
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
gitignores:
  full-files: ["src/**", "tests/**"]
  excerpted-files: ["src/**", "tests/**"]
also-include:
  full-files:
    - "/README.md"
    - "/docs/user-guide.md"
    - "/CHANGELOG.md"
    - "/pyproject.toml"
  excerpted-files:
    - "/src/llm_context/cli.py"
    - "/src/llm_context/mcp.py"
    - "/.llm-context/rules/lc/*.md"
---

## Documentation Update Context

This rule provides context for updating project documentation to reflect:

1. **Unified excerpting system** (replacing outlining terminology)
2. **Consolidated file selection** with `lc-select` command
3. **Unified context retrieval** with `lc-missing` tool
4. **New SFC excerpter** for Svelte/Vue files
5. **Updated CLI commands** and MCP tools
6. **New rule composition** with excerpters

Focus on user-facing documentation that explains the current system architecture and commands.
