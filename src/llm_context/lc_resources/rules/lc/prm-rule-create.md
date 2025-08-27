---
name: lc/ins-rule-create
description: Generates a complete project context with instructions for creating focused rules, including new chat prefixes and common guidelines. Includes all rule files in full content for reference. Use for efficient rule creation tasks.
instructions: ["lc/ins-rule-intro", "lc/ins-rule-framework"]
overview: full
compose:
  filters: [lc/flt-base]
also-include:
  full-files: [/.llm-context/rules/**]
---
