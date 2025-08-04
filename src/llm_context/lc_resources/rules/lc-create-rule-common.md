---
name: lc-create-rule-common
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

**Outline support:** `.c`, `.cc`, `.cpp`, `.cs`, `.el`, `.ex`, `.elm`, `.go`, `.java`, `.js`, `.mjs`, `.php`, `.py`, `.rb`, `.rs`, `.ts`

Files with these extensions are the only candidates for outline-files. Other file types will be ignored in outline selection.

## Rule System Semantics

### File Selection

- `also-include: {full-files: [...], outline-files: [...]}` - Include complete or outlined content
- `implementations: [[file, definition], ...]` - Extract specific functions/classes

### Filtering (gitignore-style patterns)

- `gitignores: {full-files: [...], outline-files: [...], overview_files: [...]}` - Exclude patterns
- `limit-to: {full-files: [...], outline-files: [...], overview_files: [...]}` - Restrict to patterns
- **All items are pathspecs** - Use `.gitignore` syntax: `**/*.test.js` for recursive patterns, `src/` for directories, `/path/file.ext` for specific files

**Path Format**: All pathspecs must be relative to the project root, starting with `/` but NOT including the project directory name:

- ✅ `"/src/components/**"` - correct relative path
- ❌ `"/myproject/src/components/**"` - includes project name
- ✅ `"/.llm-context/rules/lc-code.md"` - correct for root-level directories
- ❌ `"/myproject/.llm-context/rules/lc-code.md"` - includes project name

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

### Overview Modes

- `overview: "full"` - **Default choice** - Complete directory tree showing all files
  - Provides visibility into entire codebase for informed file selection
  - Essential when you might need files outside the initial focused context
- `overview: "focused"` - **Large repos only** - Grouped view showing only relevant directories
  - Use only when full overview would be too verbose (1000+ files)
  - Limits visibility but reduces context size significantly

### Example Advanced Rule

```yaml
---
name: api-debugging
description: "API debugging with test exclusions"
overview: "full"
compose:
  filters: ["lc-filters"]
gitignores:
  full-files: ["**/test/**", "**/*.test.*"]
limit-to:
  outline-files: ["src/api/**", "src/types/**"]
also-include:
  full-files: ["/src/api/auth.js"]
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
overview: "full"
compose:
  filters: ["lc-no-files"]
also-include:
  full-files:
    - "/path/to/file1.ext"
    - "/path/to/file2.ext"
  outline-files:
    - "/path/to/outline1.ext"
---

## Task-Specific Context
Optional: Additional context or instructions for this rule.
EOF

lc-set-rule tmp-task-name
lc-sel-files
lc-sel-outlines
lc-context
```

## Best Practices

- Start minimal and add only when necessary
- Use descriptive rule names (`tmp-` prefix for temporary rules)
- Document why each file was included
- Aim for 10-50% of full project context size
- Consider iterative refinement in follow-up conversations
- Use `overview: "full"` by default; only switch to `"focused"` for very large repositories

The goal is creating the most efficient context for the specific task while maintaining comprehension.
