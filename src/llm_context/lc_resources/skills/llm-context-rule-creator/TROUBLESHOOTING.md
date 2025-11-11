# Rule Creation Troubleshooting

Common issues and solutions.

## No Files Matched

**Problem:** Rule selects zero files

**Causes:**

1. Paths don't start with `/`
2. Paths include project name
3. Patterns don't match actual structure
4. Filters too restrictive

**Solutions:**

```yaml
# ❌ Wrong
also-include:
  full-files:
    - "src/file.py"              # Missing /
    - "/myproject/src/file.py"    # Has project name
    - "/src/"                     # Directory, not files

# ✅ Correct
also-include:
  full-files:
    - "/src/file.py"
    - "/src/**/*.py"
```

---

## Context Too Large

**Problem:** Generated context exceeds 100k tokens

**Solutions:**

1. **Move files to excerpted:**

```yaml
# Before
also-include:
  full-files:
    - "/src/**"  # Too broad

# After
also-include:
  full-files:
    - "/src/core/**"  # Just core
  excerpted-files:
    - "/src/**"  # Rest as structure
```

2. **Use implementations:**

```yaml
# Instead of full file
also-include:
  full-files:
    - "/src/large_utils.py"

# Extract specific function
implementations:
  - ["/src/large_utils.py", "needed_function"]
```

3. **Add exclusions:**

```yaml
gitignores:
  full-files:
    - "**/test/**"
    - "**/*.md"
```

---

## Missing Required Compose

**Problem:** Error about missing excerpters

**Solution:**

```yaml
# ❌ Missing
compose:
  filters: [lc/flt-base]

# ✅ Required
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]  # Always needed
```

---

## Rule Not Found

**Problem:** `lc-set-rule tmp-prm-my-rule` fails

**Causes:**

1. File not saved to `.llm-context/rules/`
2. Wrong filename (needs `.md` extension)
3. Typo in rule name

**Solution:**

```bash
# Save to correct location
.llm-context/rules/tmp-prm-my-rule.md

# Verify
ls .llm-context/rules/tmp-prm-*.md
```

---

## Composition Conflicts

**Problem:** Warning about multiple `limit-to` clauses

**Cause:** Composing rules with conflicting `limit-to`

**Solution:**

```yaml
# Only first limit-to is used
# Put most specific rule first in composition
compose:
  filters: [specific-filter, lc/flt-base]
```

Or define `limit-to` in the rule itself:

```yaml
compose:
  filters: [lc/flt-base] # No limit-to conflicts
limit-to:
  full-files: ["/src/api/**"] # Define here
```

---

## Path Pattern Not Matching

**Problem:** Pattern should match but doesn't

**Debug:**

```yaml
# Test patterns incrementally
also-include:
  full-files:
    - "/src/api/routes.py"  # Specific file first

# Then expand
also-include:
  full-files:
    - "/src/api/**"  # Directory pattern

# Check for typos
# ❌ /src/aip/**
# ✅ /src/api/**
```

---

## YAML Syntax Error

**Problem:** Invalid YAML in frontmatter

**Common mistakes:**

```yaml
# ❌ Missing quotes for patterns with special chars
also-include:
  full-files:
    - /src/**/*.py

# ✅ Quote patterns
also-include:
  full-files:
    - "/src/**/*.py"

# ❌ Wrong indentation
compose:
filters: [lc/flt-base]  # Should be indented

# ✅ Correct indentation
compose:
  filters: [lc/flt-base]
```

**Solution:** Validate YAML before saving
