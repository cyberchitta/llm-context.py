# Rule Examples

Complete examples with reasoning.

## Example 1: Add Rate Limiting

**Task:** "Add rate limiting middleware to API endpoints"

**Analysis:**
1. Explore with `lc-outlines` (CLI) or `lc_outlines` (MCP) → reveals `/src/api/middleware/` and `/src/api/routes.py`
2. Read existing middleware to understand patterns
3. Found `rate_limit` decorator in `/src/utils/decorators.py`

**Rule:**

```yaml
---
description: Add rate limiting middleware to API endpoints
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/api/middleware/**"
    - "/src/api/routes.py"
    - "/config/api.yaml"
  excerpted-files:
    - "/src/api/endpoints/**"
implementations:
  - ["/src/utils/decorators.py", "rate_limit"]
---
## Context
Add rate limiting to all API endpoints. Follow existing middleware patterns.
The rate_limit decorator provides the implementation pattern.
```

**Reasoning:**
- Full: middleware (where new code goes), routes (integration), config
- Excerpted: endpoints (see structure, not full implementations)
- Implementation: just the decorator, not the whole utils file

**Result:** ~35k tokens (vs ~200k for full project)

---

## Example 2: Refactor Auth to JWT

**Task:** "Refactor authentication from sessions to JWT tokens"

**Analysis:**
1. Auth code in `/src/auth/`
2. User model provides token payload context
3. Routes show current auth usage patterns

**Rule:**

```yaml
---
description: Refactor authentication from sessions to JWT
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/auth/**"
    - "/src/middleware/auth.py"
    - "/config/auth.yaml"
  excerpted-files:
    - "/src/models/user.py"
    - "/src/api/**/routes.py"
gitignores:
  full-files:
    - "**/tests/**"
---
## Context
Migrate from session-based auth to JWT. User model shows token claim structure.
Route files show current auth middleware usage.
```

**Reasoning:**
- Full: all auth code (being modified), middleware, config
- Excerpted: user model (token claims), routes (usage patterns)
- Excluded: tests initially (add later if needed)

**Result:** ~50k tokens

---

## Example 3: Debug Performance

**Task:** "Debug slow data processing in report generation"

**Analysis:**
1. Report generator at `/src/reports/generator.py`
2. Performance tests exist at `/tests/reports/test_performance.py`
3. Data sources in `/src/data/`

**Rule:**

```yaml
---
description: Debug performance in report generation
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/reports/generator.py"
    - "/src/reports/processors/**"
    - "/tests/reports/test_performance.py"
  excerpted-files:
    - "/src/data/**"
    - "/src/models/report.py"
implementations:
  - ["/src/utils/profiling.py", "profile_function"]
---
## Context
Report generation is slow. Focus on generator and processors.
Data layer shown as structure only. Use profiling decorator for instrumentation.
```

**Result:** ~30k tokens

---

## Example 4: Minimal Fix

**Task:** "Fix typo in error message in auth handler"

**Rule:**

```yaml
---
description: Fix error message typo in auth handler
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files:
    - "/src/auth/handler.py"
---
## Task
Fix the typo in the authentication error message.
```

**Result:** ~2k tokens

This is the minimal pattern - exclude everything, include only what's needed.
