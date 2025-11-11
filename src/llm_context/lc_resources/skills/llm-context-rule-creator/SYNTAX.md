# Rule Syntax Reference

Load this when you need detailed syntax information.

## Complete Schema

```yaml
---
description: "One-line task description (required)"
overview: "full" | "focused"  # Default: full
compose:
  filters: [<filter-rules>]   # File selection rules
  excerpters: [<exc-rules>]   # Outlining config (required)
instructions: [<ins-rules>]   # Optional guidelines
gitignores:                   # Additional exclusions
  full-files: [<patterns>]
  excerpted-files: [<patterns>]
  overview-files: [<patterns>]
limit-to:                     # Restrict to patterns
  full-files: [<patterns>]
  excerpted-files: [<patterns>]
also-include:                 # Force include
  full-files: [<patterns>]
  excerpted-files: [<patterns>]
implementations:              # Specific extractions
  - [<file>, <name>]
excerpt-modes:                # Override default outliner
  <pattern>: <mode>
excerpt-config:               # Excerpter settings
  <mode>: {<config>}
---
## Rule Content
Markdown providing task-specific context.
```

## Field Details

### compose

Merge rules together:

- `filters`: Combine gitignores, limit-to, also-include
- `excerpters`: Combine excerpt-modes, excerpt-config

**Always include:** `excerpters: [lc/exc-base]`

### gitignores

Exclude patterns (additive):

```yaml
gitignores:
  full-files: ["**/test/**", "*.tmp"]
  excerpted-files: ["*.md"]
```

### limit-to

**Warning:** Only first `limit-to` per key is used in composition.

```yaml
limit-to:
  full-files: ["/src/api/**"] # Only these files
```

### also-include

Force include despite filters:

```yaml
also-include:
  full-files: ["/important.config"]
  excerpted-files: ["/large-file.py"]
```

### implementations

Extract specific definitions:

```yaml
implementations:
  - ["/src/utils.js", "validateToken"]
  - ["/src/auth.js", "AuthManager"]
```

## Path Format Rules

✅ **Correct:**

- `/src/file.py` - Root-relative
- `/src/**/*.py` - Glob pattern
- `**/*.js` - Any depth

❌ **Wrong:**

- `/myproject/src/file.py` - Includes project name
- `src/file.py` - Missing leading slash
- `/src/` - Directory (match files: `/src/**`)

## System Rules Reference

**Filters:**

- `lc/flt-base` - Standard exclusions (binaries, logs, etc.)
- `lc/flt-no-files` - Exclude everything (use with also-include)
- `lc/flt-no-full` - No full content files
- `lc/flt-no-outline` - No excerpted files

**Excerpters:**

- `lc/exc-base` - Code outlining for all languages

**Instructions:**

- `lc/ins-developer` - Developer guidelines
- `lc/ins-rule-framework` - Full framework docs

**Styles:**

- `lc/sty-code` - Universal principles
- `lc/sty-python` - Python-specific
- `lc/sty-javascript` - JS-specific

## Composition Examples

**Minimal context:**

```yaml
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
```

**Standard + custom:**

```yaml
compose:
  filters: [lc/flt-base, my-project-filters]
  excerpters: [lc/exc-base]
instructions: [lc/ins-developer, lc/sty-python]
```
