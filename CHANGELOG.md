# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2024-12-17

### Bug Fixes
- Remove templates key
- Use system default profile in resolver

### Features
- Ensure file selection before context generation in MCP
- Add "*.tmp" to ignored files
- Add sample code-file profile
- Add file output support via profile settings

## [0.2.0] - 2024-12-06

### Bug Fixes

- Ensure correct profile persistence
- Handle missing prompt template gracefully
- Bad path in manifest
- Attempt to prevent duplicate context retrieval
- Update logging
- Attempt to prevent duplicate file retrievals
- Get server working again
- Add fallback logger for exception handling
- Keep using pipx until 'uv' tool is debugged
- Use ValueError for missing profile validation
- Bug introduced by warning key
- Missing argument
- Restore version map
- Remove erroneous '\*.scm' from gitignores in config.toml

### Features

- Make profile templates optional in storage
- Switch to tomlkit for better TOML handling
- Persist active profile selection in state file
- Add project notes with consistent naming for user/project notes
- Integrate MCP template for improved API context output
- Add personal notes support
- Use package version for MCP server initialization
- Add only-includes pattern filtering for file selection
- Implement context generation MCP endpoints
- Make tree-sitter dependency optional
- Add version command for installed package
- Partially tested switch from poetry to uv
- Add profile inheritance via base property
- Simplified config update
- Implement independent profiles with separate gitignores, templates, and settings
- Exclude non-text files based on extensions

### Refactor

- Renamed to profile_name for clarity
- Rename local
- Rename variables
- Moved function def to keep all commands together
- Remove redundant with_prompt setting
- Rename with_notes setting to with_user_notes for clarity
- Change user notes location to under home
- Rename settings -> spec
- Strip server code to essential
- Rename folder_structure_diagram.py to folder_diagram.py
- Restructure configuration and state management
- Move default profile to system state only
- Remove redundant with_logging decorator
- Add IGNORE_NOTHING constant for minimal gitignore patterns
- Renamed and reorganized classes
- Rename commands.py -> cli.py
- Rename classes, fix mypy, format
- Break import cycle by moving ExecEnv import into logging util
- Replace warnings with logging for user messages
- Replace print with logging
- Rename for accuracy
- Removed side effects for clean state management - many small renames and restructuring deltas
- Rename ContextConfig -> FilterDescriptor
- Remove summary file
- Make project root explicit
- Split system state from user config
- Add SystemState, ProfileTemplate, reorder classes
- Rename and restructure context generation classes

## [0.1.0] - 2024-09-20

Initial public release.

### Features

- Implement core functionality for generating LLM context from code repositories
- Add support for multiple programming languages
- Integrate smart file selection using `.gitignore` patterns
- Implement clipboard integration for seamless LLM chat interaction
- Add file outlining capabilities for large projects
- Create command-line interface with multiple commands:
  - `lc-init`: Initialize LLM Context for a project
  - `lc-sel-files`: Select files for full content inclusion
  - `lc-sel-outlines`: Select files for outline inclusion
  - `lc-context`: Generate and copy context to clipboard
  - `lc-read-cliplist`: Process LLM-requested files
- Add `--with-prompt` flag to `lc-context` command for including default prompt
- Implement customizable ignore patterns via `.llm-context/config.toml`
- Add support for custom templates in `.llm-context/templates/`
