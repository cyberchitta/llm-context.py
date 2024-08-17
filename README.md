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
- **Optional Technical Summary**: Allows inclusion of a markdown file summarizing the project's technical aspects.

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

LLM Code Context offers several command-line tools, each designed for a specific task. All commands should be run from the root directory of your project, where the primary `.gitignore` file is located.

Here are the main commands:

   ```sh
   # Select files
   lcc-select
   # Generate context from selected files
   lcc-genfiles
   # Generate full context (including folder structure and summary)
   lcc-gencontext
   # Generate folder structure diagram:
   lcc-dirtree
   ```

Typical workflow:

1. Navigate to your project's root directory in the terminal.
2. Edit the project configuration file `.llm-code-context/config.json` to add any files to the "gitignores" key that should be in git but may not be useful for code context (e.g., "LICENSE" and "poetry.lock", maybe even "README.md").
3. Run `lcc-select` to choose the files you want to include in your context. You can look at `.llm-code-context/scratch.json` to see what files are currently selected. If you prefer, you can edit the scratch file directly, before the next step.
4. Run `lcc-genfiles` to process the selected files and copy the formatted context to your clipboard.
5. Paste the context into your conversation with the LLM.

For a more comprehensive context that includes the folder structure and technical summary:

6. Run `lcc-gencontext` to generate and copy the full context, including the folder structure diagram and the technical summary (if available).
   
## Technical Summary

LLM Code Context supports an optional technical summary feature, although **its utility is currently unclear**. This feature allows you to include a markdown file that provides project-specific information that may not be easily inferred from the code alone. To use this feature:

1. Create a markdown file in your project root (e.g., `tech-summary.md`).
2. In your `.llm-code-context/config.json` file, set the `summary_file` key to the name of your summary file:
   ```json
   {
     "summary_file": "tech-summary.md"
   }
   ```

The summary can include information like architectural decisions, non-obvious performance considerations, or future plans. For example:
- "We chose a microservices architecture to allow for independent scaling of components."
- "The process_data() function uses custom caching to optimize repeated calls with similar inputs."
- "The authentication system is slated for an overhaul in Q3 to implement OAuth2."

When you run `lcc-gencontext`, this summary will be included after the folder structure diagram in the generated context.

## Project Structure

```
└── <bound method ConfigManager.project_root_path of <llm_code_context.config_manager.ConfigManager object at 0x104f0be00>>
    └── ..
        ├── .gitignore
        ├── .llm-code-context
        │   ├── .gitignore
        │   ├── claude-custom.md
        │   ├── config.json
        │   ├── scratch.json
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
        │   └── llm_code_context
        │       ├── __init__.py
        │       ├── config_manager.py
        │       ├── context_generator.py
        │       ├── file_selector.py
        │       ├── folder_structure_diagram.py
        │       ├── git_ignorer.py
        │       ├── pathspec_ignorer.py
        │       ├── template.py
        │       └── templates
        │           ├── full-context.j2
        │           └── sel-file-contents.j2
        └── tests
            └── test_pathspec_ignorer.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.