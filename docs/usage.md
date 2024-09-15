# LLM Context Usage Guide

## Customizing Ignore Patterns

You can add custom ignore patterns to exclude specific files or directories from being processed by LLM Context. This is useful for ignoring files that are not relevant to your code context.

To add custom ignore patterns:

1. Create a `.llm-context/config.json` file in your project root if it doesn't exist.
2. Add or modify the `gitignores` key in the JSON file.

Example:

```json
{
  "gitignores": [
    ".git",
    ".gitignore",
    ".llm-context/",
    "*.log",
    "node_modules/"
  ]
}
```

This example will ignore the default items plus any `.log` files and the `node_modules/` directory.

## Manually Editing Selected Files

You can manually edit the list of selected files to fine-tune the context provided to the LLM.

1. Locate the `.llm-context/curr_ctx.json` file in your project root.
2. Edit the `files` array in this JSON file.

Example:

```json
{
  "files": [
    "/path/to/important_file1.py",
    "/path/to/important_file2.py"
  ]
}
```

This allows you to precisely control which files are included in the context, overriding the automatic selection process.

Note: Be cautious when manually editing these files to avoid syntax errors.
