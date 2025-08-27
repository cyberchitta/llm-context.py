---
name: lc/ins-rule-framework
description: Provides a decision framework, semantics, and best practices for creating task-focused rules, including file selection patterns and composition guidelines. Use as core guidance for building custom rules for context generation.
---

## Decision Framework

Create task-focused rules by selecting the minimal set of files needed for your objective, using the following rule categories:

- **Prompt Rules (`prm-`)**: Generate project contexts (e.g., `lc/prm-developer` for code files, `lc/prm-rule-create` for rule creation tasks).
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion (e.g., `lc/flt-base` for standard exclusions, `lc/flt-no-files` for minimal contexts).
- **Instruction Rules (`ins-`)**: Provide guidance (e.g., `lc/ins-developer` for developer guidelines, `lc/ins-rule-intro` for chat-based rule creation).
- **Style Rules (`sty-`)**: Enforce coding standards (e.g., `lc/sty-python` for Python-specific style, `lc/sty-code` for universal principles).

### Quick Decision Guide

- **Need detailed code implementations?** → Use `lc/prm-developer` for full content or specific `also-include` patterns.
- **Need only code structure?** → Use `lc/flt-no-full` with `also-include` for outline files.
- **Need coding style guidelines?** → Include `lc/sty-code`, `lc/sty-python`, etc., for relevant languages.
- **Need minimal context (metadata/notes)?** → Use `lc/flt-no-files`.
- **Need rule creation guidance?** → Compose with `lc/ins-rule-intro` or this rule (`lc/ins-rule-framework`).

**Outline Support**: Only files with extensions `.c`, `.cc`, `.cpp`, `.cs`, `.el`, `.ex`, `.elm`, `.go`, `.java`, `.js`, `.mjs`, `.php`, `.py`, `.rb`, `.rs`, `.ts` are eligible for outline selection. Other file types are ignored in outline-files.

## Rule System Semantics

### File Selection

- **`also-include: {full-files: [...], outline-files: [...]}`**: Specify files for full content or outlines.
  - Example: Include specific files in full content or outlines for targeted tasks.
- **`implementations: [[file, definition], ...]`**: Extract specific function/class implementations (not supported for C/C++).
  - Example: `["/src/utils/helpers.js", "validateToken"]` to retrieve a specific function.

### Filtering (gitignore-style patterns)

- **`gitignores: {full-files: [...], outline-files: [...], overview-files: [...]}`**: Exclude files using patterns.
  - Use `lc/flt-base` for standard exclusions (e.g., binaries, logs).
  - Use `lc/flt-no-full` or `lc/flt-no-outline` to exclude all full or outline files.
- **`limit-to: {full-files: [...], outline-files: [...], overview-files: [...]}`**: Restrict selections to specific patterns.
  - Example: `["src/api/**"]` to limit to API-related files.

**Path Format**: Patterns must be relative to the project root, starting with `/` but excluding the project name:

- ✅ `"/src/components/**"` (correct relative path)
- ❌ `"/myproject/src/components/**"` (includes project name)
- ✅ `"/.llm-context/rules/**"` (correct for rule files)
- Valid patterns: `**/*.js` (all JavaScript files), `/src/main.py` (specific file), `**/tests/**` (all test files).

**Important**: `limit-to` and `also-include` must match file paths, not directories:

- ✅ `"src/**"` (matches all files in src)
- ❌ `"src/"` (directory pattern, won’t match files)

### Composition

- **`compose: {filters: [...], rules: [...]}`**: Combine rules for modular context generation.
  - **`filters`**: Merge `gitignores`, `limit-to`, and `also-include` from other `flt-` rules (e.g., `lc/flt-base` for defaults, `lc/flt-no-files` for minimal contexts).
  - **`rules`**: Concatenate content from other rules (e.g., `lc/ins-developer` for guidelines).
  - Example: Compose `lc/flt-base` with `lc/prm-developer` for code-focused contexts.

### Overview Modes

- **`overview: "full"`**: Default. Shows a complete directory tree with all files (✓ full, ○ outline, ✗ excluded). Use for comprehensive visibility.
- **`overview: "focused"`**: Groups directories, showing details only for those with included files. Use for large repositories (1000+ files) to reduce context size.

## Example Advanced Rule

```yaml
---
name: tmp-prm-api-debugging
description: Focused context for debugging API-related code, excluding tests
overview: full
compose:
  filters: [lc/flt-base]
gitignores:
  full-files: ["**/test/**", "**/*.test.*"]
limit-to:
  outline-files: ["/src/api/**", "/src/types/**"]
also-include:
  full-files: ["/src/api/auth.js"]
implementations:
  - ["/src/utils/helpers.js", "validateToken"]
---
```

This rule:

- Uses `lc/flt-base` for standard exclusions.
- Excludes test files from full content.
- Limits outlines to API and type files.
- Includes a specific auth file in full and a function implementation.

## Implementation

Create a new user rule in `.llm-context/rules/` using shell commands:

```bash
cat > .llm-context/rules/tmp-prm-task-name.md << 'EOF'
---
name: tmp-prm-task-name
description: Brief description of the task focus
overview: full
compose:
  filters: [lc/flt-no-files]
also-include:
  full-files:
    - "/path/to/file1.ext"
    - "/path/to/file2.ext"
  outline-files:
    - "/path/to/outline1.ext"
---
## Task-Specific Context
Add optional task-specific instructions here.
EOF
lc/set-rule tmp-prm-task-name
lc/sel-files
lc/sel-outlines
lc/context
```

## Best Practices

- **Start Minimal**: Use `lc/flt-no-files` or `lc/flt-no-full` to include only essential files.
- **Use Descriptive Names**: Prefix temporary user prompt rules with `tmp-prm-` (e.g., `tmp-prm-api-debug`) to indicate temporary contexts.
- **Leverage Categories**:
  - Use `prm-` rules (e.g., `lc/prm-developer`, `lc/prm-rule-create`) for task-specific contexts.
  - Use `flt-` rules (e.g., `lc/flt-base`) for precise file control.
  - Include `ins-` rules (e.g., `lc/ins-developer`) for developer guidelines.
  - Reference `sty-` rules (e.g., `lc/sty-python`) for style enforcement.
- **Document Choices**: Explain why files are included in the rule’s content section.
- **Iterate**: Refine rules in follow-up conversations based on task needs.
- **Prefer Full Overview**: Use `overview: "full"` unless the repository is very large (1000+ files).
- **Aim for Efficiency**: Target 10-50% of full project context size for optimal LLM performance.

**Goal**: Create focused, reusable rules that minimize context while maximizing task effectiveness.
