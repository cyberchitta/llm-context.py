---
name: flt-repo-base
description: additional repo specific filters.
compose:
  filters: [lc/flt-base]
gitignores:
  full-files:
    - "*.md"
    - /tests
    - tag-qry/
    - lc_resources/
  excerpted-files:
    - "*.md"
    - /tests
    - tag-qry/
    - lc_resources/
---
