# Development Rules (updated)

Always run the following checks from the local virtualenv (.venv) after any code and/or Markdown change:

- pylint: `source .venv/bin/activate && pylint **/*.py`
- pyright: `source .venv/bin/activate && pyright`
- isort: `source .venv/bin/activate && python -m isort --check --diff .`
- pymarkdownlnt: `source .venv/bin/activate && pymarkdownlnt --config .pymarkdownlnt.json scan --recurse --exclude=./.venv .`
- yamllint: `source .venv/bin/activate && yamllint -c .yamllint.yaml .`
- pytest (with coverage): `source .venv/bin/activate && pytest -v` (coverage and threshold are configured in pyproject.toml)
- helm lint (if charts present): `helm lint helm/`

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

## Notes

Helm templates under `helm/templates/**` are excluded from yamllint due to Go template syntax. Use `helm lint` for those.

## Additional requirements

- When Python code changes, always run pytest with coverage and keep coverage ≥ 80%.
