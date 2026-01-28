# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

**Smart context management for LLM development workflows.** Share relevant project files instantly through intelligent selection and rule-based filtering.

## The Problem

Getting the right context into LLM conversations is friction-heavy:

- Manually finding and copying relevant files wastes time
- Too much context hits token limits, too little misses important details
- AI requests for additional files require manual fetching
- Hard to track what changed during development sessions

## The Solution

llm-context provides focused, task-specific project context through composable rules.

**For humans using chat interfaces:**
```bash
lc-select   # Smart file selection
lc-context  # Copy formatted context to clipboard
# Paste and work - AI can access additional files via MCP
```

**For AI agents with CLI access:**
```bash
lc-preview tmp-prm-auth    # Validate rule selects right files
lc-context tmp-prm-auth    # Get focused context for sub-agent
```

**For AI agents in chat (MCP tools):**
- `lc_outlines` - Generate excerpted context from current rule
- `lc_preview` - Validate rule effectiveness before use
- `lc_missing` - Fetch specific files/implementations on demand

> **Note**: This project was developed in collaboration with several Claude Sonnets (3.5, 3.6, 3.7, 4.0) and Groks (3, 4), using LLM Context itself to share code during development. All code is heavily human-curated by @restlessronin.

## Installation

```bash
uv tool install "llm-context>=0.5.0"
```

## Quick Start

### Human Workflow (Clipboard)

```bash
# One-time setup
cd your-project
lc-init

# Daily usage
lc-select
lc-context
# Paste into your LLM chat
```

### MCP Integration (Recommended)

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

Restart Claude Desktop. Now AI can access additional files during conversations without manual copying.

### Agent Workflow (CLI)

AI agents with shell access use llm-context to create focused contexts:

```bash
# Agent explores codebase
lc-outlines

# Agent creates focused rule for specific task
# (via Skill or lc-rule-instructions)

# Agent validates rule
lc-preview tmp-prm-oauth-task

# Agent uses context for sub-task
lc-context tmp-prm-oauth-task
```

### Agent Workflow (MCP)

AI agents in chat environments use MCP tools:

```bash
# Explore codebase structure
lc_outlines(root_path, rule_name)

# Validate rule effectiveness  
lc_preview(root_path, rule_name)

# Fetch specific files/implementations
lc_missing(root_path, param_type, data, timestamp)
```

## Core Concepts

### Rules: Task-Specific Context Descriptors

Rules are YAML+Markdown files that describe what context to provide for a task:

```yaml
---
description: "Debug API authentication"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
Focus on authentication system and related tests.
```

### Five Rule Categories

- **Prompt Rules (`prm-`)**: Generate project contexts (e.g., `lc/prm-developer`)
- **Filter Rules (`flt-`)**: Control file inclusion (e.g., `lc/flt-base`, `lc/flt-no-files`)
- **Instruction Rules (`ins-`)**: Provide guidelines (e.g., `lc/ins-developer`)
- **Style Rules (`sty-`)**: Enforce coding standards (e.g., `lc/sty-python`)
- **Excerpt Rules (`exc-`)**: Configure content extraction (e.g., `lc/exc-base`)

### Rule Composition

Build complex rules from simpler ones:

```yaml
---
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
  excerpters: [lc/exc-base]
---
```

## Essential Commands

| Command              | Purpose                                  |
| -------------------- | ---------------------------------------- |
| `lc-init`            | Initialize project configuration         |
| `lc-select`          | Select files based on current rule       |
| `lc-context`         | Generate and copy context                |
| `lc-context -p`      | Include prompt instructions              |
| `lc-context -m`      | Format as separate message               |
| `lc-context -nt`     | No tools (manual workflow)               |
| `lc-set-rule <name>` | Switch active rule                       |
| `lc-preview <rule>`  | Validate rule selection and size         |
| `lc-outlines`        | Get code structure excerpts              |
| `lc-missing`         | Fetch files/implementations (manual MCP) |

## AI-Assisted Rule Creation

Let AI help create focused, task-specific rules. Two approaches depending on your environment:

### Claude Skill (Interactive, Claude Desktop/Code)

**How it works**: Global skill guides you through creating rules interactively. Examines your codebase as needed using MCP tools.

**Setup**:
```bash
lc-init  # Installs skill to ~/.claude/skills/
# Restart Claude Desktop or Claude Code
```

**Usage**:
```bash
# 1. Share project context
lc-context  # Any rule - overview included

# 2. Paste into Claude, then ask:
# "Create a rule for refactoring authentication to JWT"
# "I need a rule to debug the payment processing"
```

Claude will:
1. Use project overview already in context
2. Examine specific files via `lc-missing` as needed
3. Ask clarifying questions about scope
4. Generate optimized rule (`tmp-prm-<task>.md`)
5. Provide validation instructions

