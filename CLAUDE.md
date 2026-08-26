# CLAUDE.md

## Working notes (gitignored)

Tracked separately in the private `working-notes` repo, symlinked at `_notes/`;
invisible to the `Grep`/`Glob` tools (global `CLAUDE.md` has the `rg` forms).
Read directly when relevant:

- `_notes/field-notes.md` — friction log for the `lc-curate-context` skill,
  written from consumer sessions in other repos. Newest entry at the top.
- `_notes/implementation-log.md` — what shipped from a drained field note.
  Entries stand on their own; the note each came from is gone. Its header
  carries the next entry point; this repo keeps no separate worklist.

Speculative unless stated otherwise. Do not implement from these without asking.

Field notes: `_notes/field-notes.md`

## Draining the field notes

An observation earns a change after **2–3 sightings in separate contexts**;
bugs, and notes that resonate with an already-recorded candidate, promote on
one. Be suspicious of frequency from a single author — one observation refined
twice is still one observation.

A promoted entry is **deleted**, and a summary that stands alone goes in
`_notes/implementation-log.md`. This is the file's only retirement gate, and it
went un-run from 2026-05-17 to 2026-08-26, by which point the file was 16KB and
half of it described behaviour that no longer existed.

Where a promoted note lands:

| Observation | Target |
| --- | --- |
| Wrong output, crash, or a broken documented invariant | code + a regression test |
| A command or instruction the tool emits that does not work | the template, and a test over the rendered artifact |
| Rule authoring: what to select, and how to verify it | skill `SKILL.md` / `PATTERNS.md` / `EXAMPLES.md` |
| Rule file schema and field semantics | skill `SYNTAX.md` |
| CLI or MCP behaviour, flags, output routing | skill `COMMANDS.md` |
| A failure mode a reader will hit again | skill `TROUBLESHOOTING.md` |
| Consumers without skill support | `lc_resources/rules/lc/ins-rule-framework.md` |
| Product direction, not friction | leave in `field-notes.md`, or track it where it can be tested |

The skill's own docs ship from `src/llm_context/lc_resources/` — that is the
source of truth. `.llm-context/` and `.claude/skills/` are generated copies,
refreshed only when `CURRENT_CONFIG_VERSION` rises, so a fix that skips the
version bump reaches new installs and nobody else.
