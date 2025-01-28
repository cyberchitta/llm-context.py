# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)

LLM Context is a tool that helps developers quickly inject relevant content from code/text projects into Large Language Model chat interfaces. It leverages `.gitignore` patterns for smart file selection and provides both a streamlined clipboard workflow using the command line and direct LLM integration through the Model Context Protocol (MCP).

> **Note**: This project was developed in collaboration with Claude-3.5-Sonnet, using LLM Context itself to share code during development. All code in the repository is human-curated (by me 😇, @restlessronin).

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

### Installing via Smithery

To install LLM Context for Claude Desktop automatically via [Smithery](https://smithery.ai/server/llm-context):

```bash
npx -y @smithery/cli install llm-context --client claude
```

### Installing via uv
Install LLM Context using [uv](https://github.com/astral-sh/uv):

```bash
uv tool install llm-context
```

To upgrade to the latest version:

```bash
uv tool upgrade llm-context
```

> **Warning**: LLM Context is under active development. Updates may overwrite configuration files prefixed with `lc-`. We recommend backing up any customized files before updating.

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

### CLI Quick Start and Typical Workflow

1. Navigate to your project's root directory
2. Initialize repository: `lc-init` (only needed once)
3. (Optional) Edit `.llm-context/config.toml` to customize ignore patterns
4. Select files: `lc-sel-files`
5. (Optional) Review selected files in `.llm-context/curr_ctx.toml`
6. Generate context: `lc-context`
7. Use with your preferred interface:

- Project Knowledge (Claude Pro): Paste into knowledge section
- GPT Knowledge (Custom GPTs): Paste into knowledge section
- Regular chats: Use `lc-set-profile code-prompt` first to include instructions

8. When the LLM requests additional files:
   - Copy the file list from the LLM
   - Run `lc-read-cliplist`
   - Paste the contents back to the LLM

## Core Commands

- `lc-init`: Initialize project configuration
- `lc-set-profile <name>`: Switch profiles
- `lc-sel-files`: Select files for inclusion
- `lc-context`: Generate and copy context
- `lc-read-cliplist`: Process LLM file requests
- `lc-changed`: List files modified since last context generation

## Features & Advanced Usage

LLM Context provides advanced features for customizing how project content is captured and presented:

- Smart file selection using `.gitignore` patterns
- Multiple profiles for different use cases
- Code outline generation for supported languages
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
