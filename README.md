# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

LLM Context is a tool that helps developers quickly inject relevant content from code/text projects into Large Language Model chat interfaces. It leverages `.gitignore` patterns for smart file selection and provides both a streamlined clipboard workflow using the command line and direct LLM integration through the Model Context Protocol (MCP).

> **Note**: This project was developed in collaboration with several Claude Sonnets - 3.5, 3.6 and 3.7 (and more recently Grok-3 as well), using LLM Context itself to share code during development. All code in the repository is human-curated (by me 😇, @restlessronin).

## Important: Profile Changes and Command-line Parameters

As of version 0.2.16, we've made some key improvements:

1. **Diagram File Filtering**:

- The `-x` flag (previously `no_media` setting) has been removed
- Media/Binary files are now automatically filtered from diagram output using pattern-based ignores
- You can customize which files are excluded from diagram using the `diagram_files` key in your profile's gitignores

2. **Profile Simplification**:

- System profiles have been reduced to just "lc-code" and "lc-gitignores"
- The old "code-prompt" and "code-file" profiles are no longer needed as their functionality is now handled by command-line parameters
- All system profiles are prefixed with "lc-" for clarity

3. **Command Parameters**: Behavior options are controlled via command-line parameters:

- `-p`: Include prompt instructions in context
- `-u`: Include user notes in context
- `-f FILE`: Write context to specified output file

Examples:

```bash
# Generate context with prompt included
lc-context -p

# Generate context with user notes and save to file
lc-context -u -f project-context.md

# Generate context with all options
lc-context -p -u -f project-context.md
```

If you have customized profiles or have references to them in your workflows, please update them accordingly.

## Important: Configuration File Format Change

Configuration files were converted from TOML to YAML in v 0.2.9. Existing users **must manually convert** any customizations in `.llm-context/config.yaml` files to the new `.llm-context/config.yaml`.

## Why LLM Context?

For an in-depth exploration of the reasoning behind LLM Context and its approach to AI-assisted development, check out our article: [LLM Context: Harnessing Vanilla AI Chats for Development](https://www.cyberchitta.cc/articles/llm-ctx-why.html)

## Current Usage Patterns

- **Direct LLM Integration**: Native integration with Claude Desktop via MCP protocol
- **Chat Interface Support**: Works with any LLM chat interface via CLI/clipboard
  - Optimized for interfaces with persistent context like Claude Projects and Custom GPTs
  - Works equally well with standard chat interfaces
- **Project Types**: Suitable for code repositories and collections of text/markdown/html documents
- **Project Size**: Optimized for projects that fit within an LLM's context window. Large project support is in development

## Installation

Install LLM Context using [uv](https://github.com/astral-sh/uv):

```bash
# Basic installation
uv tool install llm-context

# Or with code outlining support (recommended for developers)
# uv tool install "llm-context[outline]"
```

To upgrade to the latest version:

```bash
# Basic upgrade
uv tool upgrade llm-context

# Or with code outlining support
# uv tool upgrade "llm-context[outline]"
```

> **Warning**: LLM Context is under active development. Updates may overwrite configuration files prefixed with `lc-`. We recommend all configuration files be version controlled for this reason.

## Quickstart

### MCP with Claude Desktop

Add to 'claude_desktop_config.json':

```jsonc
{
  "mcpServers": {
    "CyberChitta": {
      "command": "uvx",
      // Basic installation:
      "args": ["--from", "llm-context", "lc-mcp"]
      // With code outlining support (uncomment this line and comment the line above:
      // "args": ["--from", "llm-context[outline]", "lc-mcp"]
    }
  }
}
```

Once configured, you can start working with your project in two simple ways:

1. Say: "I would like to work with my project"
   Claude will ask you for the project root path.

2. Or directly specify: "I would like to work with my project /path/to/your/project"
   Claude will automatically load the project context.

### CLI Quick Start and Typical Workflow

1. Navigate to your project's root directory
2. Initialize repository: `lc-init` (only needed once)
3. (Optional) Edit `.llm-context/config.yaml` to customize ignore patterns
4. Select files: `lc-sel-files`
5. (Optional) Review selected files in `.llm-context/curr_ctx.yaml`
6. Generate context: `lc-context` (with optional flags: `-p` for prompt, `-u` for user notes)
7. Use with your preferred interface:

- Project Knowledge (Claude Pro): Paste into knowledge section
- GPT Knowledge (Custom GPTs): Paste into knowledge section
- Regular chats: Use `lc-context -p` to include instructions

8. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-clip-files`
   - Paste the contents back to the LLM

## Core Commands

- `lc-init`: Initialize project configuration
- `lc-set-profile <n>`: Switch profiles (system profiles are prefixed with "lc-")
- `lc-sel-files`: Select files for inclusion
- `lc-sel-outlines`: Select files for outline generation (requires installing with `[outline]` extra)
- `lc-context [-p] [-u] [-f FILE]`: Generate and copy context
  - `-p`: Include prompt instructions
  - `-u`: Include user notes
  - `-f FILE`: Write to output file
- `lc-prompt`: Generate project instructions for LLMs
- `lc-clip-files`: Process LLM file requests
- `lc-changed`: List files modified since last context generation
- `lc-outlines`: Generate outlines for code files (requires installing with `[outline]` extra)
- `lc-clip-implementations`: Extract code implementations requested by LLMs (requires installing with `[outline]` extra, doesn't support C/C++)

## Features & Advanced Usage

LLM Context provides advanced features for customizing how project content is captured and presented:

- Smart file selection using `.gitignore` patterns
- Multiple profiles for different use cases
  - System profiles (prefixed with "lc-") provide default functionality
  - User-defined profiles can be created independently or extend existing profiles
- Code Navigation Features:
  1. **Smart Code Outlines**: Allows LLMs to view the high-level structure of your codebase with automatically generated outlines highlighting important definitions (requires `[outline]` extra)
  2. **Definition Implementation Extraction**: Paste full implementations of specific definitions that are requested by LLMs after they review the code outlines, using the `lc-clip-implementations` command
- Customizable templates and prompts

See our [User Guide](docs/user-guide.md) for detailed documentation of these features.

## Similar Tools

Check out our [comprehensive list of alternatives](https://www.cyberchitta.cc/articles/lc-alternatives.html) - the sheer number of tools tackling this problem demonstrates its importance to the developer community.

## Acknowledgments

LLM Context evolves from a lineage of AI-assisted development tools:

- This project succeeds [LLM Code Highlighter](https://github.com/restlessronin/llm-code-highlighter), a TypeScript library I developed for IDE integration.
- The concept originated from my work on [RubberDuck](https://github.com/rubberduck-ai/rubberduck-vscode) and continued with later contributions to [Continue](https://github.com/continuedev/continuedev).
- LLM Code Highlighter was heavily inspired by [Aider Chat](https://github.com/paul-gauthier/aider). I worked with GPT-4 to translate several Aider Chat Python modules into TypeScript, maintaining functionality while restructuring the code.
- This project uses tree-sitter [tag query files](src/llm_context/highlighter/tag-qry/) from Aider Chat.
- LLM Context exemplifies the power of AI-assisted development, transitioning from Python to TypeScript and back to Python with the help of GPT-4 and Claude-3.5-Sonnet.

I am grateful for the open-source community's innovations and the AI assistance that have shaped this project's evolution.

I am grateful for the help of Claude-3.5-Sonnet in the development of this project.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
