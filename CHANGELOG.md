# Changelog

All notable changes to this project will be documented in this file.

## [0.3.3] - 2025-06-03

### Bug Fixes
- Ensure UTF-8 encoding on Windows to prevent charmap codec errors
- Enhance final reminder to discourage unnecessary file requests
- Delete state store when referencing stale rule

### Documentation
- Add preferred workflow to README
- Add new "Full Context Magic" article to README
- Be precise about new format

### Features
- Emphasize checking context before requesting files
- Improve key file visibility in context diagrams
- Skip automatic outline selection when changing rules
- Add webp to ignores
- Improve clarity of context usage instructions

## [0.3.2] - 2025-04-03

### Bug Fixes
- Installation issue on linux where old versions are being installed
- Prevent overwriting rule files after state update

### Features
- Improve AI instructions in context templates

### Refactor
- Streamline lc-code rule content

## [0.3.1] - 2025-04-01

### Bug Fixes
- Remove unintended gitignores

### Documentation
- Improve context template instructions to prevent unnecessary file requests

### Refactor
- Remove hardcoded pattern lists and unused methods

## [0.3.0] - 2025-03-31

### Features
- Replace profiles with Markdown/YAML-based rules

## [0.2.18] - 2025-03-29

### Features
- Make context template instructions conditional on content
- Implement profile file and rule references

## [0.2.17] - 2025-03-25

### Features
- Integrate outline functionality into standard distribution
- Optimize diagram generation and add .git to default ignores

## [0.2.16] - 2025-03-24

### Features
- Replace no_media flag with pattern-based diagram_files filtering
- Reorganize profile structure with system profiles / base gitignore

### Refactor
- Remove unused folder structure diagram
- Replace profile settings with command parameters
- Remove unused highlighter functionality

### Mcp
- Clarify when to use lc-get-files in templates

## [0.2.15] - 2025-03-10

### Bug Fixes
- Clarify C/C++ implementation retrieval limitation in tool description

### Features
- Preserve custom profiles during config updates

## [0.2.14] - 2025-03-09

### Features
- Expose (MCP & CLI) definition implementation extraction capabilities
- Add explicit markers to prevent redundant context requests
- Use name line for outlines and highlights

## [0.2.13] - 2025-02-28

### Bug Fixes
- Fix hatch build problems

## [0.2.11] - 2025-02-27

### Bug Fixes
- Broken build updated

### Features
- Improve parser performance with caching
- Add code outlines command

## [0.2.10] - 2025-02-25

### Bug Fixes
- Broken resource update

## [0.2.9] - 2025-02-24

### BREAKING
- Switch configuration from TOML to YAML (customization in toml files has to be manually re-applied)

## [0.2.9] - 2025-02-24

### Bug Fixes
- Ensure profile switch updates file selection correctly

### Features
- Add profile descriptions for better usability
- Add .gitignore creation in .llm_context during init

## [0.2.8] - 2025-02-09

### Features
- Migrate to tree-sitter-language-pack

## [0.2.7] - 2025-02-01

### Features
- Add lc-prompt command to generate standalone prompts

## [0.2.6] - 2025-01-15

### Bug Fixes
- Don't update timestamps on selection
- Update list tools

### Features
- Add generation timestamp instructions in templates
- Add file modification tracking
- Prefix MCP tools with lc- for namespacing
- Try to avoid redundant use of project_context

### Refactor
- Refine MCP related instructions

## [0.2.2] - 2024-12-25

### Features
- Add absolute root path for get_files tool (for project / MCP interop)
- Replace folder structure diagram with flat diagram

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
- Remove erroneous '\*.scm' from gitignores in config.yaml

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
- Implement customizable ignore patterns via `.llm-context/config.yaml`
- Add support for custom templates in `.llm-context/templates/`
