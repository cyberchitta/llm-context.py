---
name: lc/sty-jupyter
description: Specifies style guidelines for Jupyter notebooks (.ipynb), focusing on cell structure, documentation, type annotations, AI-assisted development, and output management. Use for Jupyter-based projects to ensure clear, executable notebooks.
---

## Jupyter Notebook Guidelines

### Cell Structure

- One logical concept per cell (single function, data transformation, or analysis step)
- Execute cells independently when possible - avoid hidden dependencies
- Use meaningful cell execution order that tells a clear story

### Documentation Pattern

- Use markdown cells for descriptions, not code comments
- Code cells should contain zero comments - let expressive code speak for itself
- Focus markdown on _why_ and _context_, not _what_ and _how_

### Type Annotations

- Use `jaxtyping` and similar libraries for concrete, descriptive type signatures
- Specify array shapes, data types, and constraints explicitly
- Examples:

  ```python
  from jaxtyping import Float, Int, Array

  def process_features(
      data: Float[Array, "batch height width channels"],
      labels: Int[Array, "batch"]
  ) -> Float[Array, "batch features"]:
  ```
