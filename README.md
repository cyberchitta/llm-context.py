# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

**Smart context management for LLM development workflows.** Define the minimal file set a task needs with a composable rule, then pack it for a chat, an MCP client, or a disposable sub-agent.

Getting the right context into an LLM is friction-heavy: finding and copying files by hand wastes time, too much context hits token limits, too little misses what matters, and follow-up file requests mean more manual fetching. A rule describes the selection once; the tooling handles packing, follow-up fetches, and change tracking.

## Documentation lives in the skill

The full documentation is the **`lc-curate-context` skill**, installed into your project by `lc-init`. It is written to be read by an agent, and it is the only copy — this README is a landing page, not a manual.

| File | Contents |
| --- | --- |
| `SKILL.md` | Writing a rule; the workflow; packing for a sub-agent |
| `COMMANDS.md` | CLI and MCP reference, including output routing |
| `SYNTAX.md` | Rule file schema and every field |
| `PATTERNS.md` | Reusable rule shapes |
| `EXAMPLES.md` | Worked examples |
| `TROUBLESHOOTING.md` | Failure cases |

Find them at `.claude/skills/lc-curate-context/` after `lc-init`. In Claude Code the skill loads automatically; elsewhere, read the files directly.

## Installation

```bash
uv tool install "llm-context>=0.6.0"
cd <project-root>
lc-init          # creates .llm-context/, installs the skill into .claude/skills/
```

Upgrading: `uv tool upgrade llm-context`, then any `lc-*` command refreshes the skill, rules and templates in place.

## Three ways to use it

**Human, via clipboard** — generate context, paste into any chat.

```bash
lc-select        # pin a file selection for the active rule
lc-context       # copy the pack to the clipboard
```

**Chat with MCP** — the model fetches what it needs on its own.

```jsonc
{
  "mcpServers": {
    "llm-context": {
      "command": "uvx",
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

The `lc_missing`, `lc_changed`, `lc_outlines` and `lc_preview` tools let the model pull files it wasn't given and notice ones that changed underneath it.

**Sub-agent, via a pipe** — a dispatcher writes the prompt, llm-context supplies the files.

```bash
lc-preview -r tmp-prm-auth              # check the rule selects what you expect
lc-context -r tmp-prm-auth -a | claude -p 'Your task here'
```

`-r` is what routes output to stdout; without it `lc-context` copies to the clipboard, so a pipe or redirect gets nothing but log lines. These commands take no bare positional rule name — always `-r`. `-a` renders the pack's fetch instructions as shell commands the child runs itself, so from the repo root it can call `lc-missing` against the pack's timestamp for anything left out. See `SKILL.md` "Packing for a Sub-Agent".

## Rules in one minute

A rule is YAML frontmatter plus optional markdown:

```yaml
---
description: "Debug API authentication"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
Focus on the authentication system and its tests.
```

Rules compose, and are named by category: `prm-` produces a context, `flt-` controls file inclusion, `ins-` supplies guidelines, `sty-` enforces coding standards, `exc-` configures excerpting. Files you expect to edit go in `full-files`; supporting code goes in `excerpted-files`, where it is reduced to signatures and definitions. See `SYNTAX.md` and `PATTERNS.md`.

## What a generated context contains

Complete contents for full files, structural excerpts for the rest, a filtered file listing marking what is and isn't included, and a timestamp that `lc-missing` and `lc-changed` resolve against.

A pack is always partial — the listing is filtered by your `.gitignore` files and by the rule before anything is marked excluded, so files can exist that it never mentions. The header reports how many files are full, outlined and excerpted, so a consumer can check what it actually received rather than trusting the rule.

## Learn More

- [Design Philosophy](https://www.cyberchitta.cc/articles/llm-ctx-why.html) — why llm-context exists
- [Real-world Examples](https://www.cyberchitta.cc/articles/full-context-magic.html) — using full context effectively

## License

Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

Developed in collaboration with several Claude models and Groks, using LLM Context itself to share code during development. All code is heavily human-curated by [@restlessronin](https://github.com/restlessronin).
