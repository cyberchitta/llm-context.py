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
lc-select # Smart file selection
lc-context # Instant formatted context
# Paste and work - AI can access additional files seamlessly
```

**Result**: From "I need to share my project" to productive AI collaboration in seconds.

> **Note**: This project was developed in collaboration with several Claude Sonnets (3.5, 3.6, 3.7 and 4.0), as well as Groks (3 and 4), using LLM Context itself to share code during development. All code in the repository is heavily human-curated (by me 😇, @restlessronin).

## Installation

```bash
uv tool install "llm-context>=0.5.0"
```

## Quick Start

### Basic Usage

```bash
# One-time setup
cd your-project
lc-init
# Daily usage
lc-select
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
compose:
  filters: [lc/flt-base]
gitignores:
  full-files: ["*.md", "/tests", "/node_modules"]
---
EOF
# Customize main development rule
cat > .llm-context/rules/prm-code.md << 'EOF'
---
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo-base]
  excerpters: [lc/exc-base]
---
Additional project-specific guidelines and context.
EOF
```

## Deployment Patterns

Choose based on your LLM environment:

- **System Message**: `lc-context -p` (AI Studio, etc.)
- **Single User Message**: `lc-context -p -m` (Grok, etc.)
- **Separate Messages**: `lc-prompt` + `lc-context -m`
- **Project/Files (included)**: `lc-context` (Claude Projects, etc.)
- **Project/Files (searchable)**: `lc-context -m` (force into context)

See [Deployment Patterns](docs/user-guide.md#deployment-patterns) in the user guide for details.

## Core Commands

| Command           | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `lc-init`         | Initialize project configuration           |
| `lc-select`       | Select files based on current rule         |
| `lc-context`      | Generate and copy context                  |
| `lc-context -p`   | Generate context with prompt               |
| `lc-context -m`   | Send context as separate message           |
| `lc-context -nt`  | No tools (for Project/Files inclusion)     |
| `lc-context -f `  | Write context to file                      |
| `lc-set-rule <n>` | Switch between rules                       |
| `lc-missing`      | Handle file and context requests (non-MCP) |

## Rule System

Rules use a systematic five-category structure:

- **Prompt Rules (`prm-`)**: Generate project contexts (e.g., `lc/prm-developer`, `lc/prm-rule-create`)
- **Filter Rules (`flt-`)**: Control file inclusion (e.g., `lc/flt-base`, `lc/flt-no-files`)
- **Instruction Rules (`ins-`)**: Provide guidelines (e.g., `lc/ins-developer`, `lc/ins-rule-framework`)
- **Style Rules (`sty-`)**: Enforce coding standards (e.g., `lc/sty-python`, `lc/sty-code`)
- **Excerpt Rules (`exc-`)**: Configure extractions for context reduction (e.g., `lc/exc-base`)

### Example Rule

```yaml
---
description: "Debug API authentication issues"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
Focus on authentication system and related tests.
```

## AI-Assisted Rule Creation

Let AI create focused rules for specific tasks. There are two approaches depending on your setup:

### Approach 1: Claude Skill (Recommended for Claude Desktop/Code)

**How it works**: A global Claude Skill helps you create rules interactively. It requires project context (with overview) already shared via llm-context, and uses `lc-missing` to examine specific files as needed.

**Setup**:

```bash
lc-init  # Installs skill to ~/.claude/skills/
# Restart Claude Desktop or Claude Code
```

**Workflow**:

```bash
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude

# 3. Ask the Skill to help create a rule
# "Create a rule for refactoring authentication to JWT"
# "I need a rule to debug the payment processing system"
```

Claude will:

1. Use the project overview already in context
2. Use `lc-missing` to examine specific files as needed for deeper analysis
3. Ask clarifying questions about scope and focus
4. Intelligently select relevant files (5-15 full, 10-30 excerpted)
5. Generate optimized rule configuration
6. Save to `.llm-context/rules/tmp-prm-<task-name>.md`
7. Provide instructions for testing the rule

**Skill Files**:

- `Skill.md` - Quick workflow and patterns (always loaded)
- `PATTERNS.md` - Common rule patterns (on demand)
- `SYNTAX.md` - Detailed syntax reference (on demand)
- `EXAMPLES.md` - Complete walkthroughs (on demand)
- `TROUBLESHOOTING.md` - Problem solving (on demand)

**Skill Updates**: Automatically updated when you upgrade llm-context. Restart Claude to use the new version.

### Approach 2: Prompt-Based with Instruction Rules (Works Anywhere)

**How it works**: You use a project rule that loads comprehensive rule-creation documentation as context.

**Setup**: No special setup needed - the documentation is built-in.

**Usage**:

```bash
# 1. Load the rule creation framework into context
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. Paste into any LLM and describe your task
# "I need to add OAuth integration to the auth system"

# 3. The LLM generates a focused rule using the framework

# 4. Use the focused context
lc-set-rule tmp-prm-oauth-task
lc-select
lc-context
```

**Documentation Included**:

- `lc/ins-rule-intro` - Chat-based rule creation introduction
- `lc/ins-rule-framework` - Comprehensive decision framework, semantics, and best practices

### Comparison

| Aspect                       | Skill                             | Instruction Rules               |
| ---------------------------- | --------------------------------- | ------------------------------- |
| **Setup**                    | Automatic with `lc-init`          | Already available               |
| **Requires project context** | Yes (overview needed)             | Yes (overview needed)           |
| **Interaction**              | Interactive, multi-turn in Claude | Static documentation in context |
| **Exploration**              | Uses `lc-missing` as needed       | Manual or via AI requests       |
| **Best for**                 | Claude Desktop/Code users         | Any LLM, API, automation        |

Both approaches require sharing project context first via `lc-context`. They produce equivalent results - choose based on your environment and preference.

## Workflow Patterns

### Daily Development

```bash
lc-set-rule lc/prm-developer
lc-select
lc-context
# AI can review changes, access additional files as needed
```

### Focused Tasks

```bash
# Share project context
lc-context

# Then ask Skill (Claude Desktop/Code):
# "Create a rule for [your task]"

# Or work with any LLM using instruction rules:
# lc-set-rule lc/prm-rule-create && lc-context -nt
```

### MCP Benefits

- **Code review**: AI examines your changes for completeness/correctness
- **Additional files**: AI accesses initially excluded files when needed
- **Change tracking**: See what's been modified during conversations
- **Zero friction**: No manual file operations during development discussions

## Key Features

- **Smart File Selection**: Rules automatically include/exclude appropriate files
- **Instant Context Generation**: Formatted context copied to clipboard in seconds
- **MCP Integration**: AI can access additional files without manual intervention
- **Systematic Rule Organization**: Five-category system for clear rule composition
- **AI-Assisted Rule Creation**: Two approaches - interactive Skill or documentation-based
- **Code Excerpting**: Extractions of significant content to reduce context while preserving structure

## Learn More

- [User Guide](docs/user-guide.md) - Complete documentation
- [Design Philosophy](https://www.cyberchitta.cc/articles/llm-ctx-why.html)
- [Real-world Examples](https://www.cyberchitta.cc/articles/full-context-magic.html)

## License

Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
