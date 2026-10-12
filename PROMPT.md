# Prompts untuk AI (Cursor / Claude Code)

## A. Prompt review (tempel setelah menambahkan tiap stage)
Read AGENTS.md. Review the code I just added for: bugs, edge cases not covered by tests,
security issues, unclear naming and missing docs. List findings by severity. Do not rewrite
everything; propose minimal diffs only. Then run `make lint test`.

## B. Stage 4: tambah satu rule baru (dikerjakan sendiri bersama AI)
Add a new rule `open_graph_title`: the page should have `<meta property="og:title" content="...">`
with non-empty content. The parser currently stores meta tags by `name` only, so extend it to also
capture `property`. Rule weights must still sum to 100: rebalance (for example lower `word_count`
to 5 and give the new rule 5) and explain your choice. Add pass and fail tests, update the rules
table in README.md and run `make lint test`. Keep the diff small.
