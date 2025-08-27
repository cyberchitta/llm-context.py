# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

**Reduce friction when providing context to LLMs.** Share relevant project files instantly through smart selection and rule-based filtering.

## The Problem

Getting project context into LLM chats is tedious:

- Manually copying/pasting files takes forever
- Hard to identify which files are relevant
- Including too much hits context limits, too little misses important details
- AI requests for additional files require manual fetching
- Repeating this process for every conversation

## The Solution

```bash
lc-sel-files    # Smart file selection
lc-context      # Instant formatted context
# Paste and work - AI can access additional files seamlessly
```

**Result**: From "I need to share my project" to productive AI collaboration in seconds.

> **Note**: This project was developed in collaboration with several Claude Sonnets (3.5, 3.6, 3.7 and 4.0), as well as Groks (3 and 4), using LLM Context itself to share code during development. All code in the repository is heavily human-curated (by me 😇, @restlessronin).

## Installation

```bash
uv tool install "llm-context>=0.4.0"
```

## Quick Start

### Basic Usage

```bash
# One-time setup
cd your-project
lc-init

# Daily usage
lc-sel-files
lc-context
```

### MCP Integration (Recommended)

```jsonc
{
  "mcpServers": {
    "llm-context": {
      "command": "uvx",
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

With MCP, AI can access additional files directly during conversations.

### Project Customization

```bash
# Create project-specific filters
cat > .llm-context/rules/flt-repo-base.md << 'EOF'
---
name: flt-repo-base
compose:
  filters: [lc/flt-base]
gitignores:
  full-files: ["*.md", "/tests", "/node_modules"]
---
EOF

# Customize main development rule
cat > .llm-context/rules/prm-code.md << 'EOF'
---
name: code
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo-base]
---
EOF
```

## Core Commands

| Command              | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `lc-init`            | Initialize project configuration          |
| `lc-sel-files`       | Select files based on current rule        |
| `lc-context`         | Generate and copy context                 |
| `lc-context -nt`     | Generate context for non-MCP environments |
| `lc-set-rule <name>` | Switch between rules                      |
| `lc-clip-files`      | Handle file requests (non-MCP)            |

## Rule System

Rules use a systematic four-category structure:

- **Prompt Rules (`prm-`)**: Generate project contexts (e.g., `lc/prm-developer`, `lc/prm-rule-create`)
- **Filter Rules (`flt-`)**: Control file inclusion (e.g., `lc/flt-base`, `lc/flt-no-files`)
- **Instruction Rules (`ins-`)**: Provide guidelines (e.g., `lc/ins-developer`, `lc/ins-rule-framework`)
- **Style Rules (`sty-`)**: Enforce coding standards (e.g., `lc/sty-python`, `lc/sty-code`)

### Example Rule

```yaml
---
name: tmp-prm-api-debug
description: "Debug API authentication issues"
compose:
  filters: [lc/flt-no-files]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
Focus on authentication system and related tests.
```

## Workflow Patterns

### Daily Development

```bash
lc-set-rule lc/prm-developer
lc-sel-files
lc-context
# AI can review changes, access additional files as needed
```

### Focused Tasks

```bash
# Let AI help create minimal context
lc-set-rule lc/prm-rule-create
lc-context -nt
# Work with AI to create task-specific rule using tmp-prm- prefix
```

### MCP Benefits

- **Code review**: AI examines your changes for completeness/correctness
- **Additional files**: AI accesses initially excluded files when needed
- **Change tracking**: See what's been modified during conversations
- **Zero friction**: No manual file operations during development discussions

## Key Features

**Smart File Selection**: Rules automatically include/exclude appropriate files
**Instant Context Generation**: Formatted context copied to clipboard in seconds
**MCP Integration**: AI can access additional files without manual intervention
**Systematic Rule Organization**: Four-category system for clear rule composition
**AI-Assisted Rule Creation**: Let AI help create minimal context for specific tasks

## Learn More

- [User Guide](docs/user-guide.md) - Complete documentation
- [Design Philosophy](https://www.cyberchitta.cc/articles/llm-ctx-why.html)
- [Real-world Examples](https://www.cyberchitta.cc/articles/full-context-magic.html)

## License

Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
