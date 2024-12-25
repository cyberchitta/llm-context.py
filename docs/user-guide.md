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
   - [lc-set-profile](#lc-set-profile-name)
   - [lc-sel-files](#lc-sel-files)
   - [lc-sel-outlines](#lc-sel-outlines)
   - [lc-context](#lc-context)
   - [lc-read-cliplist](#lc-read-cliplist)

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

3. The default "code" profile is ready to use. For specialized needs, you can customize settings in `.llm-context/config.toml`.

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
   - For regular chats: Use `lc-profile code-prompt` first to include guiding instructions

4. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-read-cliplist`
   - Paste the new content back to the LLM

### Command Overview

Core commands you'll use frequently:

- `lc-init`: Set up LLM Context in your project
- `lc-set-profile <name>`: Switch between different profile configurations
- `lc-sel-files`: Select files for full content inclusion
- `lc-sel-outlines`: Select files for structural outline generation
- `lc-context`: Generate and copy context to clipboard
- `lc-read-cliplist`: Process file requests from the LLM

### Common Use Cases

1. Code Projects:

   - Use default "code" profile
   - Run `lc-sel-files` to include source code
   - Optional: Use `lc-sel-outlines` for structural overview

2. Documentation Projects:

   - Switch to documentation focus: `lc-profile copy`
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

   - `config.toml`: Main configuration file
   - `lc-project-notes.md`: Project-specific notes
   - `lc-prompt.md`: Prompt
   - `templates/`: Template files
   - `curr_ctx.toml`: Current context state

3. User Configuration
   - `~/.llm-context/lc-user-notes.md`: User specific notes

### Files and Directories

Standard project layout:

```
your-project/
├── .llm-context/
│   ├── config.toml          # Main configuration
│   ├── lc-project-notes.md  # Project notes 
│   ├── lc-prompt.md         # LLM Instructions
│   ├── curr_ctx.toml        # Current state
│   └── templates/           # Template files
│       ├── lc-context.j2
│       ├── lc-files.j2
│       └── lc-highlights.j2
├── .gitignore               # Required
└── [project files]
```

### State Management

LLM Context maintains state in `curr_ctx.toml`:

- Tracks selected files per profile
- Preserves selections between sessions
- Updates automatically with commands

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
   - `code`: Default for software projects
   - `code-prompt`: Adds LLM instructions

## Configuration

### Configuration Files

#### config.toml

Primary configuration file containing:

```toml
# Template mappings
[templates]
context = "lc-context.j2"
files = "lc-files.j2"
highlights = "lc-highlights.j2"

# Profile definitions
[profiles.code]
gitignores = {
    full_files = [".git", ".gitignore", ".llm-context/", "*.lock"],
    outline_files = [".git", ".gitignore", ".llm-context/", "*.lock"]
}
settings = {
    no_media = true,
    with_user_notes = false
}
only-include = {
    full_files = ["**/*"],
    outline_files = ["**/*"]
}
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
2. Update references in `config.toml`
3. Keep original files as reference

### Profile Configuration

Profiles control how files are selected and context is generated. Each profile combines:

- Repository .gitignore patterns (always active)
- Additional exclusion patterns from profile's gitignores
- Optional inclusion patterns to restrict file selection

Important: The `.git` directory should always be included in your profile's gitignores patterns since it isn't typically in .gitignore files but should always be excluded from context generation.

Here's a complete example:

```toml
[profiles.code]  # Default profile included with LLM Context
gitignores = {
    full_files = [".git", ".gitignore", ".llm-context/", "*.lock"],
    outline_files = [".git", ".gitignore", ".llm-context/", "*.lock"]
}
settings = {
    no_media = true,
    with_user_notes = false
}
only-include = {
    full_files = ["**/*"],
    outline_files = ["**/*"]
}

[profiles.code-prompt]  # Built-in profile that adds LLM instructions
base = "code"  # Inherits from code profile
prompt = "lc-prompt.md"  # Adds prompt template to output
```

#### Settings Reference

Profile settings control behavior:

```toml
settings = {
    # Exclude binary/media files from folder structure
    no_media = true,

    # Include user notes from ~/.llm-context/lc-user-notes.md
    with_user_notes = false,

    # Write lc-context to file (relative to current directory) in addition to clipboard
    context_file = "context.md.tmp"
}
```

#### File Selection Patterns

Two types of pattern collections:

1. Additional Exclusions (gitignores):

```toml
gitignores = {
    # Files excluded from full content
    full_files = [".git", "*.lock"],

    # Files excluded from outlines
    outline_files = [".git", "*.lock"]
}
```

2. Optional Restrictions (only-include):

```toml
only-include = {
    # Only include these in full content
    full_files = ["**/*"],  # Include everything not excluded

    # Only include these in outlines
    outline_files = ["**/*.py", "**/*.js"]  # Restrict outlines to Python and JS
}
```

#### Example Custom Profiles

1. Documentation Focus:

```toml
[profiles.docs]
gitignores = {
    full_files = [".git", ".llm-context/", "*.lock"]
}
settings = {
    no_media = true,
    with_user_notes = true  # Include personal notes
}
only-include = {
    full_files = [
        "**/*.md", "**/*.txt",   # Documentation files
        "README*", "LICENSE*"     # Project info
    ]
}
```

2. Source Files Only:

```toml
[profiles.source]
gitignores = {
    full_files = [".git", ".llm-context/", "*.lock"]
}
settings = {
    no_media = true,
}
only-include = {
    full_files = [
        "src/**/*.py",           # Python source
        "tests/**/*.py",         # Test files
        "pyproject.toml"         # Project configuration
    ]
}
prompt = "lc-prompt.md"
```

#### Profile Inheritance

Profiles can extend others using the `base` field:

```toml
[profiles.base-docs]
gitignores = {
    full_files = [".git", ".llm-context/", "*.lock"]
}
settings = { no_media = true }
only-include = {
    full_files = ["**/*.md"]
}

[profiles.docs-with-notes]
base = "base-docs"
settings = {
    no_media = true,
    with_user_notes = true  # Add personal notes
}

[profiles.with-file]
base = "code"
settings = {
    no_media = true,
    with_user_notes = false,
    context_file = "context.md.tmp" # Save to file as well as clipboard
}
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

2. Update config.toml:

```toml
[templates]
context = "my-context.j2"
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

### lc-set-profile <name>

Switches the active profile.

```bash
lc-profile code        # Switch to default code profile
lc-profile code-prompt # Switch to code profile with prompt
lc-profile web        # Switch to web profile (if configured)
```

### lc-sel-files

Selects files for full content inclusion.

- Uses active profile's configuration
- Respects `.gitignore` patterns
- Updates `curr_ctx.toml` with selections

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

### lc-read-cliplist

Processes file requests from clipboard.

- Reads file paths from clipboard
- Generates formatted content
- Copies result to clipboard

## Advanced Features

### Code Outlining

#### Installation

Requires Python ≤ 3.12 due to dependencies:

```bash
uv tool install --python 3.12 "llm-context[outline]"
```

#### Configuration

Control outline behavior in profiles:

```toml
[profiles.with-outlines]
gitignores = {
    full_files = [".git", "*.lock"],
    outline_files = [".git", "*.lock"]
}
only-include = {
    full_files = ["**/*"],
    outline_files = ["**/*.py", "**/*.js"]
}
```

#### Language Support

Currently supported languages:

- C, C++, C#
- Elisp, Elixir, Elm
- Go
- Java, JavaScript
- OCaml
- PHP, Python
- QL
- Ruby, Rust
- TypeScript

#### Limitations

- Python version restriction (≤ 3.12)
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

```toml
# Optimize pattern matching
gitignores = {
    full_files = ["node_modules/**", "*.min.*"],
    outline_files = ["node_modules/**"]
}
```

2. Language-Specific Profiles:

```toml
# Python project optimization
[profiles.python-opt]
only-include = {
    full_files = ["**/main.py", "**/core/*.py"],
    outline_files = ["**/*.py"]
}
```

3. Custom Combinations:

```toml
# Mixed content optimization
[profiles.web-opt]
only-include = {
    full_files = [
        "**/index.html",
        "**/main.js",
        "**/*.md"
    ],
    outline_files = ["**/*.js", "**/*.ts"]
}
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

3. Usage:
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
lc-read-cliplist
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
   - Use `lc-read-cliplist` for new files
   - Maintain consistent context

## Best Practices

### Project Organization

- Keep `.llm-context/config.toml` in version control
- Ignore `curr_ctx.toml` in git
- Document any custom templates you create

### Profile Management

- Start with built-in profiles, customize as needed
- Document profile purposes in a comment in config.toml
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
   - Use `lc-read-cliplist` for targeted file access
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
   - Update references in config.toml

3. No Files Selected:

   - Check your profile's gitignores and only-include patterns
   - Review `.gitignore` patterns
   - Try `lc-profile code` to use default profile

4. Outline Generation Not Working:

   - Ensure you installed with `uv tool install --python 3.12 "llm-context[outline]"`
   - Check if your files are in supported languages
   - Make sure files aren't already selected for full content

5. Context Too Large:
   - Review selected files with `cat .llm-context/curr_ctx.toml`
   - Adjust profile patterns to exclude large files
   - Use outlines instead of full content where possible
