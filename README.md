# LLM Context

LLM Context is a tool designed to help developers efficiently copy and paste relevant context from code repositories or text-based document collections into Large Language Model (LLM) chats. It leverages `.gitignore` patterns for smart file selection and uses the clipboard for seamless integration with LLM interfaces.

> **Note on AI Assistance**: This project was developed in collaboration with Claude-3.5-Sonnet. LLM Context itself was used during development to share code context with Claude in project mode. All of the code that makes it into the repo is human curated (by me 😇, @restlessronin).

## Key Features

- **Intelligent File Selection**: Respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting into LLM chats.
- **Code Structure Visualization**: Generates outlines of selected files to provide a quick overview of code structure.
- **Customizable Ignore Patterns**: Allows [additional ignore patterns to be specified](docs/usage.md#customizing-ignore-patterns), giving you fine-grained control over what's included in the context.
- **Versatile Content Support**: Works with both code repositories and collections of text-based documents.

## Installation

Use [pipx](https://pypa.github.io/pipx/) to install LLM Context:

```
pipx install llm-context
```

## Usage

### Quick Start and Typical Workflow

1. Navigate to your project's root directory.
2. (Optional) Edit `.llm-context/config.json` to [add custom ignore patterns](docs/usage.md#customizing-ignore-patterns).
3. Run `lc-sel-full` to select files for full content inclusion.
4. (Optional) Edit the selected file list. See the [Usage Guide](docs/usage.md#manually-editing-selected-files) for instructions.
5. Run `lc-context` to generate and copy the context to your clipboard.
6. Paste the generated context into your LLM chat, Claude Project, or GPT Knowledge Source.
7. Inform the LLM about the presence and nature of the context you've provided, [typically via the System or Custom prompt](docs/usage.md#prompt-for-llm).

### Handling LLM File Requests

When the LLM requests specific files:

1. Copy the LLM's file request (typically in a markdown block) to your clipboard.
2. Run `lc-clipfiles` to generate the content of the requested files.
3. Paste the generated file contents back into your chat with the LLM.

## Current Usage Patterns

1. **LLM Integration**: LLM Context has been primarily used to provide Project Knowledge in Claude and GPT Knowledge in OpenAI. It can also be used with vanilla chat interfaces, though this use case has been less explored.

2. **Project Types**: The tool has been successfully used with both code repositories and collections of text/markdown documents, making it versatile for various types of projects.

3. **Project Size**: LLM Context has been mainly used for projects where all files can be comfortably loaded into the LLM's context. Its usage for larger projects, where not all files would fit within the LLM's context window, has been limited and the workflow for such cases is less optimized.

We welcome feedback on how to improve the workflow for larger projects and other use cases.

## Large Repositories and Outlining

For larger repositories, LLM Context can use a combination of full file content and file outlines to provide a comprehensive yet manageable context:

- Full content is included for key files that require detailed analysis.
- Outlines are provided for less critical files or those that are too large for full inclusion.

This approach allows you to provide context for more files without exceeding the LLM's context window limit. For these larger projects, you can use the `lc-sel-outline` command after `lc-sel-full` to select files for outline inclusion.

**Note:** The outlining feature currently supports the following programming languages:
C, C++, C#, Elisp, Elixir, Elm, Go, Java, JavaScript, OCaml, PHP, Python, QL, Ruby, Rust, and TypeScript.

Files in unsupported languages will not be outlined and will be excluded from the outline selection.

### Feedback and Contributions

If you encounter any issues, have suggestions for improvements, or want to share your experience using the tool, please open an issue on our GitHub repository or submit a pull request with proposed changes.

## Advanced Usage

For more detailed information on customizing ignore patterns, manually editing the selected file list, crafting prompts for LLMs, and handling file requests, please refer to our [Usage Guide](docs/usage.md).

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