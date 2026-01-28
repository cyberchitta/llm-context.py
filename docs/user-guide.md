# LLM Context User Guide

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Workflow](#core-workflow)
3. [Rule System](#rule-system)
4. [AI-Assisted Rule Creation](#ai-assisted-rule-creation)
5. [Integration Options](#integration-options)
6. [Command Reference](#command-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Installation & Setup

### Prerequisites

- Python 3.10+
- Project with `.gitignore` file

### Installation

```bash
uv tool install "llm-context>=0.5.0"
```

### Project Initialization

```bash
cd /path/to/your/project
lc-init
```

Creates `.llm-context/` directory with default configuration and rules.

## Core Workflow

### Human Workflow (Daily Development)

```bash
# 1. Select files (smart defaults based on active rule)
lc-select

# 2. Generate context
lc-context     # For MCP environments
lc-context -nt # For manual workflows

# 3. Paste into AI chat

# 4. AI can access additional files via MCP as needed
```

### Agent Workflow (Context Provisioning)

**CLI (Claude Code, Cursor, etc.):**
```bash
# Validate rule effectiveness
lc-preview tmp-prm-auth

# Generate focused context
lc-context tmp-prm-auth
```

**MCP (Chat interfaces):**
```python
# Validate rule
preview = lc_preview(root_path, rule_name)

# Generate context
context = lc_outlines(root_path)

# Fetch additional files
files = lc_missing(root_path, "f", "['/proj/file.py']", timestamp)
```

## Rule System

### Systematic Organization

Rules use a five-category system with kebab-case prefixes:

- **Prompt Rules (`prm-`)**: Generate project contexts
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion
- **Instruction Rules (`ins-`)**: Provide guidance and frameworks
- **Style Rules (`sty-`)**: Enforce coding standards
- **Excerpt Rules (`exc-`)**: Configure content extraction

### Rule Structure

Rules are Markdown files with YAML frontmatter:

```yaml
---
description: "Brief description"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, custom-filters]
  excerpters: [lc/exc-base]
gitignores:
  full-files: ["*.tmp", "/build"]
also-include:
  full-files: ["/important.config"]
overview: "full" # or "focused"
---
## Rule Content
Markdown content providing additional context.
```

### Key Built-in Rules

**Prompt Rules:**
- `lc/prm-developer` - Standard development context
- `lc/prm-rule-create` - Full context for rule creation

**Filter Rules:**
- `lc/flt-base` - Standard exclusions (binaries, build artifacts)
- `lc/flt-no-files` - Exclude everything (use with `also-include`)
- `lc/flt-no-full` - Exclude all full files
- `lc/flt-no-outline` - Exclude all excerpted files

**Instruction Rules:**
- `lc/ins-developer` - Developer persona and guidelines
- `lc/ins-rule-framework` - Rule creation framework
- `lc/ins-rule-intro` - Chat-based rule creation intro

**Style Rules:**
- `lc/sty-code` - Universal programming principles
- `lc/sty-python` - Python-specific guidelines
- `lc/sty-javascript` - JavaScript-specific guidelines

**Excerpt Rules:**
- `lc/exc-base` - Base excerpting configuration

### Rule Composition Patterns

**Standard Development:**
```yaml
---
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
  excerpters: [lc/exc-base]
---
```

**Focused Task:**
```yaml
---
description: "Debug authentication"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
```

**Code Structure Only:**
```yaml
---
description: "Review architecture"
compose:
  filters: [lc/flt-no-full]
  excerpters: [lc/exc-base]
also-include:
  excerpted-files: ["/src/**/*.py"]
---
```

### Path Format

All paths relative to project root, starting with `/`:

```yaml
# ✓ Correct
also-include:
  full-files: ["/src/main.py", "/config/**"]

# ✗ Wrong - includes project name
also-include:
  full-files: ["/myproject/src/main.py"]
```

**Pattern Examples:**
```yaml
also-include:
  full-files:
    - "/src/main.py"           # Specific file
    - "/config/**"             # Directory contents
    - "**/*.py"                # All Python files
    - "**/tests/**"            # Test directories anywhere
    - "**/*.{js,ts,jsx,tsx}"   # Multiple extensions
```

## AI-Assisted Rule Creation

Let AI analyze your codebase and create focused rules. Two approaches:

### Claude Skill (Interactive)

**Setup:**
```bash
lc-init  # Installs to ~/.claude/skills/
# Restart Claude Desktop or Claude Code
```

**Usage:**
```bash
# 1. Share project context (overview required)
lc-context

# 2. Paste into Claude, then ask:
# "Create a rule for refactoring authentication to JWT"
# "I need a rule to debug payment processing"
```

Claude examines your codebase via `lc-missing`, asks clarifying questions, and generates optimized rules saved to `.llm-context/rules/tmp-prm-<task>.md`.

**Skill Files** (progressively disclosed):
- `Skill.md` - Quick workflow and patterns
- `PATTERNS.md` - Common rule patterns
- `SYNTAX.md` - Detailed syntax reference
- `EXAMPLES.md` - Complete walkthroughs
- `TROUBLESHOOTING.md` - Problem solving

### Instruction Rules (Works Anywhere)

**Usage:**
```bash
# 1. Load framework
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. Paste into any LLM and describe task
# "I need a rule for adding OAuth integration"

# 3. Use generated rule
lc-set-rule tmp-prm-oauth
lc-select
lc-context
```

**Included:**
- `lc/ins-rule-intro` - Introduction and overview
- `lc/ins-rule-framework` - Complete decision framework

### Comparison

| Aspect           | Skill                          | Instruction Rules        |
| ---------------- | ------------------------------ | ------------------------ |
| **Setup**        | Automatic with `lc-init`       | Already available        |
| **Interaction**  | Interactive, examines files    | Static documentation     |
| **Best for**     | Claude Desktop/Code            | Any LLM, any environment |

Both require project context first. Both produce equivalent results.

### Naming Conventions

- **Temporary tasks**: `tmp-prm-<task>` (e.g., `tmp-prm-api-debug`)
- **Permanent project**: `prm-<name>` (e.g., `prm-code`, `prm-api`)
- **System rules**: `lc/<category>-<name>` (e.g., `lc/flt-base`)

## Integration Options

### MCP Integration (Recommended)

**Setup:**
```jsonc
// claude_desktop_config.json
{
  "mcpServers": {
    "llm-context": {
      "command": "uvx",
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

**Benefits:**
- AI accesses additional files automatically
- Track changes during conversation
- No manual file operations

**MCP Tools:**
- `lc_outlines` - Generate excerpted context
- `lc_preview` - Validate rule effectiveness
- `lc_missing` - Fetch files/implementations
- `lc_changed` - Track modifications

### Manual Workflow (Fallback)

When LLM requests additional files:
```bash
lc-missing -f "[file1, file2]" -t <timestamp>
lc-missing -i "[[file, def], ...]" -t <timestamp>
lc-missing -e "[file1, file2]" -t <timestamp>
```

### Deployment Patterns

| Pattern                    | Command              | Use Case            |
| -------------------------- | -------------------- | ------------------- |
| System Message             | `lc-context -p`      | AI Studio           |
| Single User Message        | `lc-context -p -m`   | Grok                |
| Separate Messages          | `lc-prompt` + `lc-context -m` | Flexible   |
| Project Files (included)   | `lc-context`         | Claude Projects     |
| Project Files (searchable) | `lc-context -m`      | Force into context  |

## Command Reference

### Core Commands

**lc-init**
```bash
lc-init  # Initialize project
```

**lc-set-rule**
```bash
lc-set-rule prm-code              # Custom rule
lc-set-rule lc/prm-developer      # System rule
lc-set-rule tmp-prm-my-task       # Temporary task
```

**lc-select**
```bash
lc-select  # Select files based on active rule
```

**lc-context**
```bash
lc-context           # Generate context (MCP optimized)
lc-context -p        # Include prompt
lc-context -u        # Include user notes
lc-context -m        # Separate message mode
lc-context -nt       # No tools (manual workflow)
lc-context -f out.md # Write to file
```

**lc-preview**
```bash
lc-preview prm-code           # Preview active rule
lc-preview tmp-prm-my-task    # Preview temporary rule
```

**lc-outlines**
```bash
lc-outlines  # Get code structure excerpts
```

### Utility Commands

**lc-missing**
```bash
lc-missing -f "[file1, file2]" -t <timestamp>           # Files
lc-missing -i "[[file, def], [file, def]]" -t <ts>      # Implementations
lc-missing -e "[file1, file2]" -t <timestamp>           # Excluded sections
```

**lc-changed**
```bash
lc-changed  # List modified files since last generation
```

**lc-prompt**
```bash
lc-prompt  # Generate instructions only
```

**lc-rule-instructions**
```bash
lc-rule-instructions  # Rule creation guidance
```

## Best Practices

### Rule Organization

**Permanent Rules** (`.llm-context/rules/`):
```
flt-repo-base.md    # Project-specific filters
prm-code.md         # General development
prm-api.md          # API-focused work
prm-frontend.md     # Frontend development
```

**Temporary Rules**:
```
tmp-prm-oauth-integration.md
tmp-prm-bug-investigation.md
tmp-prm-performance-debug.md
```

### Context Efficiency

**Typical Reductions:**
- Bug fixes: 70-90% reduction
- Feature development: 40-70% reduction
- Code review: 30-50% reduction
- Architecture changes: May need broader context

**Selection Strategy:**
- **Full content**: Files you'll modify, small configs, key logic
- **Excerpted content**: Large files where structure matters
- **Exclude**: Documentation (unless relevant), tests (unless debugging)

### Rule Composition

**Start with decisions:**
- Need guidelines? Include `lc/sty-*` rules
- Need minimal context? Start with `lc/flt-no-files`
- Need standard exclusions? Use `lc/flt-base`
- Need excerpting? Compose with `lc/exc-base`

**Layer compositions:**
```yaml
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
  excerpters: [lc/exc-base]
```

## Code Excerpting

Extracts structure while reducing tokens. Supports 15+ languages including C, C++, C#, Elixir, Go, Java, JavaScript, PHP, Python, Ruby, Rust, TypeScript, Vue, Svelte.

**Configuration:**
```yaml
compose:
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/main.py"]      # Complete content
  excerpted-files: ["/src/utils/**"] # Structure only
```

## Troubleshooting

### No files selected

- Check paths start with `/` without project name
- Verify composed rules exist (e.g., `lc/flt-base`)
- Try `lc-set-rule lc/prm-developer` to test defaults
- Validate YAML syntax

### Context too large

- Use `lc/flt-no-files` with selective `also-include`
- Add exclusions to rule's `gitignores`
- Switch to `overview: "focused"`
- Create focused rule with `tmp-prm-` prefix
- Use excerpting via `lc/exc-base`

### Rule composition errors

- Verify referenced rules exist
- Use correct category prefixes (`lc/flt-base`, not `lc/base`)
- Check rule names match filenames exactly

### MCP not working

- Restart Claude Desktop after config changes
- Verify `lc-mcp` exists: `which lc-mcp`
- Check Claude Desktop logs
- Use manual workflow: `lc-context -nt`

### Rule Debugging

```bash
cat .llm-context/curr_ctx.yaml  # See selected files
lc-changed                      # Check recent changes
lc-preview <rule>               # Validate rule selection
```

### Recovery

```bash
# Backup custom rules
cp -r .llm-context/rules/*.md /tmp/backup/

# Reset to defaults
rm -rf .llm-context
lc-init

# Restore custom rules
cp /tmp/backup/*.md .llm-context/rules/
```
