---
description: Provides a decision framework, semantics, and best practices for creating task-focused rules, including file selection patterns and composition guidelines. Use as core guidance for building custom rules for context generation.
---

## Decision Framework

Create task-focused rules by selecting the minimal set of files needed for your objective, using the following rule categories:

- **Prompt Rules (`prm-`)**: Generate project contexts (e.g., `lc/prm-developer` for code files, `lc/prm-rule-create` for rule creation tasks).
- **Filter Rules (`flt-`)**: Control file inclusion/exclusion (e.g., `lc/flt-base` for standard exclusions, `lc/flt-no-files` for minimal contexts).
- **Excerpting Rules (`exc-`)**: Configure code outlining and structure extraction (e.g., `lc/exc-base` for standard code outlining).
- **Instruction Rules (`ins-`)**: Provide guidance (e.g., `lc/ins-developer` for developer guidelines, `lc/ins-rule-intro` for chat-based rule creation).
- **Style Rules (`sty-`)**: Enforce coding standards (e.g., `lc/sty-python` for Python-specific style, `lc/sty-code` for universal principles).

### Quick Decision Guide

- **Need detailed code implementations?** → Use `lc/prm-developer` for full content or specific `also-include` patterns.
- **Need only code structure/outlines?** → Use `lc/flt-no-full` with `also-include` for excerpted files.
- **Need coding style guidelines?** → Include `lc/sty-code`, `lc/sty-python`, etc., for relevant languages.
- **Need minimal context (metadata/notes)?** → Use `lc/flt-no-files`.
- **Need precise file control over a small set?** → Use `lc/flt-no-files` with explicit `also-include` patterns.
- **Need rule creation guidance?** → Compose with `lc/ins-rule-intro` or this rule (`lc/ins-rule-framework`).

## Code Outlining & Excerpting System

The excerpting system provides structured views of your code through different modes:

### Code Outlining (Primary Mode)

**Files Supported**: `.c`, `.cc`, `.cpp`, `.cs`, `.el`, `.ex`, `.elm`, `.go`, `.java`, `.js`, `.mjs`, `.php`, `.py`, `.rb`, `.rs`, `.ts`

Code outlining extracts function/class definitions and key structural elements, showing:

- Function signatures with `█` markers for definitions
- Class declarations and methods
- Important structural code with `│` continuation markers
- Condensed view with `⋮...` for omitted sections

### SFC Excerpting (Single File Components)

**Files Supported**: `.svelte`, `.vue`

Extracts script sections from Single File Components while preserving structure:

- Always includes `<script>` sections
- Optionally includes `<style>` sections (configurable)
- Optionally includes template logic (configurable)
- Uses `⋮...` markers for excluded sections

### Advanced Excerpting Configuration

Control excerpting behavior through `excerpt-config`:

```yaml
excerpt-config:
  sfc:
    with-style: false # Exclude CSS/styling sections
    with-template: true # Include template markup
```

### Required Composition

**All rules must compose `lc/exc-base`** to enable code outlining functionality. The excerpting system requires excerpt-modes configuration - without it, selected files cannot be processed for structural views.

- Always include `compose: {excerpters: [lc/exc-base]}` in your rules
- Advanced users can customize `excerpt-modes` patterns if needed
- Rules without excerpt configuration will fail when processing excerpted files

## Rule System Semantics

### File Selection

- **`also-include: {full-files: [...], excerpted-files: [...]}`**: Specify files for full content or excerpts using root-relative paths (excluding project name).
  - Example: `["/nbs/03_clustering.md", "/src/**/*.py"]` to include specific files or patterns.
- **`implementations: [[file, definition], ...]`**: Extract specific function/class implementations.
  - Example: `["/src/utils/helpers.js", "validateToken"]` to retrieve a specific function.

### Filtering (gitignore-style patterns)

