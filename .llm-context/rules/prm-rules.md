---
name: prm-templates
description: work with the system rule files
instructions: [lc/ins-developer, lc/sty-code, lc/sty-python]
compose:
  filters: [flt-repo-base, flt-no-excerpters]
  excerpters: [lc/exc-base]
also-include:
  full-files: [/src/llm_context/lc_resources/rules/lc/**]
---
