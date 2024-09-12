# LLM Context

LLM Context is a Python-based tool designed to streamline the process of sharing code context with Large Language Models (LLMs) *using a standard Chat UI*. It allows developers to easily select, format, and copy relevant code snippets and project structure information, enhancing the quality of interactions with AI assistants in coding tasks.

This project was developed with significant input from Claude 3 Opus and Claude 3.5 Sonnet. All of the code that makes it into the repo is human curated (by me 😇, [@restlessronin](https://github.com/restlessronin)).

## Features

- **File Selection**: Offers a command-line interface for selecting files from your project.
- **Intelligent Ignoring**: Respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting.
- **Optional Technical Summary**: Allows inclusion of a markdown file summarizing the project's technical aspects.

## Installation

### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is a tool to help you install and run end-user CLI applications written in Python.

1. If you haven't installed pipx yet, follow the installation instructions in the pipx documentation.
2. Once pipx is installed, you can install LLM Context:
   ```
   pipx install llm-context
   ```

This will install LLM Context in an isolated environment and make its commands available in your shell.

## Usage

LLM Context offers several command-line tools, each designed for a specific task. All commands should be run from the root directory of your project, where the primary `.gitignore` file is located.

Here are the main commands:

   ```sh
   # Select all files which are not gitignored
   lcc-select
   # Generate full context (including folder structure and summary), using selected files
   lcc-gencontext
   # Generate full text contents from a list of paths in the clipboard
   lcc-genfiles
   ```

### Typical workflow

Let's say that you are collaborating with an LLM on a code repo. Use a system or custom prompt similar to [this `custom-prompt.md`](.llm-context/custom-prompt.md).

#### Provide context for your chat.

1. Navigate to your project's root directory in the terminal.
2. Edit the project configuration file `.llm-context/config.json` to add any files to the "gitignores" key that should be in git but may not be useful for code context (e.g., "LICENSE" and "poetry.lock", maybe even "README.md").
3. Run `lcc-select` to choose the files you want to include in your context. You can look at `.llm-context/scratch.json` to see what files are currently selected. If you prefer, you can edit the scratch file directly, before the next step.
4. Run `lcc-gencontext` to generate and copy the full text of all selected files, the folder structure diagram and the technical summary of the project (if available).
5. Paste the context into the first message of your conversation with the LLM, or equivalently into a Claude project file.

#### Respond to LLM requests for files

1. The LLM will request a list of files in a markdown block quote.
2. Select the block and copy into the clipboard
3. Run `lcc-genfiles` to copy the text context of the requested files into the clipboard (thus replacing it's original contents - the file list).
4. Paste the file content list into the next user message in the chat.
   
## Technical Summary

LLM Context supports an optional technical summary feature, although **its utility is currently unclear**. This feature allows you to include a markdown file that provides project-specific information that may not be easily inferred from the code alone. To use this feature:

1. Create a markdown file in your `.llm-context` folder (e.g., `.llm-context/tech-summary.md`).
2. In your `.llm-context/config.json` file, set the `summary_file` key to the name of your summary file:
   ```json
   {
     "summary_file": "tech-summary.md"
   }
   ```
If the key is missing or null, no summary will be included in the context.

The summary can include information like architectural decisions, non-obvious performance considerations, or future plans. For example:
- "We chose a microservices architecture to allow for independent scaling of components."
- "The `process_data()` function uses custom caching to optimize repeated calls with similar inputs."
- "The authentication system is slated for an overhaul in Q3 to implement OAuth2."

When you run `lcc-gencontext`, this summary will be included after the folder structure diagram in the generated context.

For an example of a technical summary, you can refer to the [`tech-summary.md` file for this repository](.llm-context/tech-summary.md).

## Project Structure

```
└── llm-context.py
    ├── .gitignore
    ├── .llm-context
    │   ├── .gitignore
    │   ├── config.json
    │   ├── custom-prompt.md
    │   ├── tech-summary.md
    │   └── templates
    │       ├── full-context.j2
    │       └── sel-file-contents.j2
    ├── LICENSE
    ├── MANIFEST.in
    ├── README.md
    ├── poetry.lock
    ├── pyproject.toml
    ├── src
    │   └── llm_context
    │       ├── __init__.py
    │       ├── config_manager.py
    │       ├── context_generator.py
    │       ├── file_selector.py
    │       ├── folder_structure_diagram.py
    │       ├── git_ignorer.py
    │       ├── path_converter.py
    │       ├── pathspec_ignorer.py
    │       ├── template.py
    │       └── templates
    │           ├── full-context.j2
    │           └── sel-file-contents.j2
    └── tests
        ├── test_path_converter.py
        └── test_pathspec_ignorer.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.