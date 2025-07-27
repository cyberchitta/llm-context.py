---
name: lc-focus-common
description: Core reusable instructions for creating focused rules
---

## Decision Framework

Create task-focused rules by deciding what you need to see to complete the task:

**Full content:** Files you need to read/modify/understand in detail
**Outlined:** Files where you just need to know structure/what's available

### Quick Decision Guide:

- Will I need to see the actual implementation? → Full
- Do I just need to know what functions/classes exist? → Outline
- Is it small enough that full content doesn't add noise? → Full
- Is it large where outline gives me what I need? → Outline

## Rule System Semantics

### File Selection

- `also-include: {full_files: [...], outline_files: [...]}` - Include complete or outlined content
- `implementations: [[file, definition], ...]` - Extract specific functions/classes

### Filtering (gitignore-style patterns)

- `gitignores: {full_files: [...], outline_files: [...], overview_files: [...]}` - Exclude patterns
- `limit-to: {full_files: [...], outline_files: [...], overview_files: [...]}` - Restrict to patterns
- **All items are pathspecs** - Use `.gitignore` syntax: `**/*.test.js` for recursive patterns, `src/` for directories, `/path/file.ext` for specific files

**Important:** Both `limit-to` and `also-include` patterns must match **file paths**, not directory names:
- ✅ `"src/**"` - matches all files in src directory (only at project root)
- ✅ `"**/tests/**"` - matches files in any tests directory  
- ✅ `"**/*.js"` - matches JavaScript files anywhere
- ✅ `".llm-context/rules/**"` - matches files in nested .llm-context/rules directory
- ❌ `"src/"` - directory pattern, won't match files inside

### Composition

- `compose: {filters: [...], rules: [...]}` - Build from other rules
- `filters` - Merge gitignore/limit-to/also-include patterns
  - Use `lc-filters` when you want to add to the default inclusion set
  - Use `lc-no-files` when you want precise control (only specified files included)
- `rules` - Concatenate content from other rules

### Presentation

- `overview: "full"` - Complete directory tree
- `overview: "focused"` - Grouped by directory, showing all files in folders that contain any included files

### Example Advanced Rule

```yaml
---
name: api-debugging
description: "API debugging with test exclusions"
overview: "focused"
compose:
  filters: ["lc-filters"]
gitignores:
  full_files: ["**/test/**", "**/*.test.*"]
limit-to:
  outline_files: ["src/api/**", "src/types/**"]
also-include:
  full_files: ["/src/api/auth.js"]
implementations:
  - ["/src/utils/helpers.js", "validateToken"]
---
```

This creates reusable, composable rules that can be precisely tuned for different scenarios.

## Implementation

Generate the complete rule and save it using shell commands.

```bash
cat > .llm-context/rules/tmp-task-name.md << 'EOF'
---
name: tmp-task-name
description: "Brief description of what this focuses on"
overview: "focused"
compose:
  filters: ["lc-no-files"]
also-include:
  full_files:
    - "/path/to/file1.ext"
    - "/path/to/file2.ext"
  outline_files:
    - "/path/to/outline1.ext"
---

## Task-Specific Context
Optional: Additional context or instructions for this rule.
EOF

lc-set-rule tmp-task-name
lc-context
```

## Best Practices

- Start minimal and add only when necessary
- Use descriptive rule names (`tmp-` prefix for temporary rules)
- Document why each file was included
- Aim for 10-50% of full project context size
- Consider iterative refinement in follow-up conversations
- Use `overview: "focused"` for compact directory listings

The goal is creating the most efficient context for the specific task while maintaining comprehension.
