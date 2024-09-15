# LLM Context Technical Summary

LLM Context is a Python tool designed to streamline the process of sharing code context with Large Language Models (LLMs). It provides functionality for selecting, formatting, and copying relevant code snippets, project structure information, and code outlines.

## Key Architectural Decisions

1. **Modular design**: The project is structured into separate modules (e.g., file_selector, context_generator, highlighter) to promote separation of concerns and maintainability.

2. **Configuration management**: The ProjectSettings class handles both project-wide and user-specific configurations, supporting flexible customization.

3. **Template-based output**: Jinja2 templating is used for formatting output, allowing for easy customization of the generated context.

4. **GitIgnore-style pattern matching**: The project uses the pathspec library to implement .gitignore-style file exclusion patterns, ensuring consistency with common developer workflows.

5. **Command-line interface**: The tool is designed as a set of CLI commands, making it easy to integrate into existing development workflows.

6. **Abstract Syntax Tree (AST) parsing**: The project now incorporates tree-sitter for AST parsing, enabling more sophisticated code analysis and outline generation.

7. **Highlighting and outlining**: New functionality for generating code highlights and outlines has been added, allowing for more compact representation of large codebases.

## Noteworthy Development Practices

- Extensive use of class methods (e.g., `create()`) for object instantiation, promoting a cleaner API and easier testing.
- Type hints are used throughout the codebase, enhancing readability and enabling static type checking.
- Increased use of dataclasses for cleaner, more maintainable code structure.
- Functional programming principles are applied where appropriate, utilizing list comprehensions and generator expressions.

## Performance Considerations

- The file selection process is optimized to traverse directories efficiently, respecting ignore patterns at each level.
- AST parsing and analysis are designed to be efficient, allowing for quick generation of code outlines and highlights.

## Current Limitations

- The tool is primarily designed for local filesystem operations and may not support remote or cloud-based project structures.
- Language support for code parsing and highlighting is limited to those supported by tree-sitter.

## Unique Aspects

- Custom implementation of .gitignore semantics (GitIgnorer class) that respects nested .gitignore files within a project structure.
- Sophisticated code outlining feature that uses AST analysis to provide concise summaries of code structure.
- Flexible templating system allowing for customization of context output format.

This summary provides an overview of the project's architecture and design philosophy. Maintainers should update this summary when significant architectural changes are made to the project.