**Skill documentation** (progressively disclosed):
- `Skill.md` - Quick workflow, decision patterns
- `PATTERNS.md` - Common rule patterns
- `SYNTAX.md` - Detailed reference
- `EXAMPLES.md` - Complete walkthroughs
- `TROUBLESHOOTING.md` - Problem solving

### Instruction Rules (Works Anywhere)

**How it works**: Load comprehensive rule-creation documentation into context, work with any LLM.

**Usage**:
```bash
# 1. Load framework
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. Paste into any LLM
# "I need a rule for adding OAuth integration"

# 3. LLM generates focused rule using framework

# 4. Use the new rule
lc-set-rule tmp-prm-oauth
lc-select
lc-context
```

**Included documentation**:
- `lc/ins-rule-intro` - Introduction and overview
- `lc/ins-rule-framework` - Complete decision framework

### Comparison

| Aspect                    | Skill                           | Instruction Rules        |
| ------------------------- | ------------------------------- | ------------------------ |
| **Setup**                 | Automatic with `lc-init`        | Already available        |
| **Interaction**           | Interactive, uses `lc-missing`  | Static documentation     |
| **File examination**      | Automatic via MCP               | Manual or via AI         |
| **Best for**              | Claude Desktop/Code             | Any LLM, any environment |
| **Updates**               | Automatic with version upgrades | Built-in to rules        |

Both require sharing project context first. Both produce equivalent results.

## Project Customization

### Create Base Filters

```bash
cat > .llm-context/rules/flt-repo-base.md << 'EOF'
---
description: "Repository-specific exclusions"
compose:
  filters: [lc/flt-base]
gitignores:
  full-files: ["*.md", "/tests", "/node_modules"]
  excerpted-files: ["*.md", "/tests"]
---
EOF
```

### Create Development Rule

```bash
cat > .llm-context/rules/prm-code.md << 'EOF'
---
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo-base]
  excerpters: [lc/exc-base]
---
Additional project-specific guidelines and context.
EOF

lc-set-rule prm-code
```

## Deployment Patterns

Choose format based on your LLM environment:

| Pattern               | Command          | Use Case                  |
| --------------------- | ---------------- | ------------------------- |
| System Message        | `lc-context -p`  | AI Studio, etc.           |
| Single User Message   | `lc-context -p -m` | Grok, etc.              |
| Separate Messages     | `lc-prompt` + `lc-context -m` | Flexible placement |
| Project Files (included) | `lc-context`  | Claude Projects, etc.     |
| Project Files (searchable) | `lc-context -m` | Force into context     |

See [Deployment Patterns](docs/user-guide.md#deployment-patterns) for details.

## Key Features

- **Intelligent Selection**: Rules automatically include/exclude appropriate files
- **Context Validation**: Preview size and selection before generation
- **Code Excerpting**: Extract structure while reducing tokens (15+ languages)
- **MCP Integration**: AI accesses additional files without manual intervention
- **Composable Rules**: Build complex contexts from reusable patterns
- **AI-Assisted Creation**: Interactive skill or documentation-based approaches
- **Agent-Friendly**: CLI and MCP interfaces for autonomous operation

## Common Workflows

### Daily Development (Human)

```bash
lc-set-rule prm-code
lc-select
lc-context
# Paste into chat - AI accesses more files via MCP if needed
```

### Focused Task (Human or Agent)

```bash
# Share project context first
lc-context

# Then create focused rule:
# Via Skill: "Create a rule for [task]"
# Via Instructions: lc-set-rule lc/prm-rule-create && lc-context -nt

# Validate and use
lc-preview tmp-prm-task
lc-context tmp-prm-task
```

### Agent Context Provisioning (CLI)

```bash
# Agent validates rule effectiveness
lc-preview tmp-prm-refactor-auth

# Agent generates context for sub-agent
lc-context tmp-prm-refactor-auth > /tmp/context.md
# Sub-agent reads context and executes task
```

### Agent Context Provisioning (MCP)

```python
# Agent validates rule
preview = lc_preview(root_path="/path/to/project", rule_name="tmp-prm-task")

# Agent generates context
context = lc_outlines(root_path="/path/to/project")

# Agent fetches additional files as needed
files = lc_missing(root_path, "f", "['/proj/src/auth.py']", timestamp)
```

## Path Format

All paths use project-relative format with project name prefix:

```
/{project-name}/src/module/file.py
/{project-name}/tests/test_module.py
```

This enables multi-project context composition without path conflicts.

**In rules**, patterns are project-relative without the prefix:
```yaml
also-include:
  full-files:
    - "/src/auth/**"      # ✓ Correct
    - "/myproject/src/**" # ✗ Wrong - don't include project name
```

## Learn More

- **[User Guide](docs/user-guide.md)** - Complete documentation with examples
- **[Design Philosophy](https://www.cyberchitta.cc/articles/llm-ctx-why.html)** - Why llm-context exists
- **[Real-world Examples](https://www.cyberchitta.cc/articles/full-context-magic.html)** - Using full context effectively

## License

Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
