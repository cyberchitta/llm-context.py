---
name: lc/sty-javascript
description: Details JavaScript-specific style guidelines, covering modern features, module systems, object design, asynchronous code, naming conventions, and documentation. Use for JavaScript projects to ensure consistent code style.
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
- Error messages must include: what failed, why it failed, and suggested action

### Naming Conventions

- Use kebab-case for file names
- Use PascalCase for classes and constructors
- Use camelCase for functions, variables, and methods
- Use UPPER_SNAKE_CASE for constants

### Documentation

- Use JSDoc comments for public APIs and complex business logic
- Document parameter and return types with JSDoc tags
