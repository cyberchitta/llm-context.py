---
name: lc/python-style
description: "Python-specific style guidelines building on universal code principles"
---

## Python-Specific Guidelines

### Pythonic Patterns
- Use list/dict comprehensions over traditional loops
- Leverage tuple unpacking and multiple assignment
- Use conditional expressions for simple conditional logic
- Prefer single-pass operations for efficiency

### Type System
- Use comprehensive type hints throughout
- Import types from `typing` module as needed
- Type hints should enhance code readability and IDE support

### Class Design
- Use `@dataclass(frozen=True)` as the default for all classes
- Keep `__init__` methods trivial - delegate complex construction to `@staticmethod create()` methods
- Design for immutability to enable functional composition
- Use `@property` for computed attributes

### Python Idioms
- Use `isinstance()` for type checking
- Leverage `enumerate()` and `zip()` for iteration
- Use context managers (`with` statements) for resource management
- Prefer `pathlib.Path` over string path manipulation

### Code Organization
- Follow PEP 8 naming conventions (snake_case for functions/variables, PascalCase for classes)
- Use meaningful module and package structure
- Import order: standard library, third-party, local modules
