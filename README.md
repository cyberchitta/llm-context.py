# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)

LLM Context is a command-line tool designed to help developers efficiently copy and paste relevant context from code / text repositories into Large Language Model (LLM) chats. It leverages `.gitignore` patterns for smart file selection and uses the clipboard for seamless integration with LLM interfaces.

> **Note**: This project was developed in collaboration with Claude-3.5-Sonnet, using LLM Context itself to share code context during development. All code in the repository is human-curated (by me 😇, @restlessronin).

## Current Usage Patterns

- **LLM Integration**: Primarily used with Claude (Project Knowledge) and GPT (Knowledge), but adaptable to various chat interfaces.
- **Project Types**: Suitable for code repositories and collections of text/markdown/html documents.
- **Project Size**: Optimized for projects that fit within an LLM's context window. Large project support is in development.

## Installation

Use [pipx](https://pypa.github.io/pipx/) to install LLM Context:

```
pipx install llm-context
```

## Usage

### Quick Start and Typical Workflow

1. [Install LLM Context](#installation) if you haven't already.
2. Navigate to your project's root directory.
3. Run `lc-init` to set up LLM Context for your project (only needed once per repository).
4. Ensure you have a custom prompt set up in your AI assistant (e.g., ChatGPT, Claude).
   - A starter prompt for code projects can be found in the `.llm-context/developer-prompt.md` file in this repository.
5. (Optional) Edit `.llm-context/config.toml` to [add custom ignore patterns](#customizing-ignore-patterns).
6. Run `lc-sel-files` to select files for full content inclusion.
7. (Optional) [Review the selected file](#reviewing-selected-files) list in `.llm-context/curr_ctx.toml`.
8. Run `lc-context` to generate and copy the context to your clipboard.
9. Paste the generated context into your Claude Project Knowledge or GPT Knowledge.
10. Start your conversation with the LLM about your project.

To keep your AI assistant's project context up-to-date:

- When significant changes occur in your project, repeat steps 6-9.
- The custom prompt remains constant and doesn't need updating.

Remember: Regularly updating the project context ensures the AI assistant has the most current information about your project structure and contents.

### Handling LLM File Requests

When the LLM asks for a file that isn't in the current context:

1. Copy the LLM's file request (typically in a markdown block) to your clipboard.
2. Run `lc-read-cliplist` to generate the content of the requested files.
3. Paste the generated file contents back into your chat with the LLM.

### Configuration

#### Customizing Ignore Patterns

Add custom ignore patterns in `.llm-context/config.toml` to exclude specific files or directories not covered by your project's `.gitignore`. This is useful for versioned files that don't contribute to code context, such as media files, large generated files, detailed changelogs, or environment-specific configurations.

Example:

```toml
# /.llm-context/config.toml
[gitignores]
full_files = [
  "*.svg",
  "*.png",
  "CHANGELOG.md",
  ".env",
  # Add more patterns here
]
```

#### Reviewing Selected Files

Review the list of selected files in `.llm-context/curr_ctx.toml` to check what's included in the context. This is particularly useful when trying to minimize context size.

```toml
# /.llm-context/curr_ctx.toml
[context]
full = [
  "/llm-context.py/pyproject.toml",
  # more files ...
]
```

## Command Reference

- `lc-init`: Initialize LLM Context for your project (only needed once per repository)
- `lc-sel-files`: Select files for full content inclusion
- `lc-sel-outlines`: Select files for outline inclusion (experimental)
- `lc-context`: Generate and copy context to clipboard
- `lc-read-cliplist`: Read contents for LLM-requested files, and copy to clipboard

## Experimental: Handling Larger Repositories

For larger projects, we're exploring a combined approach of full file content and file outlines. Use `lc-sel-outlines` after `lc-sel-files` to experiment with this feature.

**Note:** The outlining feature currently supports the following programming languages:
C, C++, C#, Elisp, Elixir, Elm, Go, Java, JavaScript, OCaml, PHP, Python, QL, Ruby, Rust, and TypeScript. Files in unsupported languages will not be outlined and will be excluded from the outline selection.

### Feedback and Contributions

We welcome feedback, issue reports, and pull requests on our [GitHub repository](https://github.com/cyberchitta/llm-context.py).

## Acknowledgments

LLM Context evolves from a lineage of AI-assisted development tools:

- This project succeeds [LLM Code Highlighter](https://github.com/restlessronin/llm-code-highlighter), a TypeScript library I developed for IDE integration.
- The concept originated from my work on [RubberDuck](https://github.com/rubberduck-ai/rubberduck-vscode) and continued with later contributions to [Continue](https://github.com/continuedev/continuedev).
- LLM Code Highlighter was heavily inspired by [Aider Chat](https://github.com/paul-gauthier/aider). I worked with GPT-4 to translate several Aider Chat Python modules into TypeScript, maintaining functionality while restructuring the code.
- This project uses tree-sitter [tag query files](src/llm_context/highlighter/tag-qry/) from Aider Chat.
- LLM Context exemplifies the power of AI-assisted development, transitioning from Python to TypeScript and back to Python with the help of GPT-4 and Claude-3.5-Sonnet.

I am grateful for the open-source community's innovations and the AI assistance that have shaped this project's evolution.

I am grateful for the help of Claude-3.5-Sonnet in the development of this project.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
