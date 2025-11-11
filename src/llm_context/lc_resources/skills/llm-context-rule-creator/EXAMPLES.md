# Detailed Rule Examples

Complete examples with reasoning.

## Example 1: Add Rate Limiting to API

### Task Description

"Add rate limiting middleware to our API endpoints"

### Analysis Process

1. **Examine structure:**

```
   lc_outlines(root_path)
```

Found:

- `/src/api/middleware/` (existing middleware)
- `/src/api/routes.py` (route definitions)
- `/src/api/endpoints/` (endpoint implementations)

2. **Check patterns:**

```
   lc_missing(root_path, "f", ["/src/middleware/auth.py"], timestamp)
```

See how existing middleware is structured

3. **Check utilities:**

```
   lc_missing(root_path, "f", ["/src/utils/decorators.py"], timestamp)
```

Found `rate_limit` decorator already exists

### Generated Rule

```yaml
---
description: Add rate limiting middleware to API endpoints
overview: full
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
    - "/src/middleware/**"
implementations:
  - ["/src/utils/decorators.py", "rate_limit"]
---
## Rate Limiting Context

Focus on existing middleware patterns for consistency.
Check how authentication middleware integrates with routes.
The rate_limit decorator provides the implementation pattern.
```

### Reasoning

**Full files (3):**

- `/src/api/middleware/**` - Where new middleware goes
- `/src/api/routes.py` - Integration point
- `/config/api.yaml` - May need rate limit settings

**Excerpted (varies, ~12):**

- `/src/api/endpoints/**` - See how endpoints are structured
- `/src/middleware/**` - Other middleware for patterns

**Implementation:**

- `rate_limit` decorator - Specific utility without full file

**Result:** ~35k tokens (was ~200k with full project)

---

## Example 2: Refactor Auth to JWT

### Task Description

"Refactor authentication system from sessions to JWT tokens"

### Analysis Process

1. **Find auth code:**

```
   lc_outlines(root_path)
```

Located `/src/auth/` directory

2. **Check dependencies:**

```
   lc_missing(root_path, "f", ["/src/models/user.py"], timestamp)
```

See user model structure

3. **Find usage:**
   Scan for routes using auth - found in `/src/api/`

### Generated Rule

```yaml
---
description: Refactor authentication from sessions to JWT tokens
overview: full
compose:
  filters: [lc/flt-base]
  excerpters: [lc/exc-base]
instructions: [lc/ins-developer, lc/sty-python]
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
## JWT Migration Context

Focus on auth module and middleware.
User model provides context for token claims.
API routes show current usage patterns.
Tests excluded initially - add later if needed.
```

### Reasoning

**Full files (multiple files in /src/auth/, plus 2 specific):**

- All auth module files - direct modification
- Middleware - integration point
- Config - JWT settings needed

**Excerpted (~15 files):**

- User model - token payload context
- Route files - usage patterns

**Excluded:**

- Tests - can add later after implementation

**Result:** ~50k tokens (was ~300k full project)

---

## Example 3: Debug Performance Issue

### Task Description

"Debug slow data processing in report generation"

### Analysis Process

1. **Locate issue:**

```
   lc_outlines(root_path)
```

Found `/src/reports/generator.py`

2. **Check tests:**

```
   lc_missing(root_path, "f", ["/tests/reports/"], timestamp)
```

See test cases and benchmarks

3. **Find data sources:**
   Located `/src/data/` and `/src/models/`

### Generated Rule

```yaml
---
description: Debug performance issues in report generation
overview: full
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
## Performance Debug Context

Focus on report generation and processing.
Data sources shown as structure only.
Profiling utility for instrumentation.
```

### Reasoning

**Full files (4-6):**

- Main generator - where bottleneck likely is
- Processors - related processing
- Performance test - benchmarks

**Excerpted (~10 files):**

- Data sources - see structure, not full data
- Report model - understand schema

**Implementation:**

- Profiling decorator - useful utility

**Result:** ~30k tokens (focused on problem area)
