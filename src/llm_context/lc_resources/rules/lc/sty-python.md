---
name: lc/sty-python
description: Provides Python-specific style guidelines, including Pythonic patterns, type system usage, class design, import organization, and idioms. Use for Python projects to ensure consistent, readable, and maintainable code.
---

## Python-Specific Guidelines

### Pythonic Patterns

- Use list/dict comprehensions over traditional loops
- Leverage tuple unpacking and multiple assignment
- Use conditional expressions for simple conditional logic
- Prefer single-pass operations: `sum(x for x in items if condition)` over separate filter+sum

### Type System

- Use comprehensive type hints throughout
- Import types from `typing` module as needed
- Use specific types: `list[str]` not `list`, `dict[str, int]` not `dict`

### Class Design

- Use `@dataclass(frozen=True)` as the default for all classes
- Keep `__init__` methods trivial - delegate complex construction to `@staticmethod create()` methods
- Design for immutability to enable functional composition
- Use `@property` for computed attributes

### Import Organization

- Always place imports at module top
- Never use function-level imports except for documented lazy-loading scenarios
- Import order: standard library, third-party, local modules
- Follow PEP 8 naming conventions (snake_case for functions/variables, PascalCase for classes)

### Python Idioms

- Use `isinstance()` for type checking
- Leverage `enumerate()` and `zip()` for iteration
- Use context managers (`with` statements) for resource management
- Prefer `pathlib.Path` over string path manipulation
