# LLM Context

LLM Context is a tool designed to help developers efficiently copy and paste relevant code context into Large Language Model (LLM) chats. It leverages `.gitignore` patterns for smart file selection and uses the clipboard for seamless integration with LLM interfaces.

> **Note on AI Assistance**: This project was developed in collaboration with Claude-3.5-Sonnet. LLM Context itself was used during development to share code context with Claude in project mode. All of the code that makes it into the repo is human curated (by me 😇, @restlessronin).

## Key Features

- **Intelligent File Selection**: Respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting into LLM chats.
- **Code Structure Visualization**: Generates outlines of selected files to provide a quick overview of code structure.
- **Customizable Ignore Patterns**: Allows additional ignore patterns to be specified, giving you fine-grained control over what's included in the context.

## Installation

Use [pipx](https://pypa.github.io/pipx/) to install LLM Context:

```
pipx install llm-context
```

## Basic Usage

LLM Context provides several commands for file selection, context generation, and project visualization:

1. `lc-sel-full`: Select files for full content inclusion
2. `lc-context`: Generate and copy context to clipboard
3. `lc-clipfiles`: Generate full file content for files listed in the clipboard

### Quick Start

1. Navigate to your project's root directory.
2. Run `lc-sel-full` to select files for full content inclusion.
3. Run `lc-context` to generate and copy the context to your clipboard.
4. Paste the generated context into your LLM chat.

For smaller repositories, it's often better to include full contents for all files rather than using outlines. The `lc-sel-outline` command is more useful for larger projects where including all file contents might exceed the LLM's context window.

For more detailed instructions on customizing ignore patterns, handling LLM file requests, and using outlines for larger projects, please refer to our [Usage Guide](docs/usage.md).

## Typical Workflow

1. Navigate to your project's root directory.
2. (Optional) Edit `.llm-context/config.json` to add custom ignore patterns.
3. Run `lc-sel-full` to choose files for context.
4. Run `lc-context` to generate the context.
5. Paste the generated context into your LLM chat, Claude Project, or GPT Knowledge Source.
6. Inform the LLM about the presence and nature of the context you've provided, most likely via the System or Custom prompt.

### Handling LLM File Requests

When the LLM requests specific files:

1. Copy the LLM's file request (typically in a markdown block) to your clipboard.
2. Run `lc-clipfiles` to generate the content of the requested files.
3. Paste the generated file contents back into your chat with the LLM.

## Large Repositories and Outlining

For larger repositories, LLM Context uses a combination of full file content and file outlines to provide a comprehensive yet manageable context:

- Full content is included for key files that require detailed analysis.
- Outlines are provided for less critical files or those that are too large for full inclusion.

This approach allows you to provide context for more files without exceeding the LLM's context window limit. For these larger projects, you can use the `lc-sel-outline` command after `lc-sel-full` to select files for outline inclusion.

**Note:** The outlining feature currently supports the following programming languages:
C, C++, C#, Elisp, Elixir, Elm, Go, Java, JavaScript, OCaml, PHP, Python, QL, Ruby, Rust, and TypeScript.

Files in unsupported languages will not be outlined and will be excluded from the outline selection. We're continuously working to expand language support for the outlining feature.

The workflow and commands for large repositories are still being refined. We welcome your feedback and experiences using LLM Context with larger codebases, especially regarding the effectiveness of the outlining feature and language support.

### Feedback and Contributions

LLM Context is an evolving tool, and we're continuously working to improve its functionality, especially for larger repositories and expanding language support. If you encounter any issues, have suggestions for improvements, or want to share your experience using the tool, please don't hesitate to:

- Open an issue on our GitHub repository
- Submit a pull request with proposed changes

Your feedback is invaluable in helping us enhance LLM Context for all users. We're particularly interested in hearing about your experiences with:

- Using the tool on large repositories
- The effectiveness of the outline feature
- Language support for the outlining feature
- Any workflow improvements you'd suggest

Together, we can make LLM Context an even more powerful tool for developers working with LLMs.

## Advanced Usage

For more detailed information on customizing ignore patterns, manually editing the selected file list, and using outlines for larger projects, please refer to our [Usage Guide](docs/usage.md).

## Acknowledgments

LLM Context has evolved from several projects and influences:

- This project is a successor to [LLM Code Highlighter](https://github.com/restlessronin/llm-code-highlighter), a TypeScript library developed for use in IDEs like VS Code.
- LLM Code Highlighter was inspired by [Aider Chat](https://github.com/paul-gauthier/aider), particularly its [RepoMap](https://aider.chat/docs/repomap.html) functionality.
- The original concept grew out of a project for [RubberDuck](https://github.com/rubberduck-ai/rubberduck-vscode) and was later used for [Continue](https://github.com/continuedev/continuedev).
- LLM Code Highlighter included functionality for ranking and highlighting tags, based on a translation of Aider Chat's Python code to TypeScript (with the help of Chat-GPT-4). This functionality is not yet implemented in LLM Context.
- The outlining functionality, independently developed in LLM Code Highlighter, has been moved to this project.
- Parts of the code in LLM Context were translated from TypeScript to Python with Claude-3.5-Sonnet's help, bringing the project full circle (Python -> TypeScript -> Python).
- This project currently uses the tree-sitter [tag query files](src/llm_context/highlighter/tag-qry/) from Aider Chat.

We are grateful for the open-source community and the innovations that have influenced this project's development.

I am grateful for the help of Claude-3.5-Sonnet in the development of this project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.