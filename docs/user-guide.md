# LLM Context User Guide

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Workflow](#core-workflow)
3. [Rule System](#rule-system)
4. [Integration Options](#integration-options)
5. [AI-Assisted Rule Creation](#ai-assisted-rule-creation)
6. [Command Reference](#command-reference)
7. [Best Practices](#best-practices)
8. [Experimental Features](#experimental-features)
9. [Troubleshooting](#troubleshooting)

## Installation & Setup

### Prerequisites

- Python 3.10+
- Project with `.gitignore` file

### Installation

```bash
uv tool install "llm-context>=0.4.0"
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
lc-sel-files

# 2. Generate context
lc-context          # For MCP environments
lc-context -nt      # For manual workflows

# 3. Paste into AI chat
# 4. AI can access additional files as needed
```

### Project Setup (One Time)

Most users create customized permanent rules:

```bash
# Project-specific filters
cat > .llm-context/rules/flt-repo.md << 'EOF'
---
name: flt-repo
description: "Repository-specific exclusions"
compose:
  filters: [lc/flt-base]
gitignores:
  full-files:
    - "*.md"
    - /tests
    - /node_modules
  outline-files:
    - "*.md"
    - /tests
---
EOF

# Main development rule
cat > .llm-context/rules/prm-code.md << 'EOF'
---
name: prm-code
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo]
---

Additional project-specific guidelines and context.
EOF
```

## Rule System

### Systematic Organization

LLM Context uses a four-category rule system with kebab-case prefixes:

- **Prompt Rules (`prm-`)**: Generate project contexts
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion
- **Instruction Rules (`ins-`)**: Provide guidance and frameworks
- **Style Rules (`sty-`)**: Enforce coding standards

### Decision Framework

**Choose rule types based on your needs:**

- **Need detailed code implementations?** → Use `lc/prm-developer` for full content
- **Need only code structure?** → Use `lc/flt-no-full` with outline files
- **Need coding guidelines?** → Include `lc/sty-code`, `lc/sty-python` for relevant languages
- **Need minimal context?** → Use `lc/flt-no-files` with specific inclusions
- **Need rule creation help?** → Use `lc/prm-rule-create` with `lc/ins-rule-framework`

### Rule Structure

Rules are Markdown files with YAML frontmatter:

```yaml
---
name: rule-name # Must match filename
description: "Brief description"
instructions: [lc/ins-developer, lc/sty-python] # Compose instructions
compose:
  filters: [lc/flt-base, custom-filters] # File selection rules
gitignores: # Additional exclusions
  full-files: ["*.tmp"]
also-include: # Force include specific files
  full-files: ["/important.config"]
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
- `lc/flt-no-outline` - Exclude all outline files

**Instruction Rules (`lc/ins-*`)**:

- `lc/ins-developer` - Developer persona and guidelines
- `lc/ins-rule-framework` - Rule creation framework and best practices
- `lc/ins-rule-intro` - Chat-based rule creation introduction

**Style Rules (`lc/sty-*`)**:

- `lc/sty-code` - Universal programming principles
- `lc/sty-python` - Python-specific guidelines
- `lc/sty-javascript` - JavaScript-specific guidelines
- `lc/sty-jupyter` - Jupyter notebook guidelines

### Rule Composition Patterns

**Standard Development Rule**:

```yaml
---
name: lc/prm-developer
description: "Main development rule"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
---
```

**Minimal Task Rule**:

```yaml
---
name: tmp-prm-auth-debug
description: "Debug authentication issues"
compose:
  filters: [lc/flt-no-files]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
```

**Code Structure Rule**:

```yaml
---
name: tmp-prm-code-review
description: "Review code structure"
compose:
  filters: [lc/flt-no-full]
also-include:
  outline-files: ["/src/**/*.py", "/src/**/*.js"]
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

   - AI uses `lc-get-files` to examine modified files
   - Provides feedback on completeness and correctness

2. **Additional Context**: "What about the database schema?"

   - AI accesses initially excluded files when discussion reveals their relevance

3. **Change Tracking**: "What files have we modified?"

   - AI uses `lc-list-modified-files` to track conversation changes

4. **Following References**: "Let me check the utility functions"

   - AI accesses files referenced during implementation discussions

#### MCP Tools

- `lc-get-files` - Direct file access
- `lc-list-modified-files` - Track changes during conversation
- Experimental: `lc-code-outlines`, `lc-get-implementations`

### Manual Workflow (Fallback)

For environments without MCP support:

```bash
# Generate context with file request instructions
lc-context -nt

# When AI requests additional files:
# 1. Copy file list from AI
# 2. Run: lc-clip-files
# 3. Paste result back to AI
```

The `-nt` flag optimizes context for manual workflows.

## AI-Assisted Rule Creation

For unusual tasks or new projects, let AI help create focused rules using the systematic framework.

### Process

```bash
# 1. Get full project context with rule creation framework
lc-set-rule lc/prm-rule-create
lc-sel-files
lc-context -nt

# 2. Describe task to AI
# "I need to add OAuth integration to the auth system"

# 3. AI generates focused rule using framework
# 4. Use the focused context
lc-set-rule tmp-prm-oauth-task
lc-sel-files
lc-context
```

### Framework-Based Rule Creation

The AI follows the systematic framework from `lc/ins-rule-framework`:

```yaml
---
name: tmp-prm-oauth-integration
description: "Add OAuth support to authentication system"
overview: full
compose:
  filters: [lc/flt-no-files]
also-include:
  full-files:
    - "/src/auth/**"
    - "/src/middleware/auth.js"
    - "/config/auth.js"
    - "/tests/auth/**"
implementations:
  - ["/src/utils/jwt.js", "validateToken"]
---
## OAuth Integration Context
Focus on existing auth patterns to maintain consistency when adding OAuth providers.
Check token validation, middleware integration, and configuration patterns.
```

### Naming Conventions

- **Temporary user rules**: Use `tmp-prm-` prefix (e.g., `tmp-prm-api-debug`)
- **Permanent user rules**: Use descriptive names with `prm-` prefix (e.g., `prm-code`, `prm-frontend`)
- **System rules**: Uses `lc/` prefix with category prefixes (e.g., `lc/flt-base`, `lc/sty-python`)

## Command Reference

### Core Commands

**lc-init**

```bash
lc-init                    # Initialize project
```

**lc-set-rule**

```bash
lc-set-rule prm-code                # Switch to custom code rule
lc-set-rule lc/prm-developer        # Use system developer rule
lc-set-rule lc/prm-rule-create      # Switch to rule creation
lc-set-rule tmp-prm-my-task         # Switch to temporary task rule
```

**lc-sel-files**

```bash
lc-sel-files               # Select files based on current rule
```

**lc-context**

```bash
lc-context                 # Generate context (MCP optimized)
lc-context -p              # Include prompt instructions
lc-context -u              # Include user notes
lc-context -nt             # No tools (manual workflow)
lc-context -f output.md    # Write to file
```

### Utility Commands

**lc-clip-files**

```bash
lc-clip-files              # Process file requests from clipboard
```

**lc-changed**

```bash
lc-changed                 # List files modified since last generation
```

**lc-prompt**

```bash
lc-prompt                  # Generate just instructions portion
```

**lc-focus-help**

```bash
lc-focus-help             # Rule creation guidance
```

## Best Practices

### Rule Organization Strategy

**Permanent Rules** (most common):

```bash
# Project-specific base filters
.llm-context/rules/filters.md      # extends lc/flt-base

# Main development rules
.llm-context/rules/code.md         # general development
.llm-context/rules/api.md          # API-focused work
.llm-context/rules/frontend.md     # frontend development
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

**Layer Compositions**:

```yaml
# Build from multiple components
instructions: [lc/ins-developer, lc/sty-python, lc/sty-code]
compose:
  filters: [lc/flt-base, project-filters, no-tests]
```

**Use Categories Appropriately**:

```yaml
# Good: Clear separation of concerns
instructions: [lc/ins-developer]  # Guidelines
compose:
  filters: [lc/flt-base]          # File selection

# Avoid: Mixing categories inappropriately
compose:
  filters: [lc/sty-python]       # Style rule in filters
```

### Context Efficiency

**Typical Reductions by Task Type**:

- Bug fixes: 70-90% reduction
- Feature development: 40-70% reduction
- Code review: 30-50% reduction
- Architecture changes: May need broader context

**Selection Strategy**:

- **Full content**: Files you'll modify, small configs, key business logic
- **Outline content**: Large files where you need structure understanding
- **Exclude**: Documentation (unless relevant), tests (unless debugging), build artifacts

### Workflow Integration

**With MCP (Seamless)**:

```bash
lc-set-rule code
lc-sel-files
lc-context                # Paste into Claude
# Claude handles additional file access automatically
```

**Without MCP (Manual)**:

```bash
lc-set-rule code
lc-sel-files
lc-context -nt            # Includes file request instructions
# Use lc-clip-files for additional requests
```

**Project Knowledge Bases**:

```bash
lc-context                # Clean context without instructions
```

## Experimental Features

> **Note**: Under development, may have usability issues.

### Code Outlining

Show structure without implementation details.

**Supported Languages**: C, C++, C#, Elixir, Elm, Go, Java, JavaScript, PHP, Python, Ruby, Rust, TypeScript

**Usage**:

```bash
lc-sel-files        # Full content files
lc-sel-outlines     # Additional structure-only files
lc-context
```

**Rule Configuration**:

```yaml
also-include:
  full-files: ["/src/main.py"] # Complete content
  outline-files: ["/src/utils/**"] # Structure only
```

### Implementation Extraction

Extract specific functions/classes on demand.

**Usage**:

```bash
lc-clip-implementations    # Process AI requests for specific code
```

**Rule Configuration**:

```yaml
implementations:
  - ["/src/utils.js", "validateUser"]
  - ["/src/auth.js", "AuthManager"]
```

**Expected Format for Manual Usage**:

```
/src/utils.js:validateUser
/src/auth.js:AuthManager
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
cat .llm-context/curr_ctx.yaml     # See selected files
lc-changed                         # Check recent changes
```

**Test System Rules**:

```bash
lc-set-rule lc/prm-developer       # Test with known good rule
lc-sel-files
```

**Validate Rule Syntax**:

- Use online YAML validator for frontmatter
- Check that all referenced rules exist
- Verify path patterns follow correct format

### Getting Help

1. `lc-focus-help` - Rule creation guidance from system
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
**Categories**: `prm-` (prompts), `flt-` (filters), `ins-` (instructions), `sty-` (styles)
**Composition**: System rules can be composed into user rules
**Updates**: System rules may be updated with new versions (user rules preserved)

Use `lc-set-rule lc/prm-rule-create` to get complete current documentation with examples.
