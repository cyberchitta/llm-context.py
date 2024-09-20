# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-09-20

Initial public release.

### Added
- feat: Implement core functionality for generating LLM context from code repositories
- feat: Add support for multiple programming languages
- feat: Integrate smart file selection using `.gitignore` patterns
- feat: Implement clipboard integration for seamless LLM chat interaction
- feat: Add file outlining capabilities for large projects
- feat: Create command-line interface with multiple commands:
  - `lc-init`: Initialize LLM Context for a project
  - `lc-sel-files`: Select files for full content inclusion
  - `lc-sel-outlines`: Select files for outline inclusion
  - `lc-context`: Generate and copy context to clipboard
  - `lc-read-cliplist`: Process LLM-requested files
- feat: Add `--with-prompt` flag to `lc-context` command for including default prompt
- feat: Implement customizable ignore patterns via `.llm-context/config.toml`
- feat: Add support for custom templates in `.llm-context/templates/`
- ci: Set up initial project structure and development environment
- docs: Create comprehensive README with usage instructions and examples
- docs: Add CHANGELOG for tracking project history