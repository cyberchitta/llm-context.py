# Common Rule Patterns

Templates for common agent delegation scenarios.

## Pattern Selection Guide

| Task Type | Pattern | Typical Size |
|-----------|---------|--------------|
| Fix a specific bug | Minimal | ~15k tokens |
| Add a feature | Feature Addition | ~35k tokens |
| Debug an issue | Debugging | ~40k tokens |
| Refactor code | Refactoring | ~50k tokens |
| Migrate to new pattern | Migration | ~60k tokens |
| Review changes | Code Review | ~45k tokens |

---

## Minimal Pattern

**When:** Small, focused task with known files.

```yaml
---
description: <specific task>
compose:
  filters: [lc/flt-no-files]    # Start with nothing
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/path/to/file1.py"
    - "/path/to/file2.py"
---
## Task
<Brief description of the specific change needed>
```

**Use when:**
- You know exactly which 2-5 files are involved
- Task is surgical (fix a bug, add a parameter)
- Minimal context reduces noise

---

## Feature Addition Pattern

**When:** Adding new functionality to existing codebase.

```yaml
---
description: Add <feature>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<integration-point>/**"
    - "/<new-code-location>/**"
  excerpted-files:
    - "/<similar-features>/**"
---
## Feature Context
<What the feature does, where it integrates, patterns to follow>
```

**File selection:**
- **Full:** Where new code goes + integration points
- **Excerpted:** Similar existing features (for patterns)

---

## Debugging Pattern

**When:** Investigating an issue in specific area.

```yaml
---
description: Debug <issue description>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<problem-area>/**"
    - "/<related-tests>/**"
  excerpted-files:
    - "/<callers>/**"
    - "/<dependencies>/**"
---
## Debug Context
<Symptoms, reproduction steps, suspected areas>
```

**File selection:**
- **Full:** Suspected problem code + relevant tests
- **Excerpted:** Code that calls or is called by problem area

---

## Refactoring Pattern

**When:** Changing implementation of existing system.

```yaml
---
description: Refactor <system> to <approach>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<code-to-change>/**"
  excerpted-files:
    - "/<callers>/**"
    - "/<dependencies>/**"
gitignores:
  full-files:
    - "**/test/**"           # Add tests later if needed
---
## Refactoring Context
<Current structure, target structure, constraints>
```

**File selection:**
- **Full:** All code being refactored
- **Excerpted:** Everything that uses or is used by that code

---

## Migration Pattern

**When:** Moving to new framework, library, or pattern.

```yaml
---
description: Migrate <system> from <old> to <new>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<old-implementation>/**"
    - "/<entry-points>/**"
  excerpted-files:
    - "/<code-using-old>/**"
    - "/<new-pattern-examples>/**"
---
## Migration Context
<Old approach, new approach, migration strategy>
```

**File selection:**
- **Full:** Old code to replace + entry points
- **Excerpted:** All usage sites + examples of new pattern

---

## Code Review Pattern

**When:** Reviewing changes for correctness and style.

```yaml
---
description: Review changes to <area>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<changed-files>/**"
  excerpted-files:
    - "/<related-code>/**"
    - "/<tests>/**"
---
## Review Context
<What changed, what to look for, standards to apply>
```

---

## API Development Pattern

**When:** Working on API endpoints.

```yaml
---
description: <API task description>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/api/routes/**"
    - "/src/api/middleware/**"
  excerpted-files:
    - "/src/models/**"
    - "/src/services/**"
implementations:
  - ["/src/utils/validators.py", "validate_request"]
---
## API Context
<Endpoint specifications, request/response formats>
```

---

## Testing Pattern

**When:** Writing or fixing tests.

```yaml
---
description: Add tests for <module>
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<module-to-test>/**"
    - "/<test-files>/**"
  excerpted-files:
    - "/<test-utilities>/**"
    - "/<similar-tests>/**"
---
## Testing Context
<What to test, coverage goals, testing patterns used>
```

---

## Composition Example

For projects with custom filters, compose them:

```yaml
---
description: <task>
compose:
  filters: [flt-repo-base]      # Project filter (includes lc/flt-base)
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<specific-files>/**"
---
```

Check `.llm-context/rules/` for available project filters like `flt-repo-base`.
