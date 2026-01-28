---
name: llm-context-rule-creator
description: Create optimized llm-context rules for specific tasks by analyzing codebase content and generating minimal file selection patterns
---

# Context Descriptor Creation

Create rules that define exactly what context is needed for a task—whether for a sub-agent or a chat conversation.

## Two Usage Modes

This skill works in two environments:

| Environment | Interface | When to Use |
|-------------|-----------|-------------|
| **Chat harness** (Claude.ai, etc.) | MCP tools | Creating context for the current conversation |
| **Agentic harness** (Claude Code, etc.) | CLI commands | Creating context to delegate to sub-agents |

The rule format is identical—only the commands differ.

## Why This Matters

When providing code context (to a sub-agent or yourself), curation is essential:

- **Too much:** Full codebase overwhelms the context window (thousands of files, millions of tokens)
- **Too little:** Missing information to complete the task
- **Wrong focus:** Irrelevant code obscures what matters

Rules solve this by describing: which files to include fully, which to excerpt (signatures/structure only), and what to exclude entirely.

## The Core Workflow

```
1. Understand the task
2. Explore the codebase (outlines, file reads)
3. Create a rule file
4. Validate the rule
5. Iterate until context is focused and complete
6. Generate and use the context
```

### CLI vs MCP Commands

| Step | CLI (Agentic) | MCP (Chat) |
|------|---------------|------------|
| Explore | `lc-outlines` | `lc_outlines` tool |
| Validate | `lc-preview <rule>` | `lc_preview` tool |
| Get context | `lc-context <rule>` | `lc_outlines` with rule + `lc_missing` |
| Check changes | `lc-changed` | `lc_changed` tool |
| Get files | `lc-missing -f '[paths]'` | `lc_missing` tool |

## Rule Basics

Rules are YAML frontmatter + markdown, saved to `.llm-context/rules/`:

```yaml
---
description: Refactor authentication to use JWT
compose:
  filters: [lc/flt-base]        # What to exclude
  excerpters: [lc/exc-base]     # How to excerpt
also-include:
  full-files:                   # Complete content
    - "/src/auth/**"
  excerpted-files:              # Structure/signatures only
    - "/src/api/routes/**"
---
## Task Context
The auth module needs migration from sessions to JWT tokens.
Focus on the middleware integration points.
```

Save as: `.llm-context/rules/tmp-prm-auth-jwt.md`

## Two Categories of Files

**Full files (5-15 typical):**
- Files to be modified
- Small configs
- Critical integration points

**Excerpted files (10-30 typical):**
- Related modules (need structure, not every line)
- Large files (only signatures/definitions)
- Dependencies and callers

Excerpting uses tree-sitter to extract function/class definitions, reducing a 500-line file to ~50 lines of signatures.

## Always Filter First

Without filters, you get thousands of files: build artifacts, node_modules, __pycache__, logs, etc.

```yaml
compose:
  filters: [lc/flt-base]  # Standard exclusions (binaries, logs, caches)
```

Check if the project has custom filters (e.g., `flt-repo-base`) and compose them:

```yaml
compose:
  filters: [flt-repo-base, lc/flt-base]
```

Then use `also-include` to add back specific files you need.

## Validating Your Rule

Use the preview command/tool to see what a rule selects:

**CLI:** `lc-preview tmp-prm-auth-jwt`
**MCP:** `lc_preview` tool with rule name

```
Rule: tmp-prm-auth-jwt
Composes: flt-repo-base → lc/flt-base

Full files (8):              12,400 bytes
  src/auth/handler.py         3,200 bytes
  src/auth/middleware.py      2,800 bytes
  ...

Excerpted files (15):         8,200 bytes (of 45,000)
  src/api/routes/user.py        420 bytes (of 2,800)
  src/api/routes/admin.py       380 bytes (of 3,100)
  ...

Total: 23 files, 20,600 bytes (~5k tokens)
```

This feedback lets you iterate:
- Too large? Move files from full to excerpted, add exclusions
- Missing something? Adjust patterns in `also-include`
- Wrong files? Check your filter composition

## Path Format

In rule patterns, paths start with `/`, relative to project root:

```yaml
# Correct patterns in rules
- "/src/auth/**"
- "/config/settings.yaml"
- "**/*.py"

# Wrong
- "src/auth/**"           # Missing leading /
- "/src/"                 # Directory, not file pattern
```

**Note:** In generated context and preview output, paths include the project directory name as a prefix (e.g., `/{project-name}/src/auth/handler.py`). This enables multi-project context composition—combining files from multiple projects without path conflicts.

## Sizing Guidelines

| Bytes | Tokens (~) | Use Case |
|-------|------------|----------|
| ~60KB | ~15k | Surgical fixes |
| ~140KB | ~35k | Feature additions |
| ~200KB | ~50k | Refactoring |
| ~320KB | ~80k | Large migrations |

Aim for the smallest context that includes everything needed.

## Quick Reference

**Minimal context (start here for small tasks):**
```yaml
compose:
  filters: [lc/flt-no-files]   # Exclude everything
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/specific/file.py"
```

**Standard task:**
```yaml
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<modify>/**"
  excerpted-files:
    - "/<context>/**"
```

**With project filters:**
```yaml
compose:
  filters: [flt-repo-base]  # Project-specific, composes lc/flt-base
  excerpters: [lc/exc-base]
```

## Command Reference

### CLI Commands (Agentic Harness)

| Command | Purpose |
|---------|---------|
| `lc-outlines` | See project structure (excerpted view) |
| `lc-preview <rule>` | Validate rule file selection |
| `lc-context <rule>` | Generate context for the rule |
| `lc-set-rule <rule>` | Set active rule |
| `lc-changed` | List files modified since last context |
| `lc-missing -f '[paths]' -t <ts>` | Get specific file contents |

### MCP Tools (Chat Harness)

| Tool | Purpose |
|------|---------|
| `lc_outlines` | See project structure (excerpted view) |
| `lc_preview` | Validate rule file selection |
| `lc_changed` | List files modified since last context |
| `lc_missing` | Get specific files, implementations, or excluded sections |
| `lc_rule_instructions` | Get rule creation documentation |

**Note:** In chat mode, use `lc_outlines` with a rule name to generate context, then `lc_missing` to retrieve full content for specific files as needed.

## File Naming

- `prm-<name>.md` - Permanent prompt rules
- `flt-<name>.md` - Reusable filter rules
- `tmp-prm-<name>.md` - Temporary task rules (delete after use)

---

**Detailed syntax:** SYNTAX.md
**Common patterns:** PATTERNS.md
**Examples:** EXAMPLES.md
**Troubleshooting:** TROUBLESHOOTING.md
