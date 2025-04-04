# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

LLM Context is a tool that helps developers quickly inject relevant content from code/text projects into Large Language Model chat interfaces. It leverages `.gitignore` patterns for smart file selection and provides both a streamlined clipboard workflow using the command line and direct LLM integration through the Model Context Protocol (MCP).

> **Note**: This project was developed in collaboration with several Claude Sonnets - 3.5, 3.6 and 3.7 (and more recently Grok-3 as well), using LLM Context itself to share code during development. All code in the repository is human-curated (by me 😇, @restlessronin).

## Breaking Changes in v0.3.0

We've switched to a Markdown (+ YAML front matter)-based rules system replacing the previous TOML/YAML-based profiles. This is a breaking change that affects configuration. See the [User Guide](docs/user-guide.md) for details on the new rule format and how to use it.

## Why LLM Context?

For an in-depth exploration of the reasoning behind LLM Context and its approach to AI-assisted development, check out our article: [LLM Context: Harnessing Vanilla AI Chats for Development](https://www.cyberchitta.cc/articles/llm-ctx-why.html)

To see LLM Context in action with real-world examples and workflows, read: [Full Context Magic - When AI Finally Understands Your Entire Project](https://www.cyberchitta.cc/articles/full-context-magic.html)

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
uv tool install "llm-context>=0.3.0"
```

To upgrade to the latest version:

```bash
uv tool upgrade llm-context
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
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

Once configured, you can start working with your project in two simple ways:

1. Say: "I would like to work with my project"
   Claude will ask you for the project root path.

2. Or directly specify: "I would like to work with my project /path/to/your/project"
   Claude will automatically load the project context.

#### Preferred Workflow: Combining Project UI with MCP

For optimal results, combine initial context through Claude's Project Knowledge UI with dynamic code access via MCP. This provides both comprehensive understanding and access to latest changes. See [Full Context Magic](https://www.cyberchitta.cc/articles/full-context-magic.html) for details and examples.

### CLI Quick Start and Typical Workflow

1. Navigate to your project's root directory
2. Initialize repository: `lc-init` (only needed once)
3. Select files: `lc-sel-files`
4. (Optional) Review selected files in `.llm-context/curr_ctx.yaml`
5. Generate context: `lc-context` (with optional flags: `-p` for prompt, `-u` for user notes)
6. Use with your preferred interface:

- Project Knowledge (Claude Pro): Paste into knowledge section
- GPT Knowledge (Custom GPTs): Paste into knowledge section
- Regular chats: Use `lc-context -p` to include instructions

7. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-clip-files`
   - Paste the contents back to the LLM

## Core Commands

- `lc-init`: Initialize project configuration
- `lc-set-rule <n>`: Switch rules (system rules are prefixed with "lc-")
- `lc-sel-files`: Select files for inclusion
- `lc-sel-outlines`: Select files for outline generation
- `lc-context [-p] [-u] [-f FILE]`: Generate and copy context
  - `-p`: Include prompt instructions
  - `-u`: Include user notes
  - `-f FILE`: Write to output file
- `lc-prompt`: Generate project instructions for LLMs
- `lc-clip-files`: Process LLM file requests
- `lc-changed`: List files modified since last context generation
- `lc-outlines`: Generate outlines for code files
- `lc-clip-implementations`: Extract code implementations requested by LLMs (doesn't support C/C++)

## Features & Advanced Usage

LLM Context provides advanced features for customizing how project content is captured and presented:

- Smart file selection using `.gitignore` patterns
- Multiple rule-based profiles for different use cases
  - System rules (prefixed with "lc-") provide default functionality
  - User-defined rules can be created independently or extend existing rules
- Code Navigation Features:
  1. **Smart Code Outlines**: Allows LLMs to view the high-level structure of your codebase with automatically generated outlines highlighting important definitions
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
