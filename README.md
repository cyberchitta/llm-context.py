# LLM Code Context

LLM Code Context is a Python-based tool designed to streamline the process of sharing code context with Large Language Models (LLMs). It allows developers to easily select, format, and copy relevant code snippets and project structure information, enhancing the quality of interactions with AI assistants in coding tasks.

This project was developed with significant input from Claude 3 Opus and Claude 3.5 Sonnet. All of the code that makes it into the repo is human curated (by me 😇).

## Features

- **File Selection**: Offers both command-line and graphical user interfaces for selecting files from your project.
- **Intelligent Ignoring**: Respects `.gitignore` rules and additional custom ignore patterns to exclude irrelevant files.
- **Customizable Output**: Uses Jinja2 templates for flexible formatting of the selected code context.
- **Folder Structure Visualization**: Generates a textual representation of your project's folder structure.
- **Clipboard Integration**: Automatically copies the generated context to your clipboard for easy pasting.
- **Configuration Management**: Supports user-specific and project-specific configurations for a tailored experience.

## Installation

### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is a tool to help you install and run end-user applications written in Python.

1. If you haven't installed pipx yet, follow the installation instructions in the pipx documentation.
2. Once pipx is installed, you can install LLM Code Context:
   ```
   pipx install llm-code-context
   ```

This will install LLM Code Context in an isolated environment and make its commands available in your shell.

## Usage

LLM Code Context provides several command-line entry points for different functionalities:

1. Select files (CLI):
   ```
   lcc-select
   ```

2. Select files (GUI):
   ```
   lcc-ui-select
   ```

3. Generate context from selected files:
   ```
   lcc-genfiles
   ```

4. Generate folder structure diagram:
   ```
   lcc-dirtree
   ```

Typical workflow:

1. Run `lcc-select` or `lcc-ui-select` to choose the files you want to include in your context.
2. Run `lcc-genfiles` to process the selected files and copy the formatted context to your clipboard.
3. Paste the context into your conversation with the LLM.

## Configuration

LLM Code Context uses three configuration files:

1. User Configuration (`~/.llm-context/config.json`). Example:
```json
{
  "templates_path": "/path/to/your/templates"
}
```

2. Project Configuration (`.llm-context/config.json` in your project root). Example:
```json
{
  "template": "all-file-contents.j2",
  "gitignores": [".git", "node_modules"],
  "root_path": "/path/to/your/project"
}
```

3. Scratch Configuration (`.llm-context/scratch.json` in your project root). Example:
   - Keeps track of the currently selected files.

You can edit these files manually or use the provided interfaces to update them.

## Project Structure

```
llm-code-context/
├── src/
│   └── llm_code_context/
│       ├── __init__.py
│       ├── config_manager.py
│       ├── context_generator.py
│       ├── file_selector.py
│       ├── file_selector_ui.py
│       ├── folder_structure_diagram.py
│       ├── gitignore_parser.py
│       ├── pathspec_ignorer.py
│       └── template_processor.py
├── templates/
│   └── all-file-contents.j2
├── tests/
│   └── test_pathspec_ignorer.py
├── .gitignore
├── README.md
├── poetry.lock
└── pyproject.toml
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.