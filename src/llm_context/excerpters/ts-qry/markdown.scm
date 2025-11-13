;; Headings
(atx_heading) @heading.atx
(setext_heading) @heading.setext

;; Code blocks
(fenced_code_block) @code.fenced
(indented_code_block) @code.indented

;; Lists - capture list_item directly (works for both tight and loose)
(list_item) @list.item

;; Tables (GFM extension)
(pipe_table) @table.pipe

;; Block quotes
(block_quote) @quote.block

;; Thematic breaks
(thematic_break) @break.thematic

;; Paragraphs - for content filtering
(paragraph) @content.paragraph