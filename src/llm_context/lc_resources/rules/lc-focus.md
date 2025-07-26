---
name: lc-focus
description: "Complete project context with comprehensive focus creation instructions for efficient rule creation"
overview: full
compose:
  filters: ["lc-filters"]
---

# Project Focus Creation Guide

You have been provided with complete project context to help create focused, task-specific rules that include only the minimum necessary files for efficient LLM conversations.

## Your Mission

Analyze the provided project structure and help the user create a focused rule that includes only the essential files needed for their specific task, dramatically reducing context size while maintaining effectiveness.

## Multi-Project Contexts

When working with multiple projects, you'll need to create separate rules for each project. Coordinate the file selections across projects to ensure the combined context provides what's needed for the task.

## Decision Framework

Create task-focused rules by deciding what you need to see to complete the task:

**Full content:** Files you need to read/modify/understand in detail
**Outlined:** Files where you just need to know structure/what's available

### Quick Decision Guide:
- Will I need to see the actual implementation? → Full
- Do I just need to know what functions/classes exist? → Outline  
- Is it small enough that full content doesn't add noise? → Full
- Is it large where outline gives me what I need? → Outline

## Implementation Options

### Option A: Using MCP Tools (if available)

Use the `lc-create-rule` tool:

```json
{
  "name": "tmp-descriptive-task-name",
  "description": "Brief description of what this focuses on",
  "files": ["/project-name/path/to/file1.ext", "/project-name/path/to/file2.ext"],
  "outlines": ["/project-name/path/to/outline1.ext"],
  "content": "Optional: Additional context or instructions for this rule."
}
```

### Option B: Manual Creation

Generate the complete rule and save it using shell commands:

```bash
# Create the rule file
cat > .llm-context/rules/tmp-task-name.md << 'EOF'
---
description: "Brief description of what this focuses on"
overview: "focused"
compose:
  filters: ["lc-no-files"]
files:
  - "/project-name/path/to/file1.ext"
  - "/project-name/path/to/file2.ext"
outlines:
  - "/project-name/path/to/outline1.ext"
---

## Task-Specific Context
Optional: Additional context or instructions for this rule.
EOF

# Activate the rule and generate context
lc-set-rule tmp-task-name
lc-context
```

## Best Practices

- Start minimal and add only when necessary
- Use descriptive rule names (`tmp-` prefix for temporary rules)
- Document why each file was included
- Aim for 10-50% of full project context size
- Consider iterative refinement in follow-up conversations
- Use `overview: "focused"` for compact directory listings

The goal is creating the most efficient context for the specific task while maintaining comprehension.
