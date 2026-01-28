# Troubleshooting

Common issues and solutions.

## No Files Selected

**Symptom:** Rule produces empty or near-empty context.

**Causes:**

1. Paths missing leading `/`
2. Path includes project name
3. Pattern doesn't match actual structure
4. Filters too aggressive

**Debug with preview:**

CLI: `lc-preview my-rule`
MCP: `lc_preview` tool

```
Full files (0):
Excerpted files (0):
```

**Fix:** Check path format:

```yaml
# Wrong
- "src/file.py"              # Missing /
- "/myproject/src/file.py"   # Has project name

# Correct
- "/src/file.py"
- "/src/**/*.py"
```

---

## Context Too Large

**Symptom:** Context exceeds target size (>100k tokens).

**Solutions:**

1. **Move files from full to excerpted:**

```yaml
# Before
full-files: ["/src/**"]

# After
full-files: ["/src/core/**"]
excerpted-files: ["/src/**"]
```

2. **Use implementations for specific functions:**

```yaml
# Instead of full file
full-files: ["/src/large_utils.py"]

# Extract just what's needed
implementations:
  - ["/src/large_utils.py", "needed_function"]
```

3. **Add exclusions:**

```yaml
gitignores:
  full-files:
    - "**/test/**"
    - "*.md"
```

---

## Missing excerpters Error

**Symptom:** Error about missing excerpters in compose.

**Fix:** Always include `lc/exc-base`:

```yaml
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]   # Required
```

---

## Rule Not Found

**Symptom:** Command/tool fails with "rule not found".

**Causes:**

1. File not in `.llm-context/rules/`
2. Missing `.md` extension
3. Typo in rule name

**Fix:** Verify file location:

```bash
ls .llm-context/rules/*.md
```

---

## also-include Pulls in Noise

**Symptom:** Context includes __pycache__, node_modules, etc.

**Cause:** `also-include` bypasses all filters.

**Fix:** Be specific:

```yaml
# Dangerous
also-include:
  full-files: ["/src/**"]

# Better
also-include:
  full-files:
    - "/src/auth/**"
    - "/src/api/routes.py"
```

Or add explicit exclusions:

```yaml
also-include:
  full-files: ["/src/**"]
gitignores:
  full-files:
    - "__pycache__"
    - "*.pyc"
    - "node_modules"
```

---

## YAML Syntax Error

**Symptom:** Parse error on rule file.

**Common mistakes:**

```yaml
# Wrong - unquoted glob with special chars
also-include:
  full-files:
    - /src/**/*.py

# Correct - quoted
also-include:
  full-files:
    - "/src/**/*.py"

# Wrong - bad indentation
compose:
filters: [lc/flt-base]

# Correct
compose:
  filters: [lc/flt-base]
```

---

## limit-to Conflicts

**Symptom:** Warning about multiple `limit-to` clauses.

**Cause:** Composing rules that both have `limit-to`.

**Fix:** Only the first `limit-to` per category is used. Put specific rule first, or define `limit-to` in the rule itself:

```yaml
compose:
  filters: [lc/flt-base]   # No limit-to here
limit-to:
  full-files: ["/src/api/**"]   # Define here instead
```

---

## Markdown Content Ignored

**Symptom:** Rule markdown doesn't appear in context.

**Cause:** Using `instructions` field.

```yaml
# Markdown is ignored when instructions is set
instructions: [lc/ins-developer]
---
## This is discarded!
```

**Fix:** Choose one approach:

- Use `instructions: [...]` to compose from other rules (no markdown needed)
- Or write markdown directly (no `instructions` field)
