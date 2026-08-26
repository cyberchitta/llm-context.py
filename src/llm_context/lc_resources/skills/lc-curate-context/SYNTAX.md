# Rule Syntax Reference

## Schema

```yaml
---
description: "Task description (required)"

overview: full | focused        # Optional. Default: full. Tree-rendering mode.

compose:
  filters: [<filter-rules>]     # File exclusion rules
  excerpters: [<exc-rules>]     # Excerpt configuration (required)

instructions: [<ins-rules>]     # Optional. Discards this file's markdown body.

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
Task-specific instructions for the agent.
```

## Fields

**`description`** (required) — one line, shown in rule listings.

**`overview`** — controls the directory tree rendered into the context. Default `full`: every file listed and annotated. `focused`: directories holding zero selected files collapse to a one-line summary; any directory with at least one selected file is still listed in full. Use `focused` where the tree would otherwise dominate the output — large repos, or a narrow selection alongside big irrelevant asset or data directories. See PATTERNS.md recipe 7.

The tree is not an inventory of the repository. It is filtered by the repo's `.gitignore` files and by `gitignores.overview-files` before anything is marked `✗`. That same file set scopes `lc-preview`'s `Referenced but not selected` section, so a file excluded from the overview cannot be reported there either.

**`compose`** (required) — merge other rules in. `filters` combine `gitignores`, `limit-to`, and `also-include`; `excerpters` combine `excerpt-modes` and `excerpt-config`. Always include `lc/exc-base`.

```yaml
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
```

**`gitignores`** — exclude matching files. Additive with composed filters.

**`limit-to`** — include *only* matching files. Only the first `limit-to` per category survives composition, so define it in the rule itself rather than inheriting it.

**`also-include`** — force include, **bypassing all filters**, including gitignores. Be specific: `"/src/**"` will pull in `__pycache__` and `node_modules`.

**`implementations`** — extract named definitions rather than whole files.

```yaml
implementations:
  - ["/src/utils.py", "validate_token"]
```

**`instructions`** — compose instruction/style rules into the context. **Setting this discards the rule file's own markdown body.** Use one or the other.

**`excerpt-modes`** — override the excerpter per pattern. Modes: `code-outliner` (default for code), `markdown`, `sfc` (Vue/Svelte).

```yaml
excerpt-modes:
  "*.md": "markdown"
```

**`excerpt-config`** — per-excerpter settings.

```yaml
excerpt-config:
  markdown:
    with-code-blocks: true
```

## Built-in Rules

| Filters | |
|---|---|
| `lc/flt-base` | Standard exclusions (binaries, logs, caches, deps) |
| `lc/flt-no-files` | Exclude everything — use with `also-include` |
| `lc/flt-no-full` | No full-content files |
| `lc/flt-no-outline` | No excerpted files |

| Excerpters | |
|---|---|
| `lc/exc-base` | Code outlining for all supported languages |

| Instructions | |
|---|---|
| `lc/ins-developer` | General development guidelines |
| `lc/ins-rule-framework` | Full rule system documentation |

| Styles | |
|---|---|
| `lc/sty-code` | Universal code principles |
| `lc/sty-python` | Python-specific guidelines |
| `lc/sty-javascript` | JavaScript-specific guidelines |

## Path Format

Rule patterns are project-root-relative and start with `/`:

```yaml
"/src/file.py"     # specific file
"/src/**/*.py"     # glob
"**/*.js"          # any depth

"src/file.py"      # WRONG - missing leading /
"/src/"            # WRONG - directory; use /src/**
```

Quote every pattern — an unquoted `- /src/**/*.py` is a YAML error.

**Output paths differ from rule paths.** Preview listings and generated context prefix the project directory name: `/{project-name}/src/file.py`. This lets context from several projects combine without collision. `lc-missing` takes paths in the *output* form.

**Scope.** All pathspecs are matched against files inside the project root; the selector never walks outside it, so `../sibling-repo/foo.md` and absolute paths silently match nothing. For a shared brief in a sibling repo, see PATTERNS.md recipe 6.
