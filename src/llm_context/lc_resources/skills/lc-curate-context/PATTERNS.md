# Rule Patterns

Use the smallest primitive vocabulary that expresses the task cleanly.

## Primitives

| Primitive | Effect | Use when |
|---|---|---|
| `lc/flt-no-files` | Start from nothing | Surgical task; you know the likely files; you want exact control. **The usual default.** |
| `lc/flt-base` | Broad code baseline, standard noise removed | Task spans a subsystem; you don't yet know the exact files; repo is small enough to stay inspectable. Verify with `lc-preview` — it can admit a lot. |
| `lc/flt-no-full` | Suppress all full-file selection | You want structure only, e.g. surveying before deciding what needs full content. |
| `lc/flt-no-outline` | Suppress all excerpted-file selection | You want exact bodies only; excerpting would add noise. |
| `lc/exc-base` | Standard excerpting behaviour | Always — compose this into every task rule. |

**`flt-repo-base`** is a convention, not a system rule: a project-local baseline in `.llm-context/rules/` capturing stable local noise (rarely-needed docs, tests, generated sources). Worth writing when several task rules need the same repo-specific baseline. If it is too broad, every rule that composes it silently over-selects.

## Recipes

### 1. Surgical change

```yaml
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<edit-targets>..."]
  excerpted-files: ["/<supporting-context>..."]
```

### 2. Surgical change, exact bodies only

```yaml
compose:
  filters: [lc/flt-no-files, lc/flt-no-outline]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<edit-targets>..."]
```

### 3. Repo baseline plus targeted additions

```yaml
compose:
  filters: [flt-repo-base]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<edit-targets>..."]
  excerpted-files: ["/<supporting-context>..."]
```

### 4. Repo baseline, full-file bias

For editing docs, rules, or templates, where excerpting the main targets adds nothing.

```yaml
compose:
  filters: [flt-repo-base, lc/flt-no-outline]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<primary-files>..."]
```

### 5. Excerpt-only survey

Use before narrowing a task rule.

```yaml
compose:
  filters: [flt-repo-base, lc/flt-no-full]
  excerpters: [lc/exc-base]
also-include:
  excerpted-files: ["/<area-to-survey>..."]
```

### 6. Shared brief in a sibling repo

`also-include` pathspecs are bounded by the project root (SYNTAX.md "Scope"), so `../other-repo/voice.md` silently matches nothing. Inline the brief into the rule body and keep the in-repo selection minimal.

```yaml
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<edit-targets>..."]
---
## Voice (inlined from ../other-repo/voice.md)

<paste the brief here>
```

Drift risk: edits to the sibling source won't propagate. Note the source path at the top of the inlined block so a future reader knows where to refresh from.

### 7. Curated reading pack, narrow topic

For a `lc/flt-no-files` + `also-include` set living in one or two directories, where the rest of the repo (data dumps, images, build output) has nothing to do with the task.

```yaml
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
overview: focused
also-include:
  full-files: ["/<curated-reading-list>..."]
```

`focused` collapses a directory to a one-line summary only when it holds **zero** selected files — any directory with at least one selected file is still listed file by file, exactly as under `full`. So it costs nothing in directories your selection already touches, and only trims ones already wholly unrelated. Prefer `full` when plausible follow-up requests could come from directories your selection doesn't touch and the consumer has a channel to service them.

### 8. Pack for a disposable sub-agent

The dispatcher writes the prompt; the rule supplies the files. Keep the rule free of instructions — the markdown body would just compete with the dispatcher's prompt.

```yaml
compose:
  filters: [lc/flt-no-files, lc/flt-no-outline]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/<everything-the-task-touches>..."]
```

```bash
lc-context -r tmp-prm-task -a | claude -p 'Task here'
```

`lc/flt-no-outline` is what makes it a whole-files pack: no file arrives as a signature-only outline the child cannot act on. Verify in the output header, not in the rule — the generated context reports how many files are full, outlined, and excerpted, so a pass that depends on complete files can assert the outlined and excerpted counts are zero.

`-a` renders the fetch instructions as shell commands the child runs itself, rather than MCP tool calls it has no server for. Run it from the repo root so they resolve. See COMMANDS.md for the three consumer renderings. See SKILL.md "Packing for a Sub-Agent".

## Anti-Patterns

**Don't enumerate selected files in the markdown body.** The generated context already lists every selected file with its status. A "Files in this pack" preamble duplicates that and goes stale on every selection change. The body is for task-specific instructions — what to do, what to watch for, what the files don't carry.

**Don't rely on a filter to guarantee a property.** `lc/flt-no-outline` expresses "no excerpts", but a later edit can compose it away with no signal. If a pass depends on the property, check the counts in the generated header.

## Verification Checklist

After writing a rule, run `lc-preview -r <rule>`:

1. Are all intended edit targets in `Full files`?
2. Did anything unrelated leak into `Full files`?
3. Are support files in `Excerpted files` rather than `Full files`?
4. Is the baseline primitive too broad for this task?

If 2 or 4 is yes, narrow the composition before touching the file lists.
