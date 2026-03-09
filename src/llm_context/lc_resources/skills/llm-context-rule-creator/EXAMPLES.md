# Worked Examples

These examples use real tasks from the `llm-context.py` repo so the choices stay grounded.

## Example 1: Improve `lc-preview` Verification

**Task:** show the exact selected full and excerpted file lists in `lc-preview`.

**Rule:**

```yaml
---
description: Improve lc-preview verification output
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/llm_context/context_preview.py"
    - "/src/llm_context/cli.py"
    - "/src/llm_context/commands.py"
    - "/src/llm_context/lc_resources/templates/lc/preview.j2"
  excerpted-files:
    - "/src/llm_context/context_generator.py"
    - "/src/llm_context/context_spec.py"
    - "/src/llm_context/file_selector.py"
    - "/src/llm_context/rule.py"
---
Make lc-preview show exact full and excerpted file membership for rule verification.
```

**Why this is minimal:**
- full: the files directly changed by the feature
- excerpted: supporting selection and rendering logic
- no repo baseline, so unrelated source files cannot leak in

**How to verify:**
- `lc-preview` should show exactly 4 full files and 4 excerpted files
- the template should be full, not excerpted
- selection internals should be excerpted, not full

## Example 2: Tighten Primitive Rule Composition

**Task:** improve the primitive rules and the skill docs that explain how to use them.

**Rule:**

```yaml
---
description: Improve primitive rules and skill guidance
compose:
  filters: [flt-repo-base, flt-no-excerpters]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/llm_context/lc_resources/skills/llm-context-rule-creator/*.md"
    - "/src/llm_context/lc_resources/rules/lc/*.md"
    - "/.llm-context/rules/*.md"
    - "/src/llm_context/rule.py"
    - "/src/llm_context/rule_parser.py"
  excerpted-files:
    - "/src/llm_context/context_spec.py"
    - "/src/llm_context/file_selector.py"
    - "/src/llm_context/commands.py"
---
Improve the primitive rule vocabulary and the skill instructions that teach agents how to compose and verify task rules.
```

**Why this may need iteration:**
- `flt-repo-base` can still admit more full files than expected
- `lc-preview` is required to confirm that rule mechanics did not pull in unrelated files
- if the full-file list grows too much, switch to `lc/flt-no-files`

## Example 3: Surgical Single-File Fix

**Task:** adjust markdown excerpt behavior in the markdown excerpter only.

**Rule:**

```yaml
---
description: Adjust markdown excerpt behavior
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/llm_context/excerpters/markdown.py"
    - "/tests/test_excerpt_languages.py"
  excerpted-files:
    - "/src/llm_context/excerpters/service.py"
    - "/src/llm_context/lc_resources/rules/lc/exc-base.md"
---
Adjust markdown excerpting while keeping context limited to markdown extraction logic and its tests.
```

**Why this is better than a broad repo filter:**
- the task is isolated
- the changed file and its test belong in full
- neighboring excerpting infrastructure only needs structural context
