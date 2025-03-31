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
   - [Repository Structure Diagram](#repository-structure-diagram)
   - [State Management](#state-management)
   - [Rules Overview](#rules-overview)

3. [Configuration](#configuration)

   - [Configuration Files](#configuration-files)
   - [Rule Configuration](#rule-configuration)
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
   - [lc-clip-implementations](#lc-clip-implementations)

5. [Advanced Features](#advanced-features)

   - [Code Outlining](#code-outlining)
   - [Rule Integration](#rule-integration)
   - [Performance Optimization](#performance-optimization)

6. [Workflows](#workflows)

   - [Direct LLM Integration (MCP)](#direct-llm-integration-mcp)
   - [Chat Interface Usage](#chat-interface-usage)
   - [Project Knowledge Base](#project-knowledge-base)
   - [Custom GPT Integration](#custom-gpt-integration)

7. [Best Practices](#best-practices)

   - [Project Organization](#project-organization)
   - [Rule Management](#rule-management)
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

   This creates the `.llm-context` directory with default configuration files and rules.

3. The default "lc-code" rule is ready to use. For specialized needs, you can create custom rules in `.llm-context/rules/`.

### Basic Workflow

1. Select files to include in your context:

   ```bash
   lc-sel-files
   ```

   This uses your `.gitignore` and rule settings to choose relevant files.

2. Select files for outline generation:

   ```bash
   lc-sel-outlines
   ```

   This will select additional files to be presented as structural outlines.

3. Generate and copy context to clipboard:

   ```bash
   lc-context
   ```

   Use command-line flags to customize the output:

   ```bash
   lc-context -p -u -f output.md
   ```

4. Paste the context into your LLM chat interface:

   - For Claude Projects/Custom GPTs: Use the knowledge section
   - For regular chats: Use `lc-context -p` to include guiding instructions

5. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-clip-files`
   - Paste the new content back to the LLM

### Command Overview

Core commands you'll use frequently:

- `lc-init`: Set up LLM Context in your project
- `lc-set-profile <n>`: Switch between different rule configurations
- `lc-sel-files`: Select files for full content inclusion
- `lc-sel-outlines`: Select files for structural outline generation
- `lc-context [-p] [-u] [-f FILE]`: Generate and copy context to clipboard
  - `-p`: Include prompt instructions
  - `-u`: Include user notes
  - `-f FILE`: Write to output file
- `lc-clip-files`: Process file requests from the LLM

### Common Use Cases

1. Code Projects:

   - Use default "lc-code" rule (or create your own)
   - Run `lc-sel-files` to include source code
   - Optional: Use `lc-sel-outlines` for structural overview
   - Generate context: `lc-context -p` (with prompt)

2. Documentation Projects:

   - Create a custom rule "docs" in `.llm-context/rules/docs.md`
   - Switch to documentation focus: `lc-set-profile docs` (after creating it)
   - Select content: `lc-sel-files`
   - Generate with user notes: `lc-context -u`
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

   - `config.yaml`: Main configuration file (templates only)
   - `rules/`: Directory containing rule files
   - `lc-project-notes.md`: Project-specific notes
   - `templates/`: Template files
   - `curr_ctx.yaml`: Current context state

3. User Configuration
   - `~/.llm-context/lc-user-notes.md`: User specific notes

### Files and Directories

Standard project layout:

```
your-project/
├── .llm-context/
│   ├── config.yaml          # Main configuration (templates)
│   ├── rules/               # Rule files
│   │   ├── lc-code.md       # Default code rule
│   │   ├── lc-gitignores.md # Base gitignore patterns
│   │   └── custom-rule.md   # Your custom rules
│   ├── lc-project-notes.md  # Project notes
│   ├── curr_ctx.yaml        # Current state
│   └── templates/           # Template files
│       ├── lc-context.j2
│       ├── lc-files.j2
│       └── lc-highlights.j2
├── .gitignore               # Required
└── [project files]
```

### Repository Structure Diagram

The repository structure diagram is a text-based representation of your project's file tree that helps LLMs understand your project's organization. It appears near the beginning of the generated context and serves several important purposes:

1. **Project Overview**: Provides a clear view of how files and directories are organized
2. **File Status Indication**: Shows which files are included as full content (✓), outlines (○), or excluded (✗)
3. **Navigation Aid**: Helps the LLM locate files it might need to examine

Example diagram:

```
Status: ✓=Full content, ○=Outline only, ✗=Excluded
Format: status path bytes (size) age

✓ /my-project/src/main.py 2048 (2.0 KB) 1d ago
○ /my-project/src/utils.py 4096 (4.0 KB) 2d ago
✗ /my-project/data/large_dataset.csv 10485760 (10.0 MB) 7d ago
```

The diagram includes:

- File status indicators (✓, ○, ✗)
- Relative paths from project root
- File sizes (both in bytes and human-readable format)
- File age (how recently the file was modified)

By default, the diagram excludes common media and binary files to keep the context focused on code and documentation. You can customize which files appear in the diagram by modifying the `diagram_files` patterns in your rule's configuration.

### State Management

LLM Context maintains state in `curr_ctx.yaml`:

- Tracks selected files per profile
- Preserves selections between sessions
- Updates automatically with commands
- Records timestamp when context is generated to track file changes

### Rules Overview

Rules are now defined as Markdown files with YAML frontmatter:

1. File Selection

   - Which files to include/exclude via gitignore patterns
   - Full content vs outline selection
   - Customizable inclusion/exclusion patterns

2. Prompt Content

   - Instructions for the LLM in Markdown format
   - Defined in the body of the rule file

3. Built-in Rules
   - `lc-gitignores.md`: Base rule containing default gitignore patterns
   - `lc-code.md`: Default rule for software projects, using the lc-gitignores base rule

Behavior options that were previously in profile settings are now controlled via command-line parameters.

## Configuration

### Configuration Files

#### config.yaml

Primary configuration file now contains only template mappings:

```yaml
# Template mappings
templates:
  context: "lc-context.j2"
  files: "lc-files.j2"
  highlights: "lc-highlights.j2"
  prompt: "lc-prompt.j2"
  definitions: "lc-definitions.j2"
```

#### Rule Files

Rule files are Markdown files with YAML frontmatter, stored in `.llm-context/rules/`:

```markdown
---
name: lc-code
description: "Default profile for software projects, using lc-gitignores base profile."
base: lc-gitignores
---

## Persona

Senior developer with 40 years experience.

## Guidelines

1. Assume questions and code snippets relate to this project unless stated otherwise
2. Follow project's structure, standards and stack
3. Provide step-by-step guidance for changes
...
```

#### Notes Files

1. Project Notes (`lc-project-notes.md`)

   - Project-specific documentation
   - Created at initialization
   - User-maintained
   - Included in context by default

2. User Notes (`~/.llm-context/lc-user-notes.md`)
   - Personal/global notes
   - Optional inclusion via the `-u` flag
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

### Rule Configuration

Rules are configured using a combination of YAML frontmatter and Markdown content:

#### Frontmatter Options

```yaml
---
name: my-rule-name                    # Rule name (matches filename without .md)
description: "Description of the rule" # Rule description
base: lc-gitignores                   # Optional, inherit from another rule
gitignores:                           # Optional, additional gitignore patterns
  full_files:
    - "node_modules/**"
    - "*.min.*"
  outline_files:
    - "node_modules/**"
    - "*.min.*" 
  diagram_files:
    - "*.jpg"
    - "*.png"
only-include:                         # Optional, restrict to specific patterns
  full_files:
    - "src/**/*.py"
  outline_files:
    - "**/*.py"
files:                                # Optional, always include these files
  - "README.md"
  - "pyproject.toml"
rules:                                # Optional, include these rule files
  - "python-style.md"
---
```

#### Markdown Content

The Markdown content of the rule file becomes the prompt instructions for the LLM:

```markdown
## Persona

Senior developer with 40 years experience.

## Guidelines

1. Assume questions and code snippets relate to this project unless stated otherwise
2. Follow project's structure, standards and stack
3. Provide step-by-step guidance for changes
...
```

Important: The `.git` directory should always be included in your rule's gitignores patterns since it isn't typically in .gitignore files but should always be excluded from context generation.

Here's a complete example:

```markdown
---
name: python-dev
description: "Python development with coding standards"
base: lc-code
gitignores:
  full_files:
    - "__pycache__/"
    - "*.pyc"
  outline_files:
    - "__pycache__/"
    - "*.pyc"
only-include:
  full_files:
    - "src/**/*.py"
    - "tests/**/*.py"
  outline_files:
    - "**/*.py"
files:
  - "pyproject.toml"
  - "requirements.txt"
rules:
  - "python-style.md"
---

## Python Development

When working with this Python project:

1. Follow PEP 8 style guidelines
2. Use type hints for all functions
3. Write comprehensive docstrings
4. Include unit tests for new functionality
```

#### File Selection Patterns

Three types of pattern collections:

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
  # Files excluded from diagram
  diagram_files:
    - "*.jpg"
    - "*.png"
    - "*.gif"
```

2. Optional Restrictions (only-include):

```yaml
only-include:
  # Only include these in full content
  full_files:
    - "**/*" # Include everything not excluded
  # Only include these in outlines
  outline_files:
    - "**/*.py"
    - "**/*.js" # Restrict outlines to Python and JS
  # Only include these in diagram
  diagram_files:
    - "**/*" # Include everything not excluded
```

The `diagram_files` patterns control which files are displayed in the repository structure diagram. This gives you fine-grained control over what files appear in the diagram. By default, common media and binary file types are excluded.

#### Rule and File References

Rules can include references to other rules and files:

```yaml
rules:
  - "python-style.md" # Programming style guide
  - "error-handling.md" # Error handling conventions
files:
  - "pyproject.toml" # Project configuration
  - "docs/user-guide.md"
```

1. **Rule References**:

   - Included in the prompt section of the context
   - Guide LLM behavior for code generation and review
   - Perfect for defining coding standards, conventions, and best practices

2. **File References**:
   - Automatically included in full file content
   - No need to select them with `lc-sel-files`
   - Useful for important files that should always be included
   - Eliminates the need to maintain separate lists of essential files

#### Path Format for References

- **Rule References**: Simple filenames or paths relative to the rules directory
  ```yaml
  rules:
    - "python.md"           # References .llm-context/rules/python.md
    - "style/naming.md"     # References .llm-context/rules/style/naming.md
  ```

- **File References**: Paths relative to the project root
  ```yaml
  files:
    - "src/main.py"         # References project file at <root>/src/main.py
    - "config/settings.json"  # References project file at <root>/config/settings.json
  ```

#### Example Custom Rules

1. Documentation Focus:

```markdown
---
name: docs
description: "Documentation-focused profile"
gitignores:
  full_files:
    - ".git"
    - ".llm-context/"
    - "*.lock"
only-include:
  full_files:
    - "**/*.md"
    - "**/*.txt" # Documentation files
    - "README*" # Project info
    - "LICENSE*"
---

## Documentation Review

When reviewing documentation in this project:

1. Check for clarity and completeness
2. Ensure consistent formatting
3. Verify all links are working
4. Suggest improvements for readability
```

2. Source Files Only:

```markdown
---
name: source
description: "Source code focus"
base: lc-code
only-include:
  full_files:
    - "src/**/*.py" # Python source
    - "tests/**/*.py" # Test files
    - "pyproject.toml" # Project configuration
---

## Code Review

When reviewing the source code:

1. Look for potential bugs and edge cases
2. Evaluate code structure and organization
3. Check for appropriate error handling
4. Consider performance implications
```

3. Python with Style Rules:

```markdown
---
name: python-style
description: "Python development with style rules"
base: lc-code
rules:
  - "python-style.md" # Style guide
  - "docstring-conventions.md" # Documentation standards
only-include:
  full_files:
    - "src/**/*.py" # Python source
    - "tests/**/*.py" # Test files
---

## Python Development Guidelines

When working with this Python codebase:

1. Follow PEP 8 style guidelines
2. Use type hints for all functions
3. Write comprehensive docstrings
4. Include unit tests for new functionality
```

This rule:

- Inherits from the default code rule
- Adds Python style and documentation conventions as rules
- Focuses only on Python source and test files
- Ensures all code follows consistent style guidelines

#### Rule Inheritance

Rules can extend others using the `base` field in frontmatter:

```yaml
base: lc-code # Inherit from lc-code rule
```

The inheritance system allows you to:

- Create base rules for common patterns
- Override specific fields in derived rules
- Mix and match configurations for different use cases

### System Rules vs User Rules

LLM Context distinguishes between system-provided rules and user-defined rules:

- **System Rules**: Prefixed with "lc-" (e.g., `lc-code.md`)

  - Most system rules are maintained by the system and may be updated during version upgrades
  - **Exception**: The `lc-gitignores.md` rule is preserved during updates, allowing you to customize project-wide ignore patterns that will be maintained across upgrades
  - System rules inherit base ignore patterns from the `lc-gitignores.md` rule

- **User Rules**: Any rule without the "lc-" prefix
  - These are always preserved during updates
  - Best practice is to create your own rules that extend system rules

When customizing gitignore patterns, you have two recommended approaches:

1. Modify the `lc-gitignores.md` rule for project-wide ignore patterns that should apply to all rules
2. Create custom rules with specific gitignore overrides for specialized use cases

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

2. Prompt Template (`lc-prompt.j2`)
   Renders prompt content:

```jinja
{%- if prompt -%}
{{ prompt }}
{%- endif %}
{%- if rules %}

## Additional Rules

{% for item in rules -%}
{{ item.content }}
{% endfor %}
{%- endif -%}
{%- if user_notes %}

{{ user_notes }}
{%- endif -%}
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
- Creates default rules in `.llm-context/rules/`
- Requires `.gitignore` file in project root
- Safe to run multiple times

### lc-set-profile profile-name

Switches the active rule.

```bash
lc-set-profile lc-code         # Switch to default code rule
lc-set-profile docs            # Switch to a custom user rule (if configured)
```

### lc-sel-files

Selects files for full content inclusion.

- Uses active rule's configuration
- Respects `.gitignore` patterns
- Updates `curr_ctx.yaml` with selections

### lc-sel-outlines

Selects files for structural outline generation.

- Limited to supported languages
- Excludes files already selected for full content

### lc-context

Generates context and copies to clipboard with optional parameters.

```bash
lc-context                      # Basic context generation
lc-context -p                   # Include prompt instructions
lc-context -u                   # Include user notes
lc-context -f output.md         # Write to specified output file
lc-context -p -u -f out.md      # Combine multiple options
```

The parameters control behavior:

- `-p`: Include prompt instructions in context
- `-u`: Include user notes in context
- `-f FILE`: Write context to specified output file

### lc-prompt

Generates project-specific instructions suitable for "System Prompts" or "Custom Instructions" sections in LLM chat interfaces.

- Outputs formatted instructions from your rule's Markdown content
- Includes user notes if the `-u` flag is included
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
- Respects current rule's file selection patterns

### lc-outlines

Generates smart outlines for all outline-eligible code files and copies to clipboard.

- Uses active rule's configuration for file selection
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

### lc-clip-implementations

Extract code implementations requested by LLMs.

- Reads file path and definition name pairs from clipboard
- Extracts full implementation of requested definitions
- Copies result to clipboard
- Format for clipboard input:
  ```
  /path/to/file.py:DefinitionName
  /path/to/file.py:another_function_name
  ```
- Useful when LLMs request to see specific implementation details
- Note: Currently doesn't support C and C++ files

## Advanced Features

### Code Outlining

LLM Context provides two powerful code navigation features:

1. Generating smart outlines to understand code structure
2. Extracting full implementations of specific definitions

These capabilities work together to help LLMs efficiently explore and understand your codebase.

#### Configuration

Control outline behavior in rules:

```yaml
gitignores:
  outline_files:
    - ".git"
    - "*.lock"
only-include:
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

#### Workflow

For code outlining to work properly:

1. First run `lc-sel-files` to select files for full content
2. Then run `lc-sel-outlines` to select additional files for outline generation
3. Finally run `lc-context` to generate the complete context including both full files and outlines

If you skip the `lc-sel-outlines` step, your context will not include any code outlines.

#### Limitations

- Implementation extraction doesn't currently support C and C++ files

#### Definition Implementation Extraction

After reviewing code outlines, LLMs may request to see the full implementation of specific definitions (classes, functions, methods, etc.). LLM Context provides a seamless workflow for this:

1. The LLM will request implementations in the format:

   ```
   /path/to/file.py:DefinitionName
   /path/to/file.py:another_function_name
   ```

2. Copy these requests to your clipboard

3. Run the command:

   ```bash
   lc-clip-implementations
   ```

4. Paste the results back to the LLM

This feature:

- Works with all languages supported by the code outliner, except C and C++ (currently not supported)
- Extracts the complete implementation, not just signatures
- Helps LLMs understand specific code components without requiring the entire file
- Enables a two-step exploration workflow: first understand structure, then examine specific implementations

Example workflow:

1. Generate context with outlines: `lc-context`
2. LLM reviews the code structure and requests specific implementations
3. Copy the requests, run `lc-clip-implementations`, paste results
4. LLM can now analyze the detailed implementations

### Rule Integration

LLM Context supports incorporating programming style guides and best practices directly into your LLM interactions through rule references in the frontmatter.

#### Rule Format

Rules should be stored as Markdown files in the `.llm-context/rules/` directory. They're included at the beginning of the context with the prompt, ensuring the LLM is aware of your coding standards from the start.

Example rule file (`.llm-context/rules/python-style.md`):

```markdown
---
name: python-style
description: "Python coding style guide"
---

## Programming Style

When writing Python code, prefer a functional and Pythonic style. Use list comprehensions instead of traditional for loops where appropriate. Leverage conditional expressions and single-pass operations for efficiency. Employ expressive naming and type hinting to enhance code clarity. Prefer stateless methods and concise boolean logic where possible. Make use of Python idioms such as tuple unpacking. In short, write **beautiful** code.
```

#### Benefits of Rule References

1. **Consistency**: Ensure all generated code follows your team's standards
2. **Efficiency**: No need to repeatedly explain coding conventions
3. **Modularity**: Create different rule sets for different languages or projects
4. **Integration**: Works with various style guide formats

#### Best Practices for Rules

1. Keep rule files concise and focused
2. Use Markdown for clear formatting
3. Organize rules by language or concern
4. Use descriptive filenames for easy reference
5. Reference other rules when needed using the `rules` field in frontmatter

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

#### Rule Optimization

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

2. Language-Specific Rules:

```yaml
# Python project optimization
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

   | Tool Name              | Description                                                          |
   | ---------------------- | -------------------------------------------------------------------- |
   | lc-project-context     | Generates a full repository overview with file contents and outlines |
   | lc-get-files           | Retrieves specific files from the project                            |
   | lc-list-modified-files | Lists files modified since a specific timestamp                      |
   | lc-code-outlines       | Returns smart outlines for all code files in the repository          |
   | lc-get-implementations | Retrieves complete code implementations of definitions               |

4. Usage:
   - Files requested via MCP are automatically processed
   - No manual clipboard operations needed
   - Maintains conversation context

### Chat Interface Usage

1. Standard Chat:

```bash
lc-context -p                  # Generate context with prompt instructions
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

   - Use `lc-set-profile lc-code`
   - Generate context with `lc-context`
   - Paste into knowledge section
   - Update as project evolves

2. Knowledge Maintenance:
   - Regular context updates
   - Consistent rule usage
   - Documentation in project notes

### Custom GPT Integration

1. Initial Setup:

   - Generate context with `lc-context`
   - Add to GPT knowledge base
   - Include prompt if needed: `lc-context -p`

2. Ongoing Usage:
   - Update knowledge as needed
   - Use `lc-clip-files` for new files
   - Maintain consistent context

## Best Practices

### Project Organization

- Keep `.llm-context/config.yaml` in version control
- Keep rule files (`.llm-context/rules/*.md`) in version control
- Ignore `curr_ctx.yaml` in git
- Document any custom templates you create

### Rule Management

- Start with built-in rules (prefixed with "lc-"), customize as needed
- Create your own rules (without the "lc-" prefix) for custom configurations
- Modify the `lc-gitignores.md` rule to customize project-wide ignore patterns
- Document rule purposes in the description field
- Share working rules with your team

### Performance Tips

1. Monitor and Optimize File Selection:

   - Review actual selected files after `lc-sel-files`
   - Remove large generated files, logs, etc.
   - Adjust rule patterns based on what you see

2. Check Context Size:

   - Review the actual context after pasting into chat
   - Look for unnecessary large files or duplicates
   - Consider using outlines for large files

3. Efficient Updates:
   - Use `lc-clip-files` for targeted file access
   - Update context when project structure changes
   - Switch rules based on your current task

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

   - Check your rule's gitignores and only-include patterns
   - Review `.gitignore` patterns
   - TryContinuing the user guide:

```markdown
3. No Files Selected:

   - Check your rule's gitignores and only-include patterns
   - Review `.gitignore` patterns
   - Try `lc-set-profile lc-code` to use default rule

4. Outline Generation Not Working:

   - Check if your files are in supported languages
   - Make sure files aren't already selected for full content
   - Run `lc-sel-outlines` after `lc-sel-files`

5. Context Too Large:

   - Review selected files with `cat .llm-context/curr_ctx.yaml`
   - Adjust rule patterns to exclude large files
   - Use outlines instead of full content where possible

6. Rule Not Found:

   - Check that the rule file exists in `.llm-context/rules/`
   - Ensure the rule filename matches what you're using with `lc-set-profile`
   - Make sure the rule file has proper frontmatter with a `name` field

7. Migration from Profiles:

   - When migrating from previous versions, create rule files for each custom profile
   - Copy profile settings to rule frontmatter
   - Move prompt content to the body of the rule file
   - Use the same name for your rule as your previous profile

## Migrating from Profiles to Rules (v0.3.0+)

In version 0.3.0, LLM Context switched from YAML-based profiles to Markdown-based rules. This section explains how to migrate your existing configuration.

### Understanding the Changes

1. **Profiles are now Rules**:
   - Profiles from `config.yaml` are now separate Markdown files in `.llm-context/rules/`
   - Each rule file contains YAML frontmatter + Markdown content

2. **Structure Changes**:
   - `config.yaml` now only contains template mappings
   - Profile settings moved to rule file frontmatter
   - Prompt content moved to rule file Markdown body

### Migration Steps

1. **Create Rule Files**:
   
   For each custom profile, create a new .md file in `.llm-context/rules/`:
   
   ```markdown
   ---
   name: my-profile-name
   description: "Description from your profile"
   base: lc-code  # If your profile inherited from another
   gitignores: 
     # Copy your gitignores section here
   only-include:
     # Copy your only-include section here
   files:
     # Copy your file-references here if any
   rules:
     # Copy your rule-references here if any
   ---

   <!-- Add your prompt content here -->
   ```

2. **Move Prompt Content**:
   
   If your profile had a `prompt` field pointing to a file, copy that file's content to the body of your rule file.

3. **Switch to the New Rule**:
   
   Use the same name for your rule as your previous profile to maintain compatibility:
   
   ```bash
   lc-set-profile my-profile-name
   ```

### Example Migration

**Old Profile (in config.yaml):**
```yaml
profiles:
  python-dev:
    description: "Python development configuration"
    base: "lc-code"
    gitignores:
      full_files:
        - "__pycache__/"
      outline_files:
        - "__pycache__/"
    only-include:
      full_files:
        - "src/**/*.py"
      outline_files:
        - "**/*.py"
    prompt: "python-prompt.md"
```

**Python Prompt File (python-prompt.md):**
```markdown
## Python Development Guidelines

1. Follow PEP 8 style guidelines
2. Use type hints for all functions
3. Write comprehensive docstrings
```

**New Rule File (.llm-context/rules/python-dev.md):**
```markdown
---
name: python-dev
description: "Python development configuration"
base: lc-code
gitignores:
  full_files:
    - "__pycache__/"
  outline_files:
    - "__pycache__/"
only-include:
  full_files:
    - "src/**/*.py"
  outline_files:
    - "**/*.py"
---

## Python Development Guidelines

1. Follow PEP 8 style guidelines
2. Use type hints for all functions
3. Write comprehensive docstrings
```

### Tips for Successful Migration

1. **Keep Names Consistent**: Use the same rule names as your previous profiles
2. **Check Configuration**: Verify frontmatter syntax is valid YAML
3. **Preserve Base Rules**: Don't modify system rules (prefixed with "lc-")
4. **Test Each Rule**: After migration, test each rule to ensure it works as expected
5. **Update Scripts**: If you have scripts that reference profiles, update them to use the new rule names

### Default Rules

LLM Context comes with default rules in the `.llm-context/rules/` directory:

1. **lc-gitignores.md**: Base rule containing default gitignore patterns
2. **lc-code.md**: Default rule for software projects (inherits from lc-gitignores)

You can examine these files to understand the new rule format and use them as templates for your own rules.
