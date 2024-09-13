# LLM Context

LLM Context is a Python-based tool designed to streamline the process of sharing code context with Large Language Models (LLMs) using a standard Chat UI. It intelligently selects relevant files using `.gitignore` rules, generates comprehensive code context, and copies it directly to your clipboard for easy sharing with AI assistants.

## Key Features

- **Intelligent File Selection**: Automatically respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting into LLM chats.
- **Code Structure Visualization**: Generates outlines of selected files to provide a quick overview of code structure.
- **Customizable Ignore Patterns**: Allows additional ignore patterns to be specified, giving you fine-grained control over what's included in the context.

## Installation

Use [pipx](https://pypa.github.io/pipx/) to install LLM Context:

```
pipx install llm-context
```

## Usage

LLM Context offers flexibility in how you share your code context, depending on the size of your repository:

### For Small Repositories

If your entire repository fits within the LLM's context window:

1. Use `lc-gencontext` to generate and copy the full content of all selected files, including the folder structure.
2. Paste this complete context into your LLM chat.

### For Large Repositories

When the entire repo is too large to fit in the LLM's context window:

1. Use `lc-gencontext` to generate the folder structure.
2. Use `lc-outlines` to generate code outlines for all selected files.
3. Combine the output from steps 1 and 2, and paste this into your LLM chat.
4. When the LLM requests specific files, use `lc-files` to generate their full content.

## Main Commands

- `lc-select`: Choose files based on gitignore rules and custom patterns.
- `lc-gencontext`: Generate full context or folder structure.
- `lc-outlines`: Generate outlines of selected files.
- `lc-files`: Generate full text contents of specific files.
- `lc-clipfiles`: Generate full text contents of files listed in the clipboard.

## Typical Workflow

1. Navigate to your project's root directory.
2. (Optional) Edit `.llm-context/config.json` to add custom ignore patterns.
3. Run `lc-select` to choose files for context.
4. For small repos: Run `lc-gencontext`.
   For large repos: Run both `lc-gencontext` and `lc-outlines`, and combine their output.
5. Paste the generated context into your LLM chat.
6. Inform the LLM about the presence and nature of the context you've provided.

### Providing Files to LLM (for large repos)

1. When the LLM requests specific files, it will typically do so in a markdown block quote.
2. Copy the LLM's file request to your clipboard.
3. Run `lc-clipfiles` to generate the content of the requested files.
4. Paste the generated file contents back into your chat with the LLM.

This workflow allows for dynamic interaction with the LLM, providing initial context and responding to specific file requests as needed during the conversation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.