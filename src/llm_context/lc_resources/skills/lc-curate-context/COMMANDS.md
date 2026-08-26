# Command Reference

## Output routing — read this first

`lc-context` and `lc-outlines` send output to **stdout when `-r <rule>` is given, and to the clipboard otherwise.** Nothing else changes routing.

```bash
lc-context                       # clipboard, active rule
lc-context -r tmp-prm-auth       # stdout, named rule — this is what pipes and redirects need
lc-context -r tmp-prm-auth > pack.md
lc-context -r tmp-prm-auth | claude -p 'Task here'
```

None of these commands take a bare rule name as a positional argument. `lc-context tmp-prm-auth` does **not** use `tmp-prm-auth`: the argument is ignored, the *active* rule is used, and the output goes to the clipboard — so a redirect captures only log lines. `lc-preview tmp-prm-auth` errors outright. Always use `-r`.

## Setup

| Command | Purpose |
|---|---|
| `lc-init` | Initialize `.llm-context/` in the project |
| `lc-set-rule <rule>` | Set the active rule (`prm-code`, `lc/prm-developer`, `tmp-prm-my-task`) |
| `lc-select` | Recompute and pin the active rule's file selection |
| `lc-version` | Print the installed version |

`lc-select` pins a selection so `lc-changed` has a baseline to diff against. It is not required before generating context — `lc-context` selects on demand for any rule that has no pinned selection.

## Generating context

```bash
lc-context              # active rule → clipboard
lc-context -r <rule>    # named rule → stdout
lc-context -p           # include the rule's prompt/instructions
lc-context -u           # include user notes
lc-context -m           # separate-message mode (emit a "ready for your request" handshake)
lc-context -a           # consumer is an agent with a shell, not MCP tools
lc-context -nt          # consumer has neither; a human relays commands
lc-context -f out.md    # also write to a file
lc-prompt               # instructions only, no files
lc-outlines             # excerpted structure only
lc-outlines -r <rule>   # ...for a named rule, to stdout
```

These three flags pick **who fetches what the pack left out**, and the pack's instructions are rendered to match. Getting this wrong is silent: the reader is told to do something it cannot do, and simply doesn't.

| Consumer | Flag | The pack tells it to |
|---|---|---|
| Chat with the MCP server | *(default)* | call the `lc-missing` / `lc-changed` tools |
| Agent with a shell, no MCP | `-a` | run `lc-missing` / `lc-changed` itself, from the project root |
| Chat with neither | `-nt` | ask the user to run the commands and paste the output back |

A `claude -p` child is the middle case: it has Bash but no MCP server, so it needs `-a`. Without it the pack hands it a JSON tool call it cannot make; with `-nt` it gets shell commands addressed to "the user", which it will not read as its own instructions.

## Validating a rule

```bash
lc-preview -r <rule>    # what the rule selects, with sizes
```

`lc-preview` computes its selection fresh and does not change any stored state.

Its `Referenced but not selected` section lists files defining symbols the selection uses but does not include, ranked by reference count. It is built from tree-sitter tag captures — the same parse that produces outlines — and matches by symbol name, so a name defined in several places is dropped rather than guessed at, and a common name can still point at the wrong file. Advisory only: nothing is added to the selection.

## Fetching what the pack left out

Every generated context carries a `Generation timestamp`. These commands resolve a pack by that timestamp, so they only work for a pack llm-context itself produced.

```bash
lc-changed                                              # files changed since the pinned selection
lc-missing -f "['/proj/src/a.py']" -t <timestamp>       # full file contents
lc-missing -i "[['/proj/src/a.py','my_func']]" -t <ts>  # specific definitions
lc-missing -e "['/proj/src/a.py']" -t <timestamp>       # excluded sections of an excerpted file
```

`lc-missing -f` is not a plain file read. Against the pack's timestamp it classifies each path: already included and unchanged → **named, not re-sent**; included but modified on disk since the pack was cut → **re-sent**; outlined → upgraded to full content; absent → fetched. The second case is the one that matters for a long-running agent, because reasoning from a stale copy fails silently.

## MCP tools

Configure the server:

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

| Tool | Equivalent |
|---|---|
| `lc_preview` | `lc-preview -r <rule>` |
| `lc_outlines` | `lc-outlines -r <rule>` |
| `lc_missing` | `lc-missing` (`param_type` `"f"` / `"i"` / `"e"`) |
| `lc_changed` | `lc-changed` |
| `lc_rule_instructions` | `lc-rule-instructions` |

There is no `lc_context` MCP tool. MCP serves a chat that already has context and needs additions; use the CLI to produce the pack itself.

## Recovery

```bash
cp -r .llm-context/rules /tmp/rules-backup   # keep custom rules
rm -rf .llm-context && lc-init               # reset to defaults
cp /tmp/rules-backup/*.md .llm-context/rules/
```

System rules under `.llm-context/rules/lc/` and the files in `.llm-context/templates/` are regenerated on version upgrade — edit the rule that composes them, not the generated copies.
