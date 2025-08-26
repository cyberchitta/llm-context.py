---
name: lc/code-style
description: "Universal code style principles for modern programming languages"
---

## Universal Code Style Principles

### Functional Programming Approach

- Prefer functional over imperative patterns
- Use modern language features over traditional loops and constructs
- Favor pure functions and immutable data structures
- Design for method chaining through immutable transformations

### Code Clarity

- Write self-documenting code through expressive naming
- Good names should make comments superfluous
- Use modern language idioms and syntax features
- Compose complex operations through small, focused functions

### Object Design

- Keep constructors/initializers simple with minimal logic
- Use static factory methods (typically `create()`) for complex object construction
- Design methods to return new instances rather than mutating state
- Prefer immutable data structures and frozen/sealed objects

### Error Handling

- Validate inputs at application boundaries, not within internal functions
- Internal functions should assume valid inputs and fail fast
- Avoid defensive programming within core logic
- Create clear contracts between functions

### Architecture

- Favor composition over inheritance
- Design for testability through small, focused units
- Maintain clear separation between pure logic and side effects

**Goal: Write beautiful code that is readable, maintainable, and robust.**
