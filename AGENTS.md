# Development Rules

Always run the full check suite after any code and/or documentation change:

- From the local virtualenv (.venv): `bash scripts/linters.sh`.
- The script aggregates: pylint, pyright, isort (check), pymarkdownlnt, yamllint, pytest, and optional helm lint.

Fix any issues immediately and rerun all checks until everything is green.

Do not finish an iteration until all tools are green:
- pylint: 10/10 and no errors
- pyright: 0 errors
- isort: no changes needed
- pymarkdownlnt: 0 issues (MD013 line-length up to 180 as in `.pymarkdownlnt.json`)
- yamllint: 0 errors (Helm templates excluded)
- pytest: all tests pass, coverage ≥ 80%
- helm lint: 0 chart(s) failed

Use configs from `pyproject.toml`, `.pymarkdownlnt.json`, `.yamllint.yaml` (run from the repository root).

If your IDE disagrees with CLI tools, align imports/types (pyright/isort), Markdown (pymarkdownlnt), YAML (yamllint) and code to satisfy pytest tests, then rerun checks.

## Changelog policy

- When creating or updating a changelog entry for a version, derive content from the actual code diff.
- Compare the current codebase with the previous release tag; if no tag exists, compare against `main`/`master`.
- Describe user‑visible changes, tooling updates, CI/build changes, and artifact names. Do not rely on chat history.
- Date entries accurately and keep them concise and factual.

## Commit message policy

- Base commit messages on the real changes in the working tree (diff), not on chat context.
- Prefer clear, scoped messages (e.g., `build:`, `ci:`, `docs:`, `feat:`, `fix:`, `refactor:`).
- Summarize the intent and key effects; avoid referencing the conversation.

## Language policy

- All code comments, documentation (including Markdown), and commit messages must be written in English.
- Chat responses should use the same language as the user's request. If the user's language is unclear, default to English.

## Agent editing policy

- Edit files only from the editor (agent mode). Do not modify files via shell commands or here‑doc/bulk console patches.
- Make every change explicit and reviewable. Do not use tools that silently rewrite files.
- If a formatter is required, run it with repo config and include the results as regular, reviewable edits.
- Commit new scripts with the executable bit set (`chmod +x`).

## Metadata

```yaml
applyTo: "**"
```
