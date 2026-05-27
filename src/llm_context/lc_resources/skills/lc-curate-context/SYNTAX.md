# Rule Syntax Reference

Complete schema and field details for rule files.

## Full Schema

```yaml
---
description: "Task description (required)"

overview: full | focused        # Optional. Default: full. Tree-rendering mode.

compose:
  filters: [<filter-rules>]     # File exclusion rules
  excerpters: [<exc-rules>]     # Excerpt configuration (required)

instructions: [<ins-rules>]     # Optional: guidelines for the agent

gitignores:                     # Additional exclusions (additive)
  full-files: [<patterns>]
  excerpted-files: [<patterns>]
  overview-files: [<patterns>]

limit-to:                       # Restrict to only these patterns
  full-files: [<patterns>]
  excerpted-files: [<patterns>]

also-include:                   # Force include (bypasses filters)
  full-files: [<patterns>]
  excerpted-files: [<patterns>]

implementations:                # Extract specific definitions
  - [<file>, <name>]

excerpt-modes:                  # Override default excerpter
  <pattern>: <mode>

excerpt-config:                 # Excerpter settings
  <mode>: {<config>}
---
## Markdown Content
Task-specific context and instructions for the agent.
```

## Field Reference

### description (required)

One-line task description. Appears in rule listings.

```yaml
description: Add rate limiting to API endpoints
```

### overview

Controls the directory tree rendered into the generated context. Default: `full`.

```yaml
overview: full      # Complete tree, every file annotated (✓ full, E excerpted, ✗ excluded)
overview: focused   # Groups directories; expands only those with included files
```

Use `focused` for repositories where the full tree would dominate the output (1000+ files). The default `full` overview already lists every selected file, so the rule's markdown body should not re-enumerate them — see PATTERNS.md "Anti-Patterns".

### compose (required)

Merge other rules into this one.

```yaml
compose:
  filters: [lc/flt-base]        # Always include base filters
  excerpters: [lc/exc-base]     # Required for excerpting
```

**filters:** Combine gitignores, limit-to, also-include from composed rules.

**excerpters:** Combine excerpt-modes and excerpt-config. Always include `lc/exc-base`.

### gitignores

Exclude files matching patterns. Additive with composed filters.

```yaml
gitignores:
  full-files:
    - "**/test/**"
    - "*.generated.py"
  excerpted-files:
    - "*.md"
```

### limit-to

Only include files matching these patterns. **Warning:** Only the first `limit-to` per category is used in composition.

```yaml
limit-to:
  full-files: ["/src/api/**"]
  excerpted-files: ["/src/**"]
```

### also-include

Force include files, **bypassing all filters**. Use with caution.

```yaml
also-include:
  full-files:
    - "/src/auth/**"
    - "/config/settings.yaml"
  excerpted-files:
    - "/src/models/**"
```

**Warning:** `also-include` ignores gitignores. Be specific to avoid pulling in __pycache__, node_modules, etc.

### implementations

Extract specific function/class definitions from files.

```yaml
implementations:
  - ["/src/utils.py", "validate_token"]
  - ["/src/auth.py", "AuthManager"]
```

Useful when you need one function from a large file.

### instructions

Reference instruction/style rules to include in context.

```yaml
instructions: [lc/ins-developer, lc/sty-python]
```

**Note:** When `instructions` is set, markdown content in the rule file is ignored.

### excerpt-modes

Override the default excerpter for specific file patterns.

```yaml
excerpt-modes:
  "*.md": "markdown"
  "*.vue": "sfc"
```

Available modes: `code-outliner` (default for code), `markdown`, `sfc` (Vue/Svelte).

### excerpt-config

Configure excerpter behavior.

```yaml
excerpt-config:
  markdown:
    with-code-blocks: true
    with-lists: true
```

## Built-in Rules

### Filters

| Rule | Purpose |
|------|---------|
| `lc/flt-base` | Standard exclusions (binaries, logs, caches, deps) |
| `lc/flt-no-files` | Exclude everything (use with `also-include`) |
| `lc/flt-no-full` | No full-content files |
| `lc/flt-no-outline` | No excerpted files |

### Excerpters

| Rule | Purpose |
|------|---------|
| `lc/exc-base` | Code outlining for all supported languages |

### Instructions

| Rule | Purpose |
|------|---------|
| `lc/ins-developer` | General development guidelines |
| `lc/ins-rule-framework` | Full rule system documentation |

### Styles

| Rule | Purpose |
|------|---------|
| `lc/sty-code` | Universal code principles |
| `lc/sty-python` | Python-specific guidelines |
| `lc/sty-javascript` | JavaScript-specific guidelines |

## Path Format

In rule patterns, paths are relative to project root, starting with `/`:

```yaml
# Correct patterns in rules
"/src/file.py"              # Specific file
"/src/**/*.py"              # Glob pattern
"**/*.js"                   # Any depth

# Wrong
"src/file.py"               # Missing leading /
"/src/"                     # Directory (use /src/**)
```

**Output format:** In generated context and preview output, paths include the project directory name: `/{project-name}/src/file.py`. This enables combining context from multiple projects without path conflicts.

**Scope:** All pathspecs (`gitignores`, `limit-to`, `also-include`) are matched against files inside the project root. The selector never walks outside that root, so `../sibling-repo/foo.md` and absolute paths silently match nothing. For shared briefs that live in a sibling repo, inline the content into the rule's markdown body — see PATTERNS.md "Shared brief in sibling repo".

## Common Mistakes

### 1. Missing excerpters

```yaml
# Wrong - will fail
compose:
  filters: [lc/flt-base]

# Correct
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
```

### 2. also-include pulling in noise

```yaml
# Dangerous - gets __pycache__, etc.
also-include:
  full-files: ["/src/**"]

# Better - be specific
also-include:
  full-files: ["/src/auth/**", "/src/api/routes.py"]
```

### 3. Mixing instructions with markdown

```yaml
# Wrong - markdown will be ignored
instructions: [lc/ins-developer]
---
## This content is discarded!
```

Choose one: use `instructions` to compose, or write markdown directly.

### 4. YAML syntax errors

```yaml
# Wrong - unquoted glob
also-include:
  full-files:
    - /src/**/*.py

# Correct - quoted
also-include:
  full-files:
    - "/src/**/*.py"
```
