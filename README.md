# LLM Code Context

LLM Code Context is a Python-based tool designed to streamline the process of sharing code context with Large Language Models (LLMs). It allows developers to easily select, format, and copy relevant code snippets and project structure information, enhancing the quality of interactions with AI assistants in coding tasks.

This project was developed with significant input from Claude 3 Opus and Claude 3.5 Sonnet. All of the code that makes it into the repo is human curated (by me 😇, [@restlessronin](https://github.com/restlessronin)).

## Features

- **File Selection**: Offers a command-line interface for selecting files from your project.
- **Intelligent Ignoring**: Respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Customizable Output**: Uses Jinja2 templates for flexible formatting of the selected code context.
- **Folder Structure Visualization**: Generates a textual representation of your project's folder structure.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting.
- **Configuration Management**: Supports user-specific and project-specific configurations for a tailored experience.

## Installation

### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is a tool to help you install and run end-user CLI applications written in Python.

1. If you haven't installed pipx yet, follow the installation instructions in the pipx documentation.
2. Once pipx is installed, you can install LLM Code Context:
   ```
   pipx install llm-code-context
   ```

This will install LLM Code Context in an isolated environment and make its commands available in your shell.

## Usage

LLM Code Context offers various command-line tools, each designed for a specific task. All commands should be run from the root directory of your project, where the `.gitignore` file is located. This is crucial because:

1. The default file selection process starts from this root directory and selects all files that are not ignored by .gitignore rules.
2. It ensures that file selection and ignore rules are applied correctly and consistently.

Here are the main commands:

1. Select files:
   ```
   lcc-select
   ```

2. Generate context from selected files:
   ```
   lcc-genfiles
   ```

3. Generate folder structure diagram:
   ```
   lcc-dirtree
   ```

Typical workflow:

1. Navigate to your project's root directory in the terminal.
2. Edit the project configuration file `.llm-code-context/config.json` to add any files to the "gitignores" key that should be in git but may not be useful for code context (e.g., "LICENSE" and "poetry.lock", maybe even "README.md").
3. Run `lcc-select` to choose the files you want to include in your context. You can look at `.llm-code-context/scratch.json` to see what files are currently selected. If you prefer, you can edit the scratch file directly, before the next step.
4. Run `lcc-genfiles` to process the selected files and copy the formatted context to your clipboard.
5. Paste the context into your conversation with the LLM.

## Configuration

LLM Code Context uses three configuration files:

1. User Configuration (located in a platform-specific directory determined by `platformdirs`):
```json
{
  "templates_path": "/path/to/your/templates"
}
```

2. Project Configuration (`.llm-code-context/config.json` in your project root). Example:
```json
{
  "template": "all-file-contents.j2",
  "gitignores": [".git", "LICENSE"]
}
```

3. Scratch Configuration (`.llm-code-context/scratch.json` in your project root). Example:
   - Keeps track of the currently selected files.

You can edit these files manually or use the provided interfaces to update them.

## Project Structure

```
└── llm-code-context.py
    ├── .gitignore
    ├── .llm-code-context
    │   ├── .gitignore
    │   └── config.json
    ├── LICENSE
    ├── MANIFEST.in
    ├── README.md
    ├── poetry.lock
    ├── pyproject.toml
    ├── src
    │   └── llm_code_context
    │       ├── __init__.py
    │       ├── config_manager.py
    │       ├── context_generator.py
    │       ├── file_selector.py
    │       ├── folder_structure_diagram.py
    │       ├── git_ignorer.py
    │       ├── initializer.py
    │       ├── pathspec_ignorer.py
    │       ├── template_processor.py
    │       └── templates
    │           └── all-file-contents.j2
    └── tests
        └── test_pathspec_ignorer.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.