- **`gitignores: {full-files: [...], excerpted-files: [...], overview-files: [...]}`**: Exclude files using patterns.
  - Use `lc/flt-base` for standard exclusions (e.g., binaries, logs).
  - Use `lc/flt-no-full` or `lc/flt-no-outline` to exclude all full or excerpted files.
- **`limit-to: {full-files: [...], excerpted-files: [...], overview-files: [...]}`**: Restrict selections to specific patterns.
  - **Important**: When composing rules, only the first `limit-to` clause for each key is used. Subsequent clauses are ignored with a warning.
  - Example: `["src/api/**"]` to limit to API-related files.

**Path Format**: All patterns must be relative to project root, starting with `/` but excluding the project name:

- ✅ `"/src/components/**"` (correct relative path)
- ❌ `"/myproject/src/components/**"` (includes project name)
- ✅ `"/.llm-context/rules/**"` (correct for rule files)

**Important**: `limit-to` and `also-include` must match file paths, not directories:

- ✅ `"src/**"` (matches all files in src)
- ❌ `"src/"` (directory pattern, won't match files)

### Composition

- **`compose: {filters: [...], excerpters: [...]}`**: Combine rules for modular context generation.
  - **`filters`**: Merge `gitignores`, `limit-to`, and `also-include` from other `flt-` rules.
  - **`excerpters`**: Merge `excerpt-modes` and `excerpt-config` from `exc-` rules.
  - Example: Compose `lc/flt-base` + `lc/exc-base` for standard code outlining.

### Overview Modes

- **`overview: "full"`**: Default. Shows complete directory tree with all files (✓ full, E excerpted, ✗ excluded).
- **`overview: "focused"`**: Groups directories, showing details only for those with included files. Use for large repositories (1000+ files).

## Example Advanced Rule

```yaml
---
description: Focused context for debugging API-related code with SFC support
overview: full
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
gitignores:
  full-files: ["**/test/**", "**/*.test.*"]
limit-to:
  excerpted-files: ["/src/api/**", "/src/components/**"]
also-include:
  full-files: ["/src/api/auth.js"]
excerpt-modes:
  "**/*.svelte": "sfc"
excerpt-config:
  sfc:
    with-style: false
    with-template: true
implementations:
  - ["/src/utils/helpers.js", "validateToken"]
---
```

This rule:

- Uses standard exclusions and code outlining
- Excludes test files from full content
- Limits excerpts to API and component files
- Configures SFC excerpting for Svelte files
- Includes specific auth file and function implementation

## Implementation

Create a new user rule in `.llm-context/rules/`:

```bash
cat > .llm-context/rules/tmp-prm-task-name.md << 'EOF'
---
description: Brief description of the task focus
overview: full
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/path/to/file1.ext"
    - "/path/to/file2.ext"
  excerpted-files:
    - "/path/to/outline1.ext"
---
## Task-Specific Context
Add optional task-specific instructions here.
EOF
lc-set-rule tmp-prm-task-name
lc-select
lc-context
```

## Best Practices

- **Start Minimal**: Use `lc/flt-no-files` with explicit `also-include` for precise control, or compose with `lc/flt-base` for broader patterns.
- **Use Descriptive Names**: Prefix temporary rules with `tmp-prm-` (e.g., `tmp-prm-api-debug`).
- **Leverage Categories**:
  - Use `prm-` rules for task-specific contexts
  - Use `flt-` rules for file control
  - Use `exc-` rules for excerpting configuration
  - Include `ins-` rules for developer guidelines
  - Reference `sty-` rules for style enforcement
- **Configure Excerpting**: Use `lc/exc-base` for standard code outlining, customize `excerpt-modes` for specific file types.
- **Document Choices**: Explain why files are included in the rule's content section.
- **Iterate**: Refine rules based on task needs.
- **Prefer Full Overview**: Use `overview: "full"` unless repository is very large (1000+ files).
- **Aim for Efficiency**: Target 10-50% of full project context size for optimal performance.

**Goal**: Create focused, reusable rules that minimize context while maximizing task effectiveness through intelligent code outlining and excerpting.
