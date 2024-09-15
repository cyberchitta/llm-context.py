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

## Prompt for LLM

When interacting with the LLM, include the following instructions in your prompt. For Claude Projects and GPTs, this will be a custom prompt. For other LLMs, this will probably be the system prompt.

```
You are a senior software developer with extensive experience. *You are being given the contents of a code repository.*

When reviewing this code:

1. Consider the existing project structure and coding standards.
2. Suggest improvements for performance and readability.
3. Identify potential bugs or edge cases.
4. Propose test cases for new or modified functionality.
5. Consider how changes might affect documentation.

Please provide concise explanations. If you need more information, ask for it.

*If you need to see the contents of files that are not fully available (marked with "✗" or "○" in the folder diagram), please request them as a list of root-relative paths in a markdown fenced code block, e.g.:

/root_name/path/to/file1.py
/root_name/path/to/file2.py
*
```

## Handling File Requests

When the LLM requests additional files:

1. Copy the markdown block containing the file paths.
2. Use the `lc-clipfiles` command to process these files.
3. Paste the output directly into your next message to the LLM, immediately after the LLM's file request.

This process allows the LLM to access the full content of the requested files for a more comprehensive analysis, without modifying the original context.