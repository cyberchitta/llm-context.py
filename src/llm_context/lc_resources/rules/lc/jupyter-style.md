---
name: lc/jupyter-style
description: "Jupyter notebook style guidelines for AI-assisted development"
---

## Jupyter Notebook Guidelines

### Cell Structure
- One logical concept per cell (single function, data transformation, or analysis step)
- Execute cells independently when possible - avoid hidden dependencies
- Use meaningful cell execution order that tells a clear story

### Documentation Pattern
- Use markdown cells for descriptions, not code comments
- Code cells should contain zero comments - let expressive code speak for itself
- Keep markdown concise - don't repeat what clear code already explains
- Focus markdown on *why* and *context*, not *what* and *how*

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

### AI-Assisted Development
- Write type-rich, self-documenting code that AI can easily understand
- Use descriptive variable names that capture the data transformation
- Structure code for easy AI modification and extension
- Prefer functional transformations over stateful operations

### Output Management
- Use `display()` for rich outputs (DataFrames, visualizations)
- Show data shapes and types after major transformations
- Suppress unnecessary output with `;` when appropriate
- Keep outputs clean and focused on the essential information
