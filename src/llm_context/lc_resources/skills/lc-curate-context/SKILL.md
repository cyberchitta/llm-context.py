---
name: lc-curate-context
description: Create llm-context rules that define the minimal sufficient file set for a task, and pack that set for a chat, an MCP client, or a disposable sub-agent
---

# Context Descriptor Creation

Write rules that define the minimal sufficient context for a task.

The job is not to gather a lot of relevant code. It is to produce the smallest full-file and excerpted-file set that is still enough to finish the task.

## Workflow

1. Understand the task in concrete file terms.
2. Pick the narrowest sensible baseline filter (see below).
3. Put files you expect to **edit** in `full-files`.
4. Put callers, dependencies, and large reference files in `excerpted-files`.
5. Run `lc-preview -r <rule>`. Read the exact `Full files` / `Excerpted files` lists, then `Referenced but not selected`.
6. Tighten until the selection is minimal and sufficient.
7. Generate the real output once before handing the rule off — `lc-context -r <rule>` — and confirm it contains file bodies, not just a tree.

## Pick the Baseline First

Start narrow unless you have a reason not to.

| Baseline | Use when |
|---|---|
| `lc/flt-no-files` | Surgical task; you know the likely files; you want exact control over membership. **Default for task rules.** |
| `flt-repo-base` or `lc/flt-base` | Broad project slice; the task spans a subsystem; the repo already has a disciplined baseline filter. |

If `lc-preview` shows unexpected full files, the baseline is too broad.

## Full vs Excerpted

**Full** — files you expect to edit; small configs or templates that control the behaviour; compact integration points where exact code matters.

**Excerpted** — callers and dependencies; large modules where structure is enough; reference implementations and surrounding architecture.

Move a file from excerpted to full only when the exact body matters.

## Verify with `lc-preview`

Read `Summary`, then `Full files`, then `Excerpted files`, and ask:

- Are all expected edit targets in `Full files`?
- Did anything unrelated leak into `Full files`?
- Are context files in `Excerpted files` rather than `Full files`?
- Is the total small enough for the task?

Do not trust a rule until the exact file lists look right.

### Referenced but not selected

`lc-preview` also lists files that **define symbols your selection uses but which the rule does not include**, ranked by how many. This is the check for the failure the file lists cannot show you: a rule that looks tidy but omits the module its edit targets actually call.

Add the ones the task needs. Leave the rest — they stay reachable through `lc-missing`, and pulling in everything reachable is how a minimal rule turns into the whole repo. Matching is by symbol name, so a common name may point at the wrong file; treat the list as a hint, not a checklist.

## Packing for a Sub-Agent

A rule is also how you hand a task to a disposable child agent. The dispatcher writes the prompt; llm-context supplies the files.

```bash
lc-context -r tmp-prm-auth -a | claude -p 'Your task here'
```

`-r` is what routes output to **stdout**; without it `lc-context` copies to the clipboard instead. This is the difference between a working pipe and an empty one — see COMMANDS.md.

Three things decide whether the pack is usable:

- **`-a` is not optional.** It tells the pack its reader is an agent with a shell, so the fetch instructions render as `lc-missing` commands the child runs itself. The default renders MCP tool calls it has no server for; `-nt` renders shell commands addressed to "the user", which it will not act on. Run the child from the repo root so those commands resolve.
- **The pack is always partial.** The file listing is filtered by the repo's `.gitignore` files and by the rule's `overview-files` ignores before anything is even marked excluded, so files exist that the listing never mentions. A tooled child *will* find them. That is expected, not a contradiction.
- **Whole-files passes should check the header, not the rule.** The generated context states how many files are full, outlined, and excerpted. If a pass depends on complete files with no excerpts, assert the outlined and excerpted counts are zero in the output rather than trusting that a filter is still configured.

See PATTERNS.md "Pack for a disposable sub-agent" for the rule shape.

## Path Rules

In rule patterns, paths start with `/`, relative to project root:

```yaml
- "/src/llm_context/rule.py"
- "/tests/test_outliner.py"
```

Preview and generated context show namespaced paths like `/{project-name}/src/...`.

## File Naming

- `tmp-prm-<name>.md` — temporary task rule
- `prm-<name>.md` — reusable prompt rule
- `flt-<name>.md` — reusable filter primitive

## Feedback

Log whenever something here is awkward, buggy, missing, surprising, or took more work than it should.

- **Don't filter** — the maintainer triages. Patterns only emerge from honest individual observations.
- Write it to the field-notes destination declared in the project's `CLAUDE.md`. If the project declares none, say so once and move on.
- Log first; worry about whether it generalizes later.

## References

- `COMMANDS.md` — CLI and MCP command reference
- `SYNTAX.md` — rule file schema and field details
- `PATTERNS.md` — reusable rule shapes
- `EXAMPLES.md` — worked examples from this repo
- `TROUBLESHOOTING.md` — failure cases
