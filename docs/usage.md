# LLM Context Usage Guide

## Customizing Ignore Patterns

You can add custom ignore patterns to exclude specific files or directories from being processed by LLM Context. This is useful for ignoring files that are not relevant to your code context.

To add custom ignore patterns:

1. Create a `.llm-context/config.json` file in your project root if it doesn't exist.
2. Add or modify the `gitignores` key in the JSON file.

Example:

```json
{
  "gitignores": {
    "full_files": [
      ".git",
      ".gitignore",
      ".llm-context/",
      "*.log",
      "node_modules/"
    ],
    "outline_files": [
      ".git",
      ".gitignore",
      ".llm-context/",
      "*.log",
      "node_modules/"
    ]
  }
}
```

This example will ignore the specified items for both full file content and outline generation.

## Manually Editing Selected Files

You can manually edit the list of selected files to fine-tune the context provided to the LLM.

1. Locate the `.llm-context/curr_ctx.json` file in your project root.
2. Edit the `context` object in this JSON file, which contains `full` and `outline` arrays for full content and outline files respectively.

Example:

```json
{
  "context": {
    "full": [
      "/path/to/important_file1.py",
      "/path/to/important_file2.py"
    ],
    "outline": [
      "/path/to/less_important_file1.py",
      "/path/to/less_important_file2.py"
    ]
  }
}
```

This allows you to precisely control which files are included in the context for full content and outlines.

## Modifying the context.j2 Template

The `context.j2` template in the `.llm-context/templates/` directory determines the structure of the context provided to the LLM. You can modify this template to customize the output:

1. Navigate to `.llm-context/templates/context.j2` in your project.
2. Edit the file to change the structure or content of the context.

For example, you might want to add or remove sections, or change the formatting of certain parts. Here's a snippet of what you might modify:

```
# Detailed Repository Content: **{{ project_name }}**

This context presents a comprehensive view of the _/{{ project_name }}_ repository.

## Repository Structure

    {{ folder_structure_diagram }}

{% if summary %}
## Project Summary

    {{ summary }}
{% endif %}

// ... (rest of the template)
```

Remember that the template uses Jinja2 syntax, so you can leverage conditional statements, loops, and other Jinja2 features to customize the output. The `{{ }}` syntax is used for variable interpolation, while `{% %}` is used for control structures like conditionals and loops.

You can add new sections, remove existing ones, or change the formatting to better suit your needs. Just be careful to maintain the overall structure that the LLM expects for optimal understanding of the context.