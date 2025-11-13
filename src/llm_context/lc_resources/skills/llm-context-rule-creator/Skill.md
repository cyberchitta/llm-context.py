---
name: llm-context-rule-creator
description: Create optimized llm-context rules for specific tasks by analyzing codebase content and generating minimal file selection patterns
---

# LLM Context Rule Creator

Create focused rules for specific development tasks.

## What Rules Do

Rules define which project files appear in LLM context. You specify **full files** (complete content) and **excerpted files** (structure/signatures only) to keep token usage reasonable. Without rules, you'd get thousands of files - build artifacts, dependencies, cache, etc. Rules filter and curate what matters for your task.

See **SYNTAX.md** for detailed field descriptions.

## Quick Workflow

1. **Understand task** - Extract goal, target files, scope
2. **Examine codebase** - Use `lc_outlines` and `lc_missing` to explore
3. **Determine filters** - Start with project defaults, check custom filters
4. **Select files** - 5-15 full, 10-30 excerpted
5. **Generate rule** - Use template with proper composition
6. **Estimate & save** - ~40k tokens target, save to `tmp-prm-<n>`

## Filtering is Critical

**Without filters, you get thousands of files** - build artifacts, dependencies, config noise, test data, etc. Always filter first.

**Start with project filters:**

- Check `.llm-context/rules/` for custom filters like `flt-repo-base`
- Use `lc/flt-base` as minimum (excludes binaries, logs, common noise)
- Compose filters in the `compose.filters` array

**Then refine with `also-include`:**

- After filtering removes unwanted files, use `also-include` to add back what you need
- This is much faster than dealing with thousands of irrelevant files

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
  filters: [lc/flt-base] # Always filter first to exclude noise
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
- **Always use filters** - never skip this step
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
