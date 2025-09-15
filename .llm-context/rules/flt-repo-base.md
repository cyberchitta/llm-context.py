---
name: flt-repo-base
description: additional repo specific filters.
compose:
  filters: [lc/flt-base]
gitignores:
  full-files:
    - "*.md"
    - /tests
    - ts-qry/
    - lc_resources/
  excerpted-files:
    - "*.md"
    - /tests
    - ts-qry/
    - lc_resources/
---
