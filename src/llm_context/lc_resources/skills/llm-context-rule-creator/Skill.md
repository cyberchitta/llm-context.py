---
name: llm-context-rule-creator
description: Create optimized llm-context rules for specific tasks by analyzing codebase content and generating minimal file selection patterns
---

# LLM Context Rule Creator

Create focused rules for specific development tasks.

## Quick Workflow

1. **Understand task** - Extract goal, target files, scope
2. **Examine codebase** - Use `lc_outlines` and `lc_missing` to explore
3. **Select files** - 5-15 full, 10-30 excerpted
4. **Generate rule** - Use template with proper composition
5. **Estimate & save** - ~40k tokens target, save to `tmp-prm-<name>`

## File Selection Guide

**Full content (5-15 files):**

- Files to be modified
- Small configs
- Integration points

**Excerpted (10-30 files):**

- Related modules (structure only)
- Large files (signatures needed)
- Tests, dependencies

**Implementations:**

- Specific functions from large files

## Basic Template

```yaml
---
description: <one-line task>
overview: full
compose:
  filters: [lc/flt-base] # Standard exclusions
  excerpters: [lc/exc-base] # Required for outlining
also-include:
  full-files:
    - "/path/to/modify/**"
  excerpted-files:
    - "/path/to/context/**"
---
## Task Context
Brief explanation of optimization focus.
```

## Key Rules

- Paths start with `/`, no project name
- Always compose `lc/exc-base`
- Target 20-80k tokens
- Use `lc/flt-no-files` for minimal contexts
- Save as `tmp-prm-<task-name>`

## Tools to Use

- `lc_outlines(root_path)` - See structure
- `lc_missing(root_path, "f", [paths], timestamp)` - Examine files

## Quick Patterns

**Refactor:**

```yaml
full-files: ["/<target>/**"]
excerpted-files: ["/<callers>/**", "/<dependencies>/**"]
```

**Add Feature:**

```yaml
full-files: ["/<integration>/**", "/<new-code>/**"]
excerpted-files: ["/<similar-feature>/**"]
```

**Debug:**

```yaml
full-files: ["/<broken>/**", "/<tests>/**"]
excerpted-files: ["/<callers>/**"]
```

---

**For detailed syntax, see SYNTAX.md**  
**For more patterns, see PATTERNS.md**  
**For complete examples, see EXAMPLES.md**  
**For troubleshooting, see TROUBLESHOOTING.md**
