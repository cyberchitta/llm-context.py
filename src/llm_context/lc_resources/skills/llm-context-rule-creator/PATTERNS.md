# Common Rule Patterns

Load this for pattern library and examples.

## Start with Filters

**Before selecting files to include, always determine what to exclude.** Every pattern here starts with appropriate filters. Check your project's custom filters first (e.g., `flt-repo-base` in llm-context), then compose with `lc/flt-base`.

---

## Refactoring Pattern

**When:** Changing implementation of existing system

```yaml
description: Refactor X to use Y
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<system-to-change>/**"
  excerpted-files:
    - "/<code-that-calls-it>/**"
    - "/<code-it-depends-on>/**"
gitignores:
  full-files:
    - "**/test/**" # Optional: additional exclusions
```

**Typical sizes:** 8-12 full, 15-25 excerpted, ~50k tokens

---

## Feature Addition Pattern

**When:** Adding new functionality

```yaml
description: Add feature Z
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<where-to-integrate>/**"
    - "/<new-code-location>/**"
  excerpted-files:
    - "/<similar-existing-features>/**"
implementations:
  - ["/<utilities>.py", "helper_function"]
```

**Typical sizes:** 5-10 full, 10-20 excerpted, ~35k tokens

---

## Debugging Pattern

**When:** Investigating issue in specific area

```yaml
description: Debug issue in X
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<problematic-code>/**"
    - "/<related-tests>/**"
  excerpted-files:
    - "/<calling-code>/**"
    - "/<dependencies>/**"
```

**Typical sizes:** 6-10 full, 8-15 excerpted, ~40k tokens

---

## Migration Pattern

**When:** Moving to new framework/library/pattern

```yaml
description: Migrate X to Y
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<old-implementation>/**"
    - "/<migration-entry-points>/**"
  excerpted-files:
    - "/<code-using-old-pattern>/**"
    - "/<new-pattern-examples>/**"
```

**Typical sizes:** 10-15 full, 20-30 excerpted, ~60k tokens

---

## Minimal/Surgical Pattern

**When:** Very specific, small scope task

```yaml
description: Quick fix for specific issue
compose:
  filters: [lc/flt-no-files] # Exclude everything, then be explicit
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/specific/file1.py"
    - "/specific/file2.py"
    - "/config/relevant.yaml"
implementations:
  - ["/utils/helpers.py", "specific_function"]
```

**Typical sizes:** 2-5 full, 0-3 excerpted, ~15k tokens

---

## Code Review Pattern

**When:** Reviewing changes in specific area

```yaml
description: Review changes to X
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<changed-files>/**"
  excerpted-files:
    - "/<related-code>/**"
    - "/<tests>/**"
```

**Typical sizes:** 8-12 full, 12-20 excerpted, ~45k tokens

---

## API Development Pattern

**When:** Working on API endpoints

```yaml
description: Develop/modify API endpoints
compose:
  filters: [lc/flt-base] # Filter first
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
```

**Typical sizes:** 10-15 full, 15-25 excerpted, ~55k tokens

---

## Testing Pattern

**When:** Writing/fixing tests for specific module

```yaml
description: Add tests for X
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<module-to-test>/**"
    - "/<test-files>/**"
  excerpted-files:
    - "/<existing-test-patterns>/**"
    - "/<test-utilities>/**"
```

**Typical sizes:** 8-10 full, 10-15 excerpted, ~40k tokens

---

## Performance Optimization Pattern

**When:** Optimizing specific bottleneck

```yaml
description: Optimize performance of X
compose:
  filters: [lc/flt-base] # Filter first
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<slow-code>/**"
    - "/<benchmarks>/**"
  excerpted-files:
    - "/<calling-code>/**"
    - "/<similar-optimized-code>/**"
```

**Typical sizes:** 6-8 full, 10-15 excerpted, ~35k tokens
