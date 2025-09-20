---
description: Outlines universal code style principles for modern programming languages, emphasizing functional patterns, clarity, immutability, and robust architecture. Use as a foundation for language-agnostic coding.
---

## Universal Code Style Principles

### Functional Programming Approach

- Prefer functional over imperative patterns
- Favor pure functions and immutable data structures
- Design for method chaining through immutable transformations
- Prefer conditional expressions over conditional statements when possible

### Code Clarity

- Write self-documenting code through expressive naming
- Good names should make comments superfluous
- Compose complex operations through small, focused functions

### Object Design

- Keep constructors/initializers simple with minimal logic
- Use static factory methods (typically `create()`) for complex object construction
- Design methods to return new instances rather than mutating state
- Prefer immutable data structures and frozen/sealed objects

### Error Handling

- Validate inputs at application boundaries, not within internal functions
- **Natural Failure Over Validation**: Don't add explicit checks for conditions that will naturally cause failures
- Let language built-in error mechanisms work (TypeError, ReferenceError, etc.)
- Only validate at true application boundaries (user input, external APIs)
- Internal functions should assume valid inputs and fail fast
- Trust that calling code has met preconditions - fail fast if not
- Avoid defensive programming within core logic
- Create clear contracts between functions

### Architecture

- Favor composition over inheritance
- Avoid static dependencies - use dependency injection for testability
- Maintain clear separation between pure logic and side effects

**Goal: Write beautiful code that is readable, maintainable, and robust.**

## Code Quality Enforcement

**CRITICAL: Follow all style guidelines rigorously in every code response.**

Before writing any code:
1. **Check functional patterns** - Are functions pure? Do they return new data instead of mutating?
2. **Review naming** - Are names concise but expressive? Avoid verbose parameter names.
3. **Verify immutability** - Are data structures immutable? Can operations be chained?
4. **Simplify logic** - Can this be written more elegantly with comprehensions, functional patterns?
5. **Type hints** - Are all parameters and returns properly typed?

**Red flags that indicate style violations:**
- Functions that mutate input parameters
- Verbose parameter names like `coverage_threshold` vs `threshold`
- Imperative loops instead of functional patterns
- Missing type hints or vague types like `Any`
- Complex nested conditionals instead of guard clauses

**When in doubt, prioritize elegance and functional patterns over apparent convenience.**
