# LLM Context

LLM Context is a Python-based tool designed to streamline the process of sharing code context with Large Language Models (LLMs) using a standard Chat UI. It intelligently selects relevant files using `.gitignore` rules, generates comprehensive code context, and copies it directly to your clipboard for easy sharing with AI assistants.

> **Note on AI Assistance**: This project was developed with significant assistance from Claude-3.5-Sonnet. LLM Context itself was used during development to share code context with Claude in project mode. All of the code that makes it into the repo is human curated (by me 😇, @restlessronin).

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

## Usage

LLM Context offers flexibility in how you share your code context, depending on the size of your repository:

### For Small Repositories

If your entire repository fits within the LLM's context window:

1. Use `lc-gencontext` to generate and copy the full content of all selected files, including the folder structure.
2. Paste this complete context into your LLM chat.

### For Large Repositories

When the entire repo is too large to fit in the LLM's context window:

1. Use `lc-select` to distinguish which files go into the context in full form, and which are "outlined".
2. Use `lc-gencontext` to generate the folder structure, full contents of specified files and outlines of those specified as such.
3. When the LLM requests specific files, use `lc-files` to generate their full content.

## Main Commands

- `lc-select`: Choose files based on gitignore rules and custom patterns.
- `lc-gencontext`: Generate full context including folder structure, summary (if available), and contents of selected files.
- `lc-outlines`: Generate outlines of selected files.
- `lc-files`: Generate full text contents of specific files.
- `lc-clipfiles`: Generate full text contents of files listed in the clipboard.

## Typical Workflow

1. Navigate to your project's root directory.
2. (Optional) Edit `.llm-context/config.json` to add custom ignore patterns.
3. Run `lc-select` to choose files for context.
4. For small repos: Run `lc-gencontext`.
   For large repos: Run both `lc-gencontext` and `lc-outlines`, and combine their output.
5. Paste the generated context into your LLM chat, Claude Project, or GPT Knowledge Source.
6. Inform the LLM about the presence and nature of the context you've provided, most likely via the System or Custom prompt.

### Providing Files to LLM (for large repos)

1. When the LLM requests specific files, it will typically do so in a markdown block quote.
2. Copy the LLM's file request to your clipboard.
3. Run `lc-clipfiles` to generate the content of the requested files.
4. Paste the generated file contents back into your chat with the LLM.

This workflow allows for dynamic interaction with the LLM, providing initial context and responding to specific file requests as needed during the conversation.

## Advanced Usage

For more detailed information on customizing ignore patterns and manually editing the selected file list, please refer to our [Usage Guide](docs/USAGE.md).

## Acknowledgments

LLM Context has evolved from several projects and influences:

- This project is a successor to [LLM Code Highlighter](https://github.com/restlessronin/llm-code-highlighter), a TypeScript library developed for use in IDEs like VS Code.
- LLM Code Highlighter was inspired by [Aider Chat](https://github.com/paul-gauthier/aider), particularly its [RepoMap](https://aider.chat/docs/repomap.html) functionality.
- The original concept grew out of a project for [RubberDuck](https://github.com/rubberduck-ai/rubberduck-vscode) and was later used for [Continue](https://github.com/continuedev/continuedev).
- LLM Code Highlighter included functionality for ranking and highlighting tags, based on a translation of Aider Chat's Python code to TypeScript (with the help of Chat-GPT-4). This functionality is not yet implemented in LLM Context.
- The outlining functionality, developed in LLM Code Highlighter, has been moved to this project.
- Parts of the outlining and highlighting code in LLM Context were translated from TypeScript to Python with Claude-3.5-Sonnet's help, bringing the project full circle.
- This project currently uses the tree-sitter [tag query files](src/llm_context/highlighter/tag-qry/) from Aider Chat.

We are grateful for the open-source community and the innovations that have influenced this project's development. The evolution from ideas/code in Aider Chat to LLM Code Highlighter (via RubberDuck and Continue) to LLM Context demonstrates the iterative nature of software development and the value of building upon and adapting existing ideas.

I am grateful for the help of Claude-3.5-Sonnet in the development of this project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.