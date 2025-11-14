# LLM Context User Guide

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Workflow](#core-workflow)
3. [Deployment Patterns](#deployment-patterns)
4. [Rule System](#rule-system)
5. [Integration Options](#integration-options)
6. [AI-Assisted Rule Creation](#ai-assisted-rule-creation)
7. [Command Reference](#command-reference)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

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

## Deployment Patterns

There are four common ways to provide context to LLMs:

### Pattern 1: System Message (AI Studio, etc.)

- **Prompt**: System message
- **Context**: System message (same)
- **Query**: First user message
- **Command**: `lc-context -p`

### Pattern 2: Single User Message (Grok, etc.)

- **Prompt**: User message
- **Context**: User message (same)
- **Query**: Second user message
- **Command**: `lc-context -p -m`

### Pattern 3: Separate User Message

- **Prompt**: System/instruction area (use `lc-prompt`)
- **Context**: User message (separate)
- **Query**: Second user message
- **Command**: `lc-prompt` then `lc-context -m`

### Pattern 4a: Project/Files (Included in Context)

- **Prompt**: System/instruction area
- **Context**: Pasted into "Project" section as named text
- **Query**: First user message
- **Command**: `lc-context`

### Pattern 4b: Project/Files (Searchable)

- **Prompt**: System/instruction area
- **Context**: User message (separate, via search)
- **Query**: Second user message
- **Command**: `lc-context -m`

## Rule System

### Systematic Organization

LLM Context uses a five-category rule system with kebab-case prefixes:

- **Prompt Rules (`prm-`)**: Generate project contexts
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion
- **Instruction Rules (`ins-`)**: Provide guidance and frameworks
- **Style Rules (`sty-`)**: Enforce coding standards
- **Excerpt Rules (`exc-`)**: Configure extractions of significant content for context reduction

### Decision Framework

**Choose rule types based on your needs:**

- **Need detailed code implementations?** → Use `lc/prm-developer` for full content
- **Need only code structure?** → Use `lc/flt-no-full` with excerpt files
- **Need coding guidelines?** → Include `lc/sty-code`, `lc/sty-python` for relevant languages
- **Need minimal context?** → Use `lc/flt-no-files` with specific inclusions
- **Need rule creation help?** → Use AI-assisted approaches (see below)
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

- `lc/exc-base` - Base configuration for excerpting, using code-outliner and SFC excerpters for structure extraction

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

### MCP Integration (Recommended for Claude Desktop)

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

#### How It Works

MCP tools become available for the LLM to use during conversation:

- `lc-missing` - Unified access to files, excerpts, implementations
- `lc-changed` - Track changes during conversation

#### Common Use Cases

1. **Code Review**: "I've implemented the auth changes, can you review them?"
2. **Additional Context**: "What about the database schema?"
3. **Change Tracking**: "What files have we modified?"

### Manual Workflow (Fallback)

For environments without MCP support, when LLM requests additional files:

```bash
lc-missing -f "[file1, file2]" -t <timestamp>
```

## AI-Assisted Rule Creation

Let AI help create focused, task-specific rules by analyzing your codebase. There are two distinct approaches:

### Understanding the Two Pathways

LLM Context provides two different ways for AI to help you create rules:

**1. Global Claude Skill** (`llm-context-rule-creator`)

- **Scope**: Available in all Claude conversations, all projects
- **Location**: `~/.claude/skills/llm-context-rule-creator/`
- **Install**: Automatic with `lc-init` + Claude restart
- **Best for**: Claude Desktop/Code users who want interactive guidance
- **Requires**: Project context already shared via llm-context

**2. Project Instruction Rules** (`lc/ins-rule-framework`, `lc/ins-rule-intro`)

- **Scope**: Available within specific projects, in project-specific conversations
- **Location**: `.llm-context/rules/lc/` (part of project)
- **Install**: Already included, no setup needed
- **Best for**: Any LLM, any environment, systematic documentation
- **Requires**: Project context already shared via llm-context

Both approaches require sharing project context first and produce equivalent results - they're just suited to different workflows and environments.

### Method 1: Claude Skill (Interactive, Claude Desktop/Code)

**How it works**: A global Claude Skill helps you create rules interactively. It requires project context (overview + framework) already shared via llm-context, and uses `lc-missing` to examine specific files as needed for deeper analysis.

**Setup**:

```bash
lc-init  # Installs skill to ~/.claude/skills/
# Restart Claude Desktop or Claude Code to activate
```

**Workflow**:

```bash
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# 1. Share any project context (overview is required)
lc-context  # Can use any rule - overview will be included
# 2. Paste into Claude
# "Create a rule for refactoring authentication to JWT"
# "I need a rule to debug the payment processing system"
```

**Why context is required**: The Skill needs the project overview to understand your codebase structure. It will then use `lc-missing` to examine specific files as needed while developing the rule strategy.

Claude will:

1. Use the project overview and framework already in context
2. Use `lc-missing` to examine specific files as needed for deeper analysis
3. Ask clarifying questions about scope and focus
4. Intelligently select relevant files (typically 5-15 full, 10-30 excerpted)
5. Generate optimized rule configuration
6. Save to `.llm-context/rules/tmp-prm-<task-name>.md`
7. Provide instructions for testing and refining the rule

**Example Interaction**:

````
You: [Paste project context from lc-context]
"Create a rule for adding OAuth integration"

Claude: I see your auth system structure. Let me examine the existing auth patterns.

[Uses lc_missing to check auth.py implementation]
[Uses lc_missing to check OAuth library usage]

Created rule 'tmp-prm-oauth-integration':

Full content (4 files):
- /src/auth/** (existing auth system)
- /config/auth.yaml (auth configuration)
- /tests/auth/test_oauth.py (OAuth tests)

Excerpted (8 files):
- /src/api/routes/auth.py (auth endpoints)
- /src/models/user.py (user model)
- Dependencies and utilities

Estimated: ~40k tokens

To use this rule:
```bash
lc-set-rule tmp-prm-oauth-integration
lc-select
lc-context
```
````

**Skill Files** (progressively disclosed):

- `Skill.md` - Quick workflow and decision patterns (always loaded)
- `PATTERNS.md` - Common rule patterns (loaded when relevant)
- `SYNTAX.md` - Detailed syntax reference (on demand)
- `EXAMPLES.md` - Complete walkthroughs (on demand)
- `TROUBLESHOOTING.md` - Problem solving (on demand)

**Skill Updates**: Automatically updated when you upgrade llm-context.

```bash
uv tool upgrade llm-context
# Skill updates on next lc command
# Restart Claude to use new version
```

**Note on lc-outlines**: This is a separate command for extracting code structure/definitions. The Skill uses `lc-missing` for file examination, not `lc-outlines`.

### Method 2: Prompt-Based with Instruction Rules (Works Anywhere)

**How it works**: You load comprehensive rule-creation documentation into context, then work with any LLM to create rules. The documentation provides systematic frameworks without requiring interactive exploration.

**Setup**: No special setup - documentation is built-in to the project.

**Workflow**:

```bash
# 1. Load the rule creation framework into context
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. Paste into your LLM and describe your task
# The context includes:
# - ins-rule-intro: introduction and decision framework
# - ins-rule-framework: comprehensive semantics and best practices
# - All system rules for reference
# - Code examples

# 3. Work with the LLM to refine the rule

# 4. Use the generated rule
lc-set-rule tmp-prm-your-task
lc-select
lc-context
```

**Example Workflow**:

```bash
$ lc-set-rule lc/prm-rule-create
$ lc-select
$ lc-context -nt
# [Copies comprehensive rule creation framework to clipboard]

# Paste into your LLM:
# "I need a rule for debugging payment processing.
#  My project has /src/payments/**, /tests/**, and uses
#  Stripe integration in /src/integrations/stripe.py"

# LLM uses the framework to generate:
# - Decision about filters
# - File selection strategy
# - Rule configuration
# - Explanation of choices
```

**Documentation Included**:

- `lc/ins-rule-intro` - Introduction and overview
- `lc/ins-rule-framework` - Complete decision framework, semantics, best practices
- Reference to all system rules
- Code examples

### Method 3: Manual Creation (Power Users)

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

| Aspect                          | Skill                              | Instruction Rules        | Manual                 |
| ------------------------------- | ---------------------------------- | ------------------------ | ---------------------- |
| **Setup**                       | Automatic with `lc-init` + restart | Already available        | No setup               |
| **Requires pre-shared context** | Yes                                | Yes                      | No                     |
| **Interaction**                 | Interactive, uses `lc-missing`     | Static documentation     | Direct editing         |
| **Best for**                    | Claude Desktop/Code                | Any LLM, any environment | Power users, templates |
| **Learning curve**              | Gentle, conversational             | Comprehensive reference  | Steep                  |

### Naming Conventions

- **Temporary task rules**: Use `tmp-prm-` prefix (e.g., `tmp-prm-api-debug`, `tmp-prm-oauth-integration`)
- **Permanent project rules**: Use descriptive names with `prm-` prefix (e.g., `prm-code`, `prm-api`, `prm-frontend`)
- **System rules**: Use `lc/` prefix with category (e.g., `lc/flt-base`, `lc/sty-python`)

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
lc-context -m # Send context as separate message (defers query to next message)
lc-context -nt # No tools (manual workflow)
lc-context -p -m # Include prompt with separate message mode
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

## Code Excerpting

Extractions of significant content to reduce context while preserving structure.

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
lc-missing -i "[[path, name], ...]" -t 1234567890.123456 # Process AI requests for specific code
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

1. **For Skill-based rule creation**:

   - Share project context: `lc-context` (any rule)
   - Then ask Skill in Claude: "Create a rule for [your task]"

2. **For instruction-based rule creation**:

   - Load framework: `lc-set-rule lc/prm-rule-create && lc-context -nt`
   - Work with LLM using the documentation provided

3. **For manual troubleshooting**: Check system rules for implementation patterns

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
