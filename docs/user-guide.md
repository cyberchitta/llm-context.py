# LLM Context User Guide

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Workflow](#core-workflow)
3. [Rule System](#rule-system)
4. [Integration Options](#integration-options)
5. [AI-Assisted Rule Creation](#ai-assisted-rule-creation)
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

### Daily Development Pattern

```bash
# 1. Select files (smart defaults)
lc-select
# 2. Generate context
lc-context # For MCP environments
lc-context -nt # For manual workflows
# 3. Paste into AI chat
# 4. AI can access additional files as needed
```

### Project Setup (One Time)

Most users create customized permanent rules:

```bash
# Project-specific filters
cat > .llm-context/rules/flt-repo.md << 'EOF'
---
description: "Repository-specific exclusions"
compose:
  filters: [lc/flt-base]
gitignores:
  full-files:
    - "*.md"
    - /tests
    - /node_modules
  excerpt-files:
    - "*.md"
    - /tests
---
EOF
# Main development rule
cat > .llm-context/rules/prm-code.md << 'EOF'
---
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo]
  excerpters: [lc/exc-base]
---
Additional project-specific guidelines and context.
EOF
```

## Rule System

### Systematic Organization

LLM Context uses a five-category rule system with kebab-case prefixes:

- **Prompt Rules (`prm-`)**: Generate project contexts
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion
- **Instruction Rules (`ins-`)**: Provide guidance and frameworks
- **Style Rules (`sty-`)**: Enforce coding standards
- **Excerpt Rules (`exc-`)**: Configure extractions of significant content for context reduction (generalizes outlining)

### Decision Framework

**Choose rule types based on your needs:**

- **Need detailed code implementations?** → Use `lc/prm-developer` for full content
- **Need only code structure?** → Use `lc/flt-no-full` with excerpt files
- **Need coding guidelines?** → Include `lc/sty-code`, `lc/sty-python` for relevant languages
- **Need minimal context?** → Use `lc/flt-no-files` with specific inclusions
- **Need rule creation help?** → Use `lc/prm-rule-create` with `lc/ins-rule-framework`
- **Need context reduction via extractions?** → Compose with `lc/exc-base` or custom exc- rules

### Rule Structure

Rules are Markdown files with YAML frontmatter:

```yaml
---
description: "Brief description"
instructions: [lc/ins-developer, lc/sty-python] # Compose instructions
compose:
  filters: [lc/flt-base, custom-filters] # File selection rules
  excerpters: [lc/exc-base] # Excerpt rules
gitignores: # Additional exclusions
  full-files: ["*.tmp"]
also-include: # Force include specific files
  full-files: ["/important.config"]
  excerpt-files: ["/large-file.py"]
excerpters: [code-outliner, sfc] # Specify excerpters
overview: "full" # "full" (default) or "focused"
---
## Rule Content
Markdown content providing additional context for the AI.
```

### Built-in System Rules

**Prompt Rules (`lc/prm-*`)**:

- `lc/prm-developer` - Standard development context
- `lc/prm-rule-create` - Full project context for rule creation
  **Filter Rules (`lc/flt-*`)**:
- `lc/flt-base` - Standard exclusions (binaries, build artifacts)
- `lc/flt-no-files` - Exclude everything (use with `also-include`)
- `lc/flt-no-full` - Exclude all full content files
- `lc/flt-no-outline` - Exclude all excerpt files
  **Instruction Rules (`lc/ins-*`)**:
- `lc/ins-developer` - Developer persona and guidelines
- `lc/ins-rule-framework` - Rule creation framework and best practices
- `lc/ins-rule-intro` - Chat-based rule creation introduction
  **Style Rules (`lc/sty-*`)**:
- `lc/sty-code` - Universal programming principles
- `lc/sty-python` - Python-specific guidelines
- `lc/sty-javascript` - JavaScript-specific guidelines
- `lc/sty-jupyter` - Jupyter notebook guidelines
  **Excerpt Rules (`lc/exc-*`)**:
- `lc/exc-base` - Base configuration for excerpting, using code-outliner and SFC excerpters for structure extraction without full implementations

### Rule Composition Patterns

**Standard Development Rule**:

```yaml
---
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
  excerpters: [lc/exc-base]
---
```

**Minimal Task Rule**:

```yaml
---
description: "Debug authentication issues"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
```

**Code Structure Rule**:

```yaml
---
description: "Review code structure"
compose:
  filters: [lc/flt-no-full]
  excerpters: [lc/exc-base]
also-include:
  excerpt-files: ["/src/**/*.py", "/src/**/*.js"]
---
```

### Path Format

All paths relative to project root, starting with `/`:

```yaml
# ✅ Correct
also-include:
  full-files: ["/src/main.py", "/config/**"]
# ❌ Wrong - includes project name
also-include:
  full-files: ["/myproject/src/main.py"]
```

**Pattern Examples**:

```yaml
also-include:
  full-files:
    - "/src/main.py" # Specific file
    - "/config/**" # Directory contents
    - "**/*.py" # All Python files
    - "**/tests/**" # Test directories anywhere
    - "**/*.{js,ts,jsx,tsx}" # Multiple extensions
```

## Integration Options

### MCP Integration (Recommended)

Provides seamless file access during AI conversations.

#### Setup

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

#### Common Use Cases

1. **Code Review**: "I've implemented the auth changes, can you review them?"

   - AI uses `lc-missing` to examine modified files
   - Provides feedback on completeness and correctness

2. **Additional Context**: "What about the database schema?"

   - AI accesses initially excluded files when discussion reveals their relevance

3. **Change Tracking**: "What files have we modified?"

   - AI uses `lc-changed` to track conversation changes

4. **Following References**: "Let me check the utility functions"

   - AI accesses files referenced during implementation discussions

#### MCP Tools

- `lc-missing` - Unified access to files, excerpts, implementations
- `lc-changed` - Track changes during conversation

## Integration Options

### Manual Workflow (Fallback)

For environments without MCP support:

```bash
# Generate context with file request instructions
lc-context -nt
# When AI requests additional files:
# 1. The AI will provide a full command in a fenced code block, like:
lc-missing -f "[file1, file2]" -t 1234567890.123456
```

# 2. Copy and run this command in your terminal

# 3. The output will be copied to your clipboard automatically

# 4. Paste the output back into the AI chat

The `-nt` flag optimizes context for manual workflows.

## AI-Assisted Rule Creation

Let AI help create focused, task-specific rules by analyzing your codebase.

### Method 1: Claude Skill (Recommended)

**Automatic Installation:**

The rule creator Skill is automatically installed when you run `lc-init`. It installs globally to `~/.claude/skills/llm-context-rule-creator/`, making it available across all your projects.

After first installation, restart Claude Code or Claude Desktop to activate.

**Usage:**

In any Claude conversation, simply describe your task:

```
"Create a rule for refactoring authentication to JWT"
"I need a rule to debug the payment processing system"
"Add rate limiting to API endpoints"
```

The Skill will:

1. Examine your codebase using MCP tools (`lc_outlines`, `lc_missing`)
2. Intelligently select relevant files (5-15 full, 10-30 excerpted)
3. Generate optimized rule configuration
4. Save to `.llm-context/rules/tmp-prm-<task-name>.md`
5. Provide instructions for using the rule

**Example Interaction:**

````
You: "Create a rule for adding rate limiting to our API"

Claude: I'll analyze your codebase and create a focused rule.

[Examines structure with lc_outlines]
[Checks middleware patterns with lc_missing]

Created rule 'tmp-prm-rate-limiting':

Full content (3 files):
- API middleware directory
- Routes configuration
- API config

Excerpted (12 files):
- Endpoint definitions
- Existing middleware examples

Implementations:
- rate_limit decorator from utils

Estimated: ~35k tokens

To use in a fresh chat:
```bash
lc-set-rule tmp-prm-rate-limiting
lc-select
lc-context
````

````

**Skill Updates:**

The Skill is automatically updated when you upgrade llm-context:

```bash
uv tool upgrade llm-context
# Skill updates on next lc-init or any lc command
# Restart Claude to use new version
````

### Method 2: Prompt-Based (Fallback)

For environments without Skills support (API, other LLMs):

```bash
# 1. Get full project context with rule creation framework
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. Describe task to AI
# "I need to add OAuth integration to the auth system"

# 3. AI generates focused rule using framework

# 4. Use the focused context
lc-set-rule tmp-prm-oauth-task
lc-select
lc-context
```

The AI follows the systematic framework from `lc/ins-rule-framework` to create rules with:

- Minimal file selection
- Appropriate composition
- Token budget awareness
- Proper path formatting

### Method 3: Manual Creation

For advanced users who prefer direct control:

```bash
cat > .llm-context/rules/tmp-prm-my-task.md << 'EOF'
---
description: My specific task
overview: full
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/path/to/modify/**"
  excerpted-files:
    - "/path/to/context/**"
---
## Task Context
Brief explanation of optimization focus.
EOF

lc-set-rule tmp-prm-my-task
lc-select
lc-context
```

### Comparison

| Method           | Setup     | Interaction             | Validation | Best For                    |
| ---------------- | --------- | ----------------------- | ---------- | --------------------------- |
| **Skill**        | Automatic | Interactive, multi-turn | Automatic  | Claude Desktop/Code users   |
| **Prompt-based** | None      | Single turn             | Manual     | API, other LLMs, automation |
| **Manual**       | None      | Direct editing          | Manual     | Power users, templates      |

### Naming Conventions

- **Temporary task rules**: Use `tmp-prm-` prefix (e.g., `tmp-prm-api-debug`)
- **Permanent project rules**: Use descriptive names with `prm-` prefix (e.g., `prm-code`, `prm-api`)
- **System rules**: Use `lc/` prefix with category (e.g., `lc/flt-base`, `lc/sty-python`)

### Skill Details

The Skill includes progressive documentation:

- **SKILL.md** - Core workflow (always loaded when relevant)
- **SYNTAX.md** - Detailed syntax reference (on demand)
- **PATTERNS.md** - Common rule patterns (on demand)
- **EXAMPLES.md** - Complete walkthroughs (on demand)
- **TROUBLESHOOTING.md** - Problem solving (on demand)

This progressive disclosure keeps context minimal while providing deep documentation when needed.

## Command Reference

### Core Commands

**lc-init**

```bash
lc-init # Initialize project
```

**lc-set-rule**

```bash
lc-set-rule prm-code # Switch to custom code rule
lc-set-rule lc/prm-developer # Use system developer rule
lc-set-rule lc/prm-rule-create # Switch to rule creation
lc-set-rule tmp-prm-my-task # Switch to temporary task rule
```

**lc-select**

```bash
lc-select # Select files based on current rule for full and excerpt content
```

**lc-context**

```bash
lc-context # Generate context (MCP optimized)
lc-context -p # Include prompt instructions
lc-context -u # Include user notes
lc-context -nt # No tools (manual workflow)
lc-context -f output.md # Write to file
```

### Utility Commands

**lc-missing**

```bash
lc-missing -f "[file1, file2]" -t <timestamp> # Process file requests
lc-missing -i "[[file, def], [file, def]]" -t <timestamp> # Process implementation requests
```

**lc-changed**

```bash
lc-changed # List files modified since last generation
```

**lc-prompt**

```bash
lc-prompt # Generate just instructions portion
```

**lc-rule-instructions**

```bash
lc-rule-instructions # Rule creation guidance
```

## Best Practices

### Rule Organization Strategy

**Permanent Rules** (most common):

```bash
# Project-specific base filters
.llm-context/rules/filters.md # extends lc/flt-base
# Main development rules
.llm-context/rules/code.md # general development
.llm-context/rules/api.md # API-focused work
.llm-context/rules/frontend.md # frontend development
```

**Temporary Rules** (specific tasks):

```bash
# Use tmp-prm- prefix for easy identification
.llm-context/rules/tmp-prm-oauth-integration.md
.llm-context/rules/tmp-prm-bug-investigation.md
.llm-context/rules/tmp-prm-performance-debug.md
```

### Rule Composition Best Practices

**Start with Framework Decision**:

- Need coding guidelines? Include `lc/sty-*` rules
- Need minimal context? Start with `lc/flt-no-files`
- Need standard exclusions? Use `lc/flt-base`
- Need development instructions? Include `lc/ins-developer`
- Need excerpting for code structure? Compose with `lc/exc-base`

**Layer Compositions**:

```yaml
# Build from multiple components
instructions: [lc/ins-developer, lc/sty-python, lc/sty-code]
compose:
  filters: [lc/flt-base, project-filters, no-tests]
  excerpters: [lc/exc-base]
```

**Use Categories Appropriately**:

```yaml
# Good: Clear separation of concerns
instructions: [lc/ins-developer] # Guidelines
compose:
  filters: [lc/flt-base] # File selection
  excerpters: [lc/exc-base] # Excerpt configuration
# Avoid: Mixing categories inappropriately
compose:
  filters: [lc/sty-python] # Style rule in filters
```

### Context Efficiency

**Typical Reductions by Task Type**:

- Bug fixes: 70-90% reduction
- Feature development: 40-70% reduction
- Code review: 30-50% reduction
- Architecture changes: May need broader context

**Selection Strategy**:

- **Full content**: Files you'll modify, small configs, key business logic
- **Excerpt content**: Large files where you need structure understanding
- **Exclude**: Documentation (unless relevant), tests (unless debugging), build artifacts

### Workflow Integration

**With MCP (Seamless)**:

```bash
lc-set-rule code
lc-select
lc-context # Paste into Claude
# Claude handles additional file access automatically
```

**Without MCP (Manual)**:

```bash
lc-set-rule code
lc-select
lc-context -nt # Includes file request instructions
# Use lc-missing for additional requests
```

**Project Knowledge Bases**:

```bash
lc-context # Clean context without instructions
```

## Code Excerpting

Extractions of significant content to reduce context while preserving structure (generalizes previous outlining functionality).
**Supported Languages**: C, C++, C#, Elixir, Elm, Go, Java, JavaScript, PHP, Python, Ruby, Rust, TypeScript, Svelte, Vue

**Usage**:

```bash
lc-select # Full and excerpt content files
lc-context
```

**Rule Configuration**:

```yaml
compose:
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/main.py"] # Complete content
  excerpt-files: ["/src/utils/**"] # Structure only
```

## Implementation Extraction

Extract specific functions/classes on demand.

**Usage**:

```bash
# The AI will provide a full command in a fenced code block, like:
lc-missing -i "[[path, name], ...]" -t 1234567890.123456 # Process AI requests for specific code (output copied to clipboard)
```

**Rule Configuration**:

```yaml
implementations:
  - ["/src/utils.js", "validateUser"]
  - ["/src/auth.js", "AuthManager"]
```

## Troubleshooting

### Common Issues

**No files selected**:

- Check paths start with `/` and don't include project name
- Verify rule composition references exist (e.g., `lc/flt-base`)
- Try `lc-set-rule lc/prm-developer` to test with system defaults
- Check YAML frontmatter syntax with validator

**Context too large**:

- Use `lc/flt-no-files` with selective `also-include`
- Add exclusions to rule's `gitignores`
- Switch to `overview: "focused"` for large repositories
- Create focused rule with `tmp-prm-` prefix
- Use excerpting to reduce content while keeping structure

**Rule composition errors**:

- Verify referenced rules exist (check `.llm-context/rules/` and system rules)
- Use correct category prefixes (`lc/flt-base`, not `lc/base`)
- Check rule names match filenames exactly (without .md extension)

**MCP not working**:

- Restart Claude Desktop after config changes
- Verify `lc-mcp` command exists: `which lc-mcp`
- Check Claude Desktop logs for errors
- Use manual workflow as fallback with `lc-context -nt`

### Rule Debugging

**Check Current Selection**:

```bash
cat .llm-context/curr_ctx.yaml # See selected files
lc-changed # Check recent changes
```

**Test System Rules**:

```bash
lc-set-rule lc/prm-developer # Test with known good rule
lc-select
```

**Validate Rule Syntax**:

- Use online YAML validator for frontmatter
- Check that all referenced rules exist
- Verify path patterns follow correct format

### Getting Help

1. `lc-rule-instructions` - Rule creation guidance from system
2. `lc-set-rule lc/prm-rule-create` - Full framework with examples
3. Check system rules in implementation for patterns
4. Use AI-assisted rule creation for complex cases

### Recovery

```bash
# Backup custom rules
cp -r .llm-context/rules/*.md /tmp/backup-rules/
# Reset to defaults
rm -rf .llm-context
lc-init
# Restore custom rules
cp /tmp/backup-rules/*.md .llm-context/rules/
```

### System Rule Reference

For development and troubleshooting, here are the current system rules:

**File Organization**: All system rules use `lc/` prefix with category indicators
**Categories**: `prm-` (prompts), `flt-` (filters), `ins-` (instructions), `sty-` (styles), `exc-` (excerpts)
**Composition**: System rules can be composed into user rules
**Updates**: System rules may be updated with new versions (user rules preserved)

Use `lc-set-rule lc/prm-rule-create` to get complete current documentation with examples.
