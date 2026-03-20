# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python service for road-violation detection and reporting.

- `main.py`: process entry point and task orchestration.
- `config/`: runtime configuration, prompts, and DB settings (`配置.py`, `数据库配置.py`).
- `detectors/`: model-facing detection logic and shared helpers (`detection_common.py`).
- `services/`: data I/O, camera frame capture, CSV integration, scheduled push, DB submission.
- `infra/`: infrastructure utilities (logging, shared runtime helpers).

Keep new code in the matching domain module. Avoid placing new business logic in `main.py`.

## Build, Test, and Development Commands
- `python main.py`  
  Run the full pipeline locally.
- `python -m py_compile main.py config/*.py detectors/*.py services/*.py infra/*.py`  
  Fast syntax validation before commit.
- `python -m py_compile (Get-ChildItem -Recurse -Filter *.py | % FullName)` (PowerShell)  
  Compile all Python files recursively.

No network-dependent package install should be required in deployment containers unless explicitly approved.

## Coding Style & Naming Conventions
- Follow PEP 8 where practical: 4-space indentation, clear function names, short functions.
- Keep existing Chinese module names unchanged for compatibility.
- New shared logic should go to `detectors/detection_common.py` or a dedicated helper in `services/`.
- Prefer explicit imports; do not use wildcard imports.
- Add concise Chinese comments for non-obvious business rules; remove commented-out dead code.

## Testing Guidelines
There is currently no formal unit-test framework in this repo. Minimum requirement for each change:

1. Run recursive `py_compile`.
2. Validate touched runtime path(s) with a small real or mock sample.
3. For CSV/DB changes, verify schema compatibility and fallback behavior for missing columns.

If you add tests later, place them under a new `tests/` directory and use `test_*.py` naming.

## Commit & Pull Request Guidelines
Use small, focused commits. Recommended commit format:

- `feat(detectors): extract shared CSV polygon loader`
- `fix(services): ignore 模型输出 column during push`
- `refactor(config): centralize csv path constants`

PRs should include:
- scope and affected modules,
- behavior changes and rollback notes,
- validation evidence (commands run, sample logs/screenshots if relevant).

## Security & Configuration Tips
- Do not hardcode new secrets; use environment variables in `config/配置.py`.
- Preserve Docker-mounted path compatibility (for example `/app/road_property_rightsmodel/...`).
- Treat `模型输出` as audit-only data unless a business rule explicitly consumes it.
