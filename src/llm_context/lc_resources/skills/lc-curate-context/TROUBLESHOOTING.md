# Troubleshooting

## Pipe or redirect captured nothing

**Symptom:** `lc-context <rule> > pack.md` produces a file of two log lines, or a piped child answers as if it got no code.

**Cause:** `lc-context` takes no positional rule argument. The name is ignored, the *active* rule is used, and output goes to the **clipboard** — stdout gets only log messages. `lc-preview <rule>` fails louder, with `unrecognized arguments`.

**Fix:** use `-r`, which both names the rule and routes to stdout.

```bash
lc-context -r my-rule > pack.md
lc-context -r my-rule | claude -p 'Task here'
```

---

## No files selected

**Symptom:** the rule produces an empty or near-empty context; `lc-preview` shows `Full files (0)`.

**Causes:** paths missing the leading `/`; path includes the project name; pattern doesn't match the real structure; filters too aggressive.

```yaml
# Wrong
- "src/file.py"              # missing leading /
- "/myproject/src/file.py"   # includes project name

# Correct
- "/src/file.py"
- "/src/**/*.py"
```

Rule patterns are project-root-relative. Only *output* — preview listings and generated context — carries the `/{project-name}/` prefix.

---

## The context says files are excluded that I expected

Check the counts in the generated header first: it reports how many files are full, outlined, and excerpted. If `full` is lower than `lc-preview -r <rule>` showed, the rule changed between the two calls, or a composed filter is narrowing the selection.

Note that the file listing is **not** an inventory of the repository. It is filtered by the repo's `.gitignore` files and by the rule's `overview-files` ignores before anything is marked `✗`, so files can exist that never appear in the listing at all.

---

## Context too large

1. **Move files from full to excerpted:**

```yaml
full-files: ["/src/core/**"]
excerpted-files: ["/src/**"]
```

2. **Extract single definitions** instead of whole files:

```yaml
implementations:
  - ["/src/large_utils.py", "needed_function"]
```

3. **Add exclusions:**

```yaml
gitignores:
  full-files: ["**/test/**", "*.md"]
```

---

## Missing excerpters error

**Symptom:** an error about missing excerpters in `compose`.

**Fix:** every rule needs `lc/exc-base`.

```yaml
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]   # required
```

---

## Rule not found

File must be at `.llm-context/rules/<name>.md`, with the `.md` extension and no typo in the name. Check with `ls .llm-context/rules/*.md`.

---

## also-include pulled in noise

**Symptom:** the context includes `__pycache__`, `node_modules`, and similar.

**Cause:** `also-include` bypasses all filters, by design.

**Fix:** be specific, or re-add exclusions explicitly.

```yaml
also-include:
  full-files: ["/src/auth/**", "/src/api/routes.py"]
```

---

## YAML syntax error

```yaml
# Wrong - unquoted glob
also-include:
  full-files:
    - /src/**/*.py

# Correct
also-include:
  full-files:
    - "/src/**/*.py"
```

Indentation matters too: `filters:` must be nested under `compose:`.

---

## limit-to conflicts

**Symptom:** a warning about multiple `limit-to` clauses.

**Cause:** only the first `limit-to` per category survives composition.

**Fix:** define `limit-to` in the rule itself rather than inheriting it from a composed filter.

---

## Markdown content ignored

**Cause:** the `instructions` field is set, which discards the rule's markdown body.

**Fix:** choose one — compose with `instructions: [...]`, or write markdown directly.

---

## Stale context timestamp

**Symptom:** `lc-missing` fails with "No context found with timestamp …".

**Cause:** these commands resolve a pack out of llm-context's own state by timestamp. A pack that llm-context did not generate — or one whose state was reset by `lc-init` — cannot be resolved.

**Fix:** regenerate the context and use the new timestamp from its header.
