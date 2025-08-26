---
name: lc/javascript-style
description: "JavaScript-specific style guidelines building on universal code principles"
---

## JavaScript-Specific Guidelines

### Modern JavaScript Features

- Use array methods (`map`, `filter`, `reduce`) over traditional loops
- Leverage arrow functions for concise expressions
- Use destructuring assignment for objects and arrays
- Prefer template literals over string concatenation
- Use spread syntax (`...`) for array/object operations

### Module System

- Prefer named exports over default exports (better tree-shaking and refactoring)
- Use consistent import/export patterns
- Structure modules with clear, focused responsibilities

### Object Design

- Use `Object.freeze()` to enforce immutability
- Keep constructors simple - use static factory methods for complex creation
- Use class syntax for object-oriented patterns
- Prefer composition through mixins or utility functions

### Asynchronous Code

- Use `async/await` over Promise chains for better readability
- Handle errors with proper try/catch blocks
- Provide meaningful error messages

### Naming Conventions

- Use kebab-case for file names
- Use PascalCase for classes and constructors
- Use camelCase for functions, variables, and methods
- Use UPPER_SNAKE_CASE for constants

### Documentation

- Use JSDoc comments for complex functions and public APIs
- Document parameter and return types
- Include usage examples for non-obvious functions
