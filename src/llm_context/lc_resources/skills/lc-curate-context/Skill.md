---
name: lc-curate-context
description: Create optimized llm-context rules for specific tasks by analyzing codebase content and generating minimal file selection patterns
---

# Context Descriptor Creation

Create rules that define the minimal sufficient context for a task.

The job is not to gather a lot of relevant code. The job is to produce the smallest full-file and excerpted-file set that is still enough to complete the task.

## Use This Workflow

1. Understand the task in concrete file terms.
2. Start from the narrowest sensible filter baseline.
3. Put files to edit in `full-files`.
4. Put callers, dependencies, and large reference files in `excerpted-files`.
5. Run `lc-preview`.
6. Read the exact `Full files` and `Excerpted files` lists.
7. Tighten until the selection is minimal and sufficient.
8. Before handing the rule off, actually generate output once: `lc-set-rule <rule>` → `lc-select` → `lc-context` (or `lc-prompt`). `lc-preview` computes its own selection on the fly and does not populate the state that `lc-context` reads from — see TROUBLESHOOTING.md "Preview Looks Right But Context Is Empty".

## Pick the Baseline First

Start narrow unless you have a good reason not to.

**Use `lc/flt-no-files` when:**
- the task is surgical
- you already know the likely files
- you want exact control over membership

**Use `flt-repo-base` or `lc/flt-base` when:**
- you need a broad project slice
- the task spans a subsystem
- the project already has a disciplined repo-level filter

If `lc-preview` shows many unexpected full files, your baseline is too broad.

## Full vs Excerpted

**Full files**
- files you expect to edit
- small configs or templates that directly control the behavior
- compact integration points where exact code matters

**Excerpted files**
- callers and dependencies
- large modules where structure is enough
- reference implementations and surrounding architecture

Move a file from excerpted to full only when the exact body matters.

## Verify with `lc-preview`

`lc-preview` is the main verification step.

Read it in this order:

1. `Summary`
2. `Full files`
3. `Excerpted files`

Ask:
- Are all expected edit targets in `Full files`?
- Did any unrelated files leak into `Full files`?
- Are context files in `Excerpted files` instead of `Full files`?
- Is the total selection small enough for the task?

Do not trust a rule until the exact file lists look right. Note that `lc-preview` looking right is not sufficient on its own — see step 8 above.

## Grounded Example 1: Improve `lc-preview`

Task: change preview formatting so it lists all selected full and excerpted files.

This is a narrow task. Start from `lc/flt-no-files`.

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

Why this shape:
- full: the command path and template being edited
- excerpted: supporting selection and rendering code for orientation
- narrow baseline: prevents accidental inclusion of most of the repo

What to look for in `lc-preview`:
- only those four edit targets in `Full files`
- supporting internals in `Excerpted files`
- no tests, docs, or unrelated resources unless intentionally added

## Grounded Example 2: Tighten Primitive Rules and Skill Guidance

Task: improve primitive rule composition and the skill docs that teach it.

This task is broader, but still needs discipline. Start from a repo filter only if it already excludes enough noise.

```yaml
---
description: Improve primitive rules and skill guidance
compose:
  filters: [flt-repo-base, flt-no-excerpters]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/llm_context/lc_resources/skills/lc-curate-context/*.md"
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

What to look for in `lc-preview`:
- all rule and skill docs appear in `Full files`
- supporting mechanics stay excerpted unless they are being changed
- repo-level defaults do not drag in unrelated source files

If preview expands too far, drop the repo baseline and switch to `lc/flt-no-files`.

## CLI and MCP Equivalents

| Step | CLI | MCP |
|------|-----|-----|
| Explore | `lc-outlines` | `lc_outlines` |
| Validate | `lc-preview <rule>` | `lc_preview` |
| Select | `lc-set-rule <rule>` then `lc-select` (required once before context/outlines will emit content) | not confirmed — flag if you hit an empty MCP result |
| Get context | `lc-context <rule>` | `lc_outlines` + `lc_missing` |
| Check drift | `lc-changed` | `lc_changed` |
| Fetch exact files | `lc-missing -f '[paths]' -t <ts>` | `lc_missing` |

## Path Rules

In rule patterns, paths start with `/`, relative to project root.

```yaml
- "/src/llm_context/rule.py"
- "/tests/test_outliner.py"
```

Preview and generated context show namespaced paths like `/{project-name}/src/...`.

## File Naming

- `tmp-prm-<name>.md`: temporary task rule
- `prm-<name>.md`: reusable prompt rule
- `flt-<name>.md`: reusable filter primitive

## Feedback

This skill is young — actively log friction whenever something is awkward, surprising, ambiguous, missing, or led you down the wrong path. Don't filter; patterns only emerge from honest individual observations.

**Where to log** (try in order):

1. **If the user has a local `llm-context.py` checkout** (sibling repo, editable install, or anywhere else on disk) — append to `<llm-context.py-repo>/field-notes.md`. That's the lowest-friction path to the maintainer, since the entry lands directly in the upstream working tree.
   - Probe common locations before asking: `../llm-context.py`, `~/GitHub/llm-context.py`, `~/src/llm-context.py`. If the user has mentioned the checkout elsewhere in the conversation, use that path.
   - If `field-notes.md` doesn't exist yet, create it with the header below.
2. **Otherwise** — append to `.llm-context/SKILL-FEEDBACK.md` in the current project (created on first entry, git-ignored by default). The user can copy entries upstream later.
3. **For items that clearly generalize beyond this project** — also paste the entry as an issue at https://github.com/cyberchitta/llm-context.py/issues so the maintainer can triage it.

**Entry format** (newest at the top):

- **Date** — `YYYY-MM-DD`, absolute (resolve "today"/"Tuesday" before writing).
- **Task** — one line describing what the user was trying to accomplish.
- **Observation** — 1–3 sentences: what surfaced, what worked around it (if anything), and whether it reads as a one-off or hints at a pattern.
- **Suggested home** — one of `Skill.md` / `PATTERNS.md` / `SYNTAX.md` / `EXAMPLES.md` / `TROUBLESHOOTING.md` / upstream code / `still-unsure`. `still-unsure` is a valid answer.

**First-time header** to drop at the top of a new feedback file (either `<llm-context.py-repo>/field-notes.md` or `.llm-context/SKILL-FEEDBACK.md`):

```markdown
# llm-context skill feedback (uncommitted)

Informal log of friction with the `lc-curate-context` skill — anything
awkward, buggy, missing, or surprising. Newest at the top.
```

Log first; decide later whether the observation generalizes.

## References

- `PATTERNS.md` for reusable shapes
- `EXAMPLES.md` for worked examples
- `SYNTAX.md` for rule syntax
- `TROUBLESHOOTING.md` for failure cases
