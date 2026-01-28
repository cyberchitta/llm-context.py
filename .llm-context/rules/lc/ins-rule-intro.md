---
description: Introduction to creating context descriptors for agent task delegation.
---

# Context Descriptor Creation

You have project context to help create focused rules that define exactly what a sub-agent needs for a specific task.

## Your Goal

Create a rule that includes only the essential files:

- **Full files:** Code to be modified, small configs, critical integration points
- **Excerpted files:** Related modules (structure only), large files (signatures only)

Target the smallest context that includes everything needed.

## Workflow

1. Understand the task requirements
2. Explore the codebase with `lc-outlines` and file reads
3. Create a rule with appropriate patterns
4. Validate with `lc-preview` to check file selection and size
5. Iterate until context is focused and complete

## Multi-Project Context

llm-context supports combining files from multiple projects. Each file path includes the project directory name as a prefix (`/{project-name}/src/...`), preventing conflicts when contexts are merged.

When working across projects, create rules in each project and combine their outputs.
