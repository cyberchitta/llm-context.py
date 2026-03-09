# Primitive Rule Patterns

Use the smallest primitive vocabulary that can express the task cleanly.

The grounded examples in this repo point to five core primitives and one common project-local primitive.

## Core Primitives

### `lc/flt-no-files`

Start from nothing.

Use when:
- the task is surgical
- you know the likely files
- you want exact control over `full-files` and `excerpted-files`

This should be the default starting point for many task rules.

### `lc/flt-base`

Start from a broad code-oriented baseline with standard noise removed.

Use when:
- the task spans a subsystem
- you do not yet know the exact files
- the repository is small enough that a broad baseline is still inspectable

Risk:
- can admit many unrelated files into `Full files`
- must be verified with `lc-preview`

### `lc/flt-no-full`

Suppress all full-file selection.

Use when:
- you want structure only
- you are surveying a subsystem before deciding what needs full content
- you want an excerpt-heavy context

### `lc/flt-no-outline`

Suppress all excerpted-file selection.

Use when:
- you want only exact file bodies
- excerpting would add noise
- the selected set is already very small

### `lc/exc-base`

Standard excerpting behavior.

Use when:
- any file may need to be excerpted
- you want the normal code-outliner / markdown / SFC behavior

This is the standard excerpter primitive and should usually be composed into task rules.

## Common Project-Local Primitive

### `flt-repo-base`

Repository-specific baseline filter.

This is not a system primitive. It should live in `.llm-context/rules/` and capture local exclusions such as:
- docs that are rarely needed
- tests that should not be included by default
- generated sources
- project-specific resource folders

Use when:
- the repository has stable local noise that should be excluded by default
- multiple task rules need the same repo-specific baseline

Risk:
- if this primitive is too broad, many task rules will silently over-select
- `lc-preview` must confirm that it behaves as intended

## Minimal Composition Recipes

### 1. Surgical change

Use this for tasks like improving `lc-preview` formatting.

```yaml
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<edit-targets>..."
  excerpted-files:
    - "/<supporting-context>..."
```

### 2. Surgical change with exact bodies only

Use when excerpting adds no value.

```yaml
compose:
  filters: [lc/flt-no-files, lc/flt-no-outline]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<edit-targets>..."
```

### 3. Broad local baseline plus targeted additions

Use when the repo already has a reliable `flt-repo-base`.

```yaml
compose:
  filters: [flt-repo-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<edit-targets>..."
  excerpted-files:
    - "/<supporting-context>..."
```

### 4. Broad baseline but full-file bias

Use when you are editing docs, rules, or templates and excerpting is not helpful for the main target set.

```yaml
compose:
  filters: [flt-repo-base, lc/flt-no-outline]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/<primary-files>..."
```

### 5. Broad baseline but excerpt-only survey

Use before narrowing a task rule.

```yaml
compose:
  filters: [flt-repo-base, lc/flt-no-full]
  excerpters: [lc/exc-base]
also-include:
  excerpted-files:
    - "/<area-to-survey>..."
```

## Heuristics from Real Tasks

From the `lc-preview` task:
- start with `lc/flt-no-files`
- list edit targets in `full-files`
- keep selection internals in `excerpted-files`
- do not use a repo baseline unless preview proves it stays tight

From the primitive-rule-docs task:
- a repo baseline can be useful, but only if `lc-preview` shows it does not drag in unrelated files
- if preview expands too far, fall back to `lc/flt-no-files`

From the markdown-excerpter task:
- a changed file and its direct test usually belong in `full-files`
- neighboring infrastructure often belongs in `excerpted-files`

## Verification Checklist

After writing a rule, run `lc-preview` and check:

1. Are all intended edit targets in `Full files`?
2. Did anything unrelated leak into `Full files`?
3. Are support files in `Excerpted files` rather than `Full files`?
4. Is the baseline primitive too broad for this task?

If the answer to 2 or 4 is yes, narrow the primitive composition before changing the file lists.
