# LLM Context User Guide

## Table of Contents

1. [Quick Start](#quick-start)

   - [First Time Setup](#first-time-setup)
   - [Basic Workflow](#basic-workflow)
   - [Command Overview](#command-overview)
   - [Common Use Cases](#common-use-cases)

2. [Core Concepts](#core-concepts)

   - [Project Configuration](#project-configuration)
   - [Files and Directories](#files-and-directories)
   - [State Management](#state-management)
   - [Profiles Overview](#profiles-overview)

3. [Configuration](#configuration)

   - [Configuration Files](#configuration-files)
   - [Profile Configuration](#profile-configuration)
   - [Template System](#template-system)

4. [Command Reference](#command-reference)

   - [lc-init](#lc-init)
   - [lc-set-profile](#lc-set-profile-profile-name)
   - [lc-sel-files](#lc-sel-files)
   - [lc-sel-outlines](#lc-sel-outlines)
   - [lc-context](#lc-context)
   - [lc-prompt](#lc-prompt)
   - [lc-clip-files](#lc-clip-files)
   - [lc-changed](#lc-changed)
   - [lc-outlines](#lc-outlines)

5. [Advanced Features](#advanced-features)

   - [Code Outlining](#code-outlining)
   - [Performance Optimization](#performance-optimization)

6. [Workflows](#workflows)

   - [Direct LLM Integration (MCP)](#direct-llm-integration-mcp)
   - [Chat Interface Usage](#chat-interface-usage)
   - [Project Knowledge Base](#project-knowledge-base)
   - [Custom GPT Integration](#custom-gpt-integration)

7. [Best Practices](#best-practices)

   - [Project Organization](#project-organization)
   - [Profile Management](#profile-management)
   - [Performance Tips](#performance-tips)

8. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)

## Quick Start

### First Time Setup

1. Navigate to your project's root directory. The project must have a `.gitignore` file.

2. Initialize LLM Context:

   ```bash
   lc-init
   ```

   This creates the `.llm-context` directory with default configuration files.

3. The default "code" profile is ready to use. For specialized needs, you can customize settings in `.llm-context/config.yaml`.

### Basic Workflow

1. Select files to include in your context:

   ```bash
   lc-sel-files
   ```

   This uses your `.gitignore` and profile settings to choose relevant files.

2. Generate and copy context to clipboard:

   ```bash
   lc-context
   ```

3. Paste the context into your LLM chat interface:

   - For Claude Projects/Custom GPTs: Use the knowledge section
   - For regular chats: Use `lc-set-profile code-prompt` first to include guiding instructions

4. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-clip-files`
   - Paste the new content back to the LLM

### Command Overview

Core commands you'll use frequently:

- `lc-init`: Set up LLM Context in your project
- `lc-set-profile <name>`: Switch between different profile configurations
- `lc-sel-files`: Select files for full content inclusion
- `lc-sel-outlines`: Select files for structural outline generation
- `lc-context`: Generate and copy context to clipboard
- `lc-clip-files`: Process file requests from the LLM

### Common Use Cases

1. Code Projects:

   - Use default "code" profile
   - Run `lc-sel-files` to include source code
   - Optional: Use `lc-sel-outlines` for structural overview

2. Documentation Projects:

   - Switch to documentation focus: `lc-set-profile copy`
   - Select content: `lc-sel-files`
   - Good for markdown/text collections

3. Web Projects:
   - Works well with both frontend and backend code
   - Can include HTML, JavaScript, and content files
   - Useful for reviewing site structure and content

## Core Concepts

### Project Configuration

LLM Context uses a layered configuration approach:

1. Project Root

   - Must contain `.gitignore`
   - All paths are relative to this directory

2. Configuration Directory (`.llm-context/`)

   - `config.yaml`: Main configuration file
   - `lc-project-notes.md`: Project-specific notes
   - `lc-prompt.md`: Prompt
   - `templates/`: Template files
   - `curr_ctx.yaml`: Current context state

3. User Configuration
   - `~/.llm-context/lc-user-notes.md`: User specific notes

### Files and Directories

Standard project layout:

```
your-project/
├── .llm-context/
│   ├── config.yaml          # Main configuration
│   ├── lc-project-notes.md  # Project notes
│   ├── lc-prompt.md         # LLM Instructions
│   ├── curr_ctx.yaml        # Current state
│   └── templates/           # Template files
│       ├── lc-context.j2
│       ├── lc-files.j2
│       └── lc-highlights.j2
├── .gitignore               # Required
└── [project files]
```

### State Management

LLM Context maintains state in `curr_ctx.yaml`:

- Tracks selected files per profile
- Preserves selections between sessions
- Updates automatically with commands
- Records timestamp when context is generated to track file changes

### Profiles Overview

Profiles control how LLM Context handles your project:

1. File Selection

   - Which files to include/exclude
   - Full content vs outline selection
   - Media file handling

2. Presentation

   - Template selection
   - Notes inclusion
   - Output formatting

3. Built-in Profiles

   - `code`: "Default profile for software projects, selecting all code files while excluding media and git-related files."
   - `code-prompt`: "Extends 'code' by including LLM instructions from lc-prompt.md for guided interactions."
   - `code-file`: "Extends 'code' by saving the generated context to 'project-context.md.tmp' for external use."

## Configuration

### Configuration Files

#### config.yaml

Primary configuration file containing:

```yaml
# Template mappings
templates:
  context: "lc-context.j2"
  files: "lc-files.j2"
  highlights: "lc-highlights.j2"

# Profile definitions
profiles:
  code:
    gitignores:
      full_files:
        - ".git"
        - ".gitignore"
        - ".llm-context/"
        - "*.lock"
      outline_files:
        - ".git"
        - ".gitignore"
        - ".llm-context/"
        - "*.lock"
    settings:
      no_media: true
      with_user_notes: false
    only-include:
      full_files:
        - "**/*"
      outline_files:
        - "**/*"
```

#### Notes Files

1. Project Notes (`lc-project-notes.md`)

   - Project-specific documentation
   - Created at initialization
   - User-maintained
   - Included in context by default

2. User Notes (`~/.llm-context/lc-user-notes.md`)
   - Personal/global notes
   - Optional inclusion via profile settings
   - Not project-specific

#### Templates Directory

Contains Jinja2 templates controlling output format:

- `lc-context.j2`: Main context format
- `lc-files.j2`: File content format
- `lc-highlights.j2`: Code outline format

Warning: Files prefixed with `lc-` may be overwritten during updates. For customization:

1. Create new files with different prefixes
2. Update references in `config.yaml`
3. Keep original files as reference

### Profile Configuration

Profiles control how files are selected and context is generated. Each profile combines:

- Repository .gitignore patterns (always active)
- Additional exclusion patterns from profile's gitignores
- Optional inclusion patterns to restrict file selection
- An optional `description` field to document the profile’s purpose

Important: The `.git` directory should always be included in your profile's gitignores patterns since it isn't typically in .gitignore files but should always be excluded from context generation.

Here's a complete example:

```yaml
profiles:
  code: # Default profile included with LLM Context
    description: "Default profile for software projects, selecting all code files while excluding media and git-related files."
    gitignores:
      full_files:
        - ".git"
        - ".gitignore"
        - ".llm-context/"
        - "*.lock"
      outline_files:
        - ".git"
        - ".gitignore"
        - ".llm-context/"
        - "*.lock"
    settings:
      no_media: true
      with_user_notes: false
    only-include:
      full_files:
        - "**/*"
      outline_files:
        - "**/*"
  code-prompt: # Built-in profile that adds LLM instructions
    description: "Extends 'code' by including LLM instructions from lc-prompt.md for guided interactions."
    base: "code" # Inherits from code profile
    prompt: "lc-prompt.md" # Adds prompt template to output
    settings:
      with_prompt: true
  code-file: # Built-in profile for file output
    description: "Extends 'code' by saving the generated context to 'project-context.md.tmp' for external use."
    base: "code"
    settings:
      context_file: "project-context.md.tmp"
```

#### Settings Reference

Profile settings control behavior:

```yaml
settings:
  # Exclude binary/media files from folder structure
  no_media: true
  # Include user notes from ~/.llm-context/lc-user-notes.md
  with_user_notes: false
  # Write lc-context to file (relative to current directory) in addition to clipboard
  context_file: "context.md.tmp"
```

#### File Selection Patterns

Two types of pattern collections:

1. Additional Exclusions (gitignores):

```yaml
gitignores:
  # Files excluded from full content
  full_files:
    - ".git"
    - "*.lock"
  # Files excluded from outlines
  outline_files:
    - ".git"
    - "*.lock"
```

2. Optional Restrictions (only-include):

```yaml
only-include:
only-include:
  # Only include these in full content
  full_files:
    - "**/*"  # Include everything not excluded
  # Only include these in outlines
  outline_files:
    - "**/*.py"
    - "**/*.js"  # Restrict outlines to Python and JS
```

#### Example Custom Profiles

1. Documentation Focus:

```yaml
profiles:
  docs:
    gitignores:
      full_files:
        - ".git"
        - ".llm-context/"
        - "*.lock"
    settings:
      no_media: true
      with_user_notes: true # Include personal notes
    only-include:
      full_files:
        - "**/*.md"
        - "**/*.txt" # Documentation files
        - "README*" # Project info
        - "LICENSE*"
```

2. Source Files Only:

```yaml
profiles:
  source:
    gitignores:
      full_files:
        - ".git"
        - ".llm-context/"
        - "*.lock"
    settings:
      no_media: true
    only-include:
      full_files:
        - "src/**/*.py" # Python source
        - "tests/**/*.py" # Test files
        - "pyproject.toml" # Project configuration
    prompt: "lc-prompt.md"
```

#### Profile Inheritance

Profiles can extend others using the `base` field:

```yaml
profiles:
  base-docs:
    gitignores:
      full_files:
        - ".git"
        - ".llm-context/"
        - "*.lock"
    settings:
      no_media: true
    only-include:
      full_files:
        - "**/*.md"
  docs-with-notes:
    base: "base-docs"
    settings:
      no_media: true
      with_user_notes: true # Add personal notes
  with-file:
    base: "code"
    settings:
      no_media: true
      with_user_notes: false
      context_file: "context.md.tmp" # Save to file as well as clipboard
```

The inheritance system allows you to:

- Create base profiles for common settings
- Override specific fields in derived profiles
- Mix and match configurations for different use cases

### Template System

#### Core Templates

1. Context Template (`lc-context.j2`)
   Controls overall output structure:

```jinja
{% if prompt %}
{{ prompt }}
{% endif %}

# Repository Content: **{{ project_name }}**

## Structure
{{ folder_structure_diagram }}

{% if files %}
## Files
{% include 'lc-files.j2' %}
{% endif %}
```

2. Prompt Template (`lc-prompt.md`)
   Sets LLM behavior:

```markdown
## Persona

[LLM role definition]

## Guidelines

[Behavior instructions]

## Response Structure

[Output format]
```

#### Customization

To customize templates:

1. Create new template with different prefix:

```bash
cp .llm-context/templates/lc-context.j2 .llm-context/templates/my-context.j2
```

2. Update config.yaml:

```yaml
templates:
  context: "my-context.j2"
```

3. Modify new template as needed

#### Variables Reference

Available in templates:

- `project_name`: Repository name
- `folder_structure_diagram`: Directory tree
- `files`: List of file contents
- `highlights`: Code outlines
- `prompt`: Prompt template content
- `project_notes`: Project notes content
- `user_notes`: User notes content

## Command Reference

### lc-init

Initializes LLM Context in your project.

- Creates `.llm-context` directory
- Sets up default configuration files
- Requires `.gitignore` file in project root
- Safe to run multiple times

### lc-set-profile profile-name

Switches the active profile.

```bash
lc-set-profile code        # Switch to default code profile
lc-set-profile code-prompt # Switch to code profile with prompt
lc-set-profile web        # Switch to web profile (if configured)
```

### lc-sel-files

Selects files for full content inclusion.

- Uses active profile's configuration
- Respects `.gitignore` patterns
- Updates `curr_ctx.yaml` with selections

### lc-sel-outlines

Selects files for structural outline generation.

- Only available with [outline] extra
- Limited to supported languages
- Excludes files already selected for full content

### lc-context

Generates context and copies to clipboard.

- Combines full content and outlines
- Applies active profile's templates
- Includes file structure diagram

### lc-prompt

Generates project-specific instructions suitable for "System Prompts" or "Custom Instructions" sections in LLM chat interfaces.

- Outputs formatted instructions from your profile's prompt template
- Includes user notes if enabled in profile settings
- Designed for:
  - Claude Projects' "Project Instructions" section
  - Custom GPT "System Prompts"
  - Similar "Custom Instruction" sections in other LLM interfaces
  - Setting up consistent project-specific LLM behavior

### lc-clip-files

Processes file requests from clipboard.

- Reads file paths from clipboard
- Generates formatted content
- Copies result to clipboard

### lc-changed

Lists files that have been modified since the context was generated:

- Uses timestamp from when context was generated
- Helps track changes during conversation
- Useful for reviewing changes before updates
- Respects current profile's file selection patterns

### lc-outlines

Generates smart outlines for all outline-eligible code files and copies to clipboard.

- Uses active profile's configuration for file selection
- Shows important code definitions (classes, functions, methods)
- Helps understand code structure without full content
- Useful for:
  - Getting a quick overview of a repository's structure
  - Identifying key components without reading all code
  - Sharing code organization with LLMs

The outline displays:

- Definition lines marked with █
- Context lines marked with │
- Skipped sections indicated with ⋮...

## Advanced Features

### Code Outlining

#### Installation

```bash
uv tool install "llm-context[outline]"
```

#### Configuration

Control outline behavior in profiles:

```yaml
profiles:
  with-outlines:
    gitignores:
      full_files:
        - ".git"
        - "*.lock"
      outline_files:
        - ".git"
        - "*.lock"
    only-include:
      full_files:
        - "**/*"
      outline_files:
        - "**/*.py"
        - "**/*.js"
```

#### Language Support

Currently supported languages:

- C, C++, C#
- Elisp, Elixir, Elm
- Go
- Java, JavaScript
- PHP, Python
- Ruby, Rust
- TypeScript

#### Limitations

- Language support is fixed
- Unsupported files are excluded
- May impact context size

### Performance Optimization

#### Context Size Management

1. Balance full content and outlines:

   - Use outlines for large files
   - Select key files for full content
   - Consider LLM context limits

2. File Selection Strategies:
   - Start with core files
   - Add related files as needed
   - Use outlines for context

#### Profile Optimization

1. Efficient Patterns:

```yaml
# Optimize pattern matching
gitignores:
  full_files:
    - "node_modules/**"
    - "*.min.*"
  outline_files:
    - "node_modules/**"
```

2. Language-Specific Profiles:

```yaml
# Python project optimization
profiles:
  python-opt:
    only-include:
      full_files:
        - "**/main.py"
        - "**/core/*.py"
      outline_files:
        - "**/*.py"
```

3. Custom Combinations:

```yaml
# Mixed content optimization
profiles:
  web-opt:
    only-include:
      full_files:
        - "**/index.html"
        - "**/main.js"
        - "**/*.md"
      outline_files:
        - "**/*.js"
        - "**/*.ts"
```

## Workflows

### Direct LLM Integration (MCP)

1. Configure Claude Desktop:

```jsonc
{
  "mcpServers": {
    "CyberChitta": {
      "command": "uvx",
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

2. Start working with your project in two simple ways:

   - Say: "I would like to work with my project"
     Claude will ask you for the project root path.

   - Or directly specify: "I would like to work with my project /path/to/your/project"
     Claude will automatically load the project context.

3. Available MCP Tools:

   | Tool Name | Description |
   |-----------|-------------|
   | lc-project-context | Generates a full repository overview with file contents and outlines |
   | lc-get-files | Retrieves specific files from the project |
   | lc-list-modified-files | Lists files modified since a specific timestamp |
   | lc-code-outlines | Returns smart outlines for all code files in the repository (requires [outline] extra) |

   Note: The `lc-code-outlines` tool is only available if you have installed llm-context with the [outline] extra:
   ```bash
   uv tool install "llm-context[outline]"

4. Usage:
   - Files requested via MCP are automatically processed
   - No manual clipboard operations needed
   - Maintains conversation context

### Chat Interface Usage

1. Standard Chat:

```bash
lc-set-profile code-prompt  # Include instructions
lc-context             # Generate and copy
# Paste into chat
```

2. File Requests:

```bash
# Copy file list from LLM
lc-clip-files
# Paste result back
```

### Project Knowledge Base

1. Claude Projects:

   - Use `lc-set-profile code`
   - Generate context with `lc-context`
   - Paste into knowledge section
   - Update as project evolves

2. Knowledge Maintenance:
   - Regular context updates
   - Consistent profile usage
   - Documentation in project notes

### Custom GPT Integration

1. Initial Setup:

   - Generate context with `lc-context`
   - Add to GPT knowledge base
   - Include prompt if needed

2. Ongoing Usage:
   - Update knowledge as needed
   - Use `lc-clip-files` for new files
   - Maintain consistent context

## Best Practices

### Project Organization

- Keep `.llm-context/config.yaml` in version control
- Ignore `curr_ctx.yaml` in git
- Document any custom templates you create

### Profile Management

- Start with built-in profiles, customize as needed
- Document profile purposes in a comment in config.yaml
- Share working profiles with your team

### Performance Tips

1. Monitor and Optimize File Selection:

   - Review actual selected files after `lc-sel-files`
   - Remove large generated files, logs, etc.
   - Adjust profile patterns based on what you see

2. Check Context Size:

   - Review the actual context after pasting into chat
   - Look for unnecessary large files or duplicates
   - Consider using outlines for large files

3. Efficient Updates:
   - Use `lc-clip-files` for targeted file access
   - Update context when project structure changes
   - Switch profiles based on your current task

## Troubleshooting

### Common Issues

1. "GITIGNORE_NOT_FOUND" Error:

   - Create a `.gitignore` file in your project root
   - Even an empty file will work

2. Template Errors:

   - Don't modify files starting with `lc-`
   - Create your own templates with different names
   - Update references in config.yaml

3. No Files Selected:

   - Check your profile's gitignores and only-include patterns
   - Review `.gitignore` patterns
   - Try `lc-set-profile code` to use default profile

4. Outline Generation Not Working:

   - Ensure you installed with `uv tool install "llm-context[outline]"`
   - Check if your files are in supported languages
   - Make sure files aren't already selected for full content

5. Context Too Large:
   - Review selected files with `cat .llm-context/curr_ctx.yaml`
   - Adjust profile patterns to exclude large files
   - Use outlines instead of full content where possible
