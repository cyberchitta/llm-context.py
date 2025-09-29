# Changelog

All notable changes to this project will be documented in this file.

## [0.5.1] - 2025-09-29

### Bug Fixes
- Eliminate overlap between files_to_fetch and already_excerpted in missing_files
- Handle list[Excerpts] return type in missing_files method

### Features
- Add explicit file verification wording to prevent content assumptions
- Add natural failure principle to error handling guidelines

## [0.5.0] - 2025-09-15

### Bug Fixes

- Return list[Excerpts] from collector to handle multiple excerpt modes
- Clarify lc-missing instructions are for user execution not LLM
- Run sfc on svelte repo
- Template name
- Include template content when include_template_logic is true in SFC excerpter
- Correct YAML frontmatter delimiter in lc/exc-base.md
- Refine dev instructions
- Clarify that latest versions are included in lc-get-files message
- Corrected cli command names in create rule instructions

### Documentation

- Update user docs with new features

### Features

- Fix lc-missing examples to use actual sample data instead of placeholders
- Add excluded sections retrieval with -e parameter for non-outline excerpts
- Add processor-aware guidance for already excerpted files in missing-files template
- Remove unused missing-excerpted template and dependencies
- Validate excerpt-modes required for all rules and fast-fail on missing config
- Update rule framework for unified excerpting system with code outlining prominence
- Upgrade to tree-sitter 0.25 API with Query/QueryCursor
- Consolidate file selection into single lc-select command
- Unify context retrieval with lc-missing tool and update templates
- Refactor excerpts to excerpter-specific templates with explanations
- Clean and copy excerpter templates during project setup
- Add SFC excerpter for extracting script sections from Svelte/Vue files
- Replace outlining with unified excerpting system using tree-sitter wrapper
- Remove lc-project-context MCP tool

### Refactor

- Remove vue config pending test
- Rename SFC config to with-style and with-template for consistency
- Consolidate code outlining into canonical excerpter structure
- Rationalized naming
- Move get_excerpted logic to ContextGenerator.missing_excerpted with template
- Move get_files logic to ContextGenerator.missing_files with template
- Remove obsolete tools replaced by unified lc-missing
- Simplify tool descriptions even more
- Extract remaining CLI business logic to commands module
- Extract MCP business logic to commands module for CLI/MCP unification
- Replace MCP server with FastMCP, remove Pydantic boilerplate
- Keep header in main context
- Reorganize templates into lc/ folder structure without prefixes
- Changed cli command back to outlines
- Rename sfc class and mode, fix test
- Use modern resources api
- Rename Source field
- Simplify query path construction
- Shorten query file names
- Rename scm folder
- Reorganize project, propogate new excerpter architecture into templates

## [0.4.1] - 2025-08-29

### Bug Fixes

- Warn on multiple limit-to clauses, keep first patterns only
- Remove limit-to from lc/flt-base to prevent composition override

### Features

- Update ins-rule-framework to document limit-to composition behavior
- Emphasize short commits
- Clarify path format rules and improve minimal context guidance
- Short commit messages by default
- Explicit instruction to follow style guides

### Refactor

- Remove redundant name field from rule YAML frontmatter

## [0.4.0] - 2025-08-27

### Bug Fixes

- Sort file lists for consistent output and state storage
- Handle rule loading errors gracefully without stack traces
- Remove tool references when -nt flag is used
- Remove tool references when -nt flag is used
- Update rule name
- Bad character in tool name
- Use markdown content for instructions field instead of full rule processing
- Update obsolete init message to reference user guide
- Add tif to globs
- Use resources.files() API for subfolder resource access
- Check file modification time in lc-get-files
- Ensure context timestamps match between content and state storage
- Only update timestamps on actual context generation
- Search all rule selections for timestamp match in MCP tools
- Update rule creator to latest yaml
- Remove extra newline in rule serialization
- Clarify text
- Outline-supported file extensions replace language list
- Correct pathspec examples in lc-focus-common rule documentation
- Repair also-include patterns with proper traversal logic
- Remove deleted import
- Update handlers to remove deleted tool
- Update sort order with current fields
- Yaml updates to rules
- Revert formatting of yaml only files
- Remove incorrect path prefixing in rule_files method
- Improve focus help tool description
- Implement recursive rule composition with cycle detection
- Timestamp should be date only
- Eliminate bare exception
- Remove rule path from context
- Improve end prompt
- Resolve mypy type errors in mcp_tools.py
- Resolve Windows 'charmap' codec error with UTF-8 encoding
- Revert prior commit
- Ensure UTF-8 encoding on Windows to prevent charmap codec errors
- Enhance final reminder to discourage unnecessary file requests
- Revert to old behaviour
- Delete state store when referencing stale rule

### Documentation

- Complete rewrite to reflect systematic rule organization and actual usage patterns

### Features

- Clean up stale system rules during updates
- Improve rule resolution error handling and init process
- New rule for working with templates
- Add AI co-author attribution to commit message format
- Add coding style guidelines to base prompt
- Add explicit code generation gate to developer prompt
- Add section on imports
- Add modular code style guidelines
- Sort glob patterns
- Add .icns to filters
- Add nested .gitignore support with comprehensive tests
- Organize system rules in lc/ subfolder
- Add context-aware file retrieval to MCP tools
- Default to full overview in rule creation for better file discoverability
- Enhance focus instructions with file extensions and path format
- Remove context size functionality
- Remove created timestamp
- Add instructions field for composable rule instructions
- Replace files/outlines with unified filtering system
- Finer grained file exclusion filters
- Add lc-focus to config
- Add comprehensive rule semantics to lc-focus content
- Add lc-focus rule for comprehensive context reduction guidance
- Add context_size() method and improve lc-create-rule feedback
- Add cli for focus help
- Add lc-create-rule MCP tool with unified focus help instructions
- Add configurable overview modes (focused/full) to rules
- Rename lc-focus-help to lc-rule-create-instructions in MCP
- Simplify focus-help template to be fully autonomous
- Add lc-block-all filter rule for explicit file selection
- Standardize YAML formatting and add rule timestamp support
- Add focused context creation instructions
- Replace rule inheritance with composition system
- Add focused overview with hierarchical file display
- Add comprehensive archive format ignores to default gitignores
- Add user message indicator to context output
- Emphasize checking context before requesting files
- Improve key file visibility in context diagrams
- Skip automatic outline selection when changing rules
- Add webp to ignores
- Improve clarity of context usage instructions

### Refactor

- Clean up vague instructions in style rules
- Reorganize rules into systematic categories with kebab-case prefixes
- Simplify file modification check in lc-get-files
- Refine for clarity
- Update SYSTEM_RULES
- Rename lc-focus to lc-create-rule for clarity
- Standardize YAML keys to kebab-case and remove last-used serialization
- Eliminate duplication in focus help instructions and remove MCP create-rule tool
- Rename lc-overview-only to lc-no-files for clarity
- Rename lc-block-all to lc-overview-only for clarity
- Move rules to project context
- Unify context templates with tools_available flag
- Rename FlatDiagram to FullOverview for clarity
- Extract MCP tool definitions to centralized module

### Testing

- Add pathspec pattern tests for also-include functionality

## [0.3.4] - 2025-06-04

### Bug Fixes

- Resolve Windows 'charmap' codec error with UTF-8 encoding
- Revert prior commit

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
- Add "\*.tmp" to ignored files
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
