# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python service for road-violation detection and reporting.

- `main.py`: entry point and task orchestration.
- `config/`: runtime settings, prompts, and DB config (`配置.py`, `数据库配置.py`).
- `detectors/`: model-facing detection logic and shared helpers (`detection_common.py`).
- `services/`: camera frame capture, CSV integration, scheduled push, and DB submission.
- `infra/`: logging and runtime utility modules.

Keep new business logic in the matching domain module, not in `main.py`.

## Build, Test, and Development Commands
- `python main.py`  
  Run the full local pipeline.
- `python -m py_compile main.py config/*.py detectors/*.py services/*.py infra/*.py`  
  Fast syntax validation for core modules.
- `python -m py_compile (Get-ChildItem -Recurse -Filter *.py | % FullName)` (PowerShell)  
  Compile all Python files recursively before commit.

Avoid network-dependent installs in deployment containers unless explicitly approved.

## Coding Style & Naming Conventions
- Follow PEP 8 where practical: 4-space indentation, short functions, clear names.
- Preserve existing Chinese module names for compatibility.
- Prefer explicit imports; do not use wildcard imports.
- Add concise Chinese comments for non-obvious business rules only.
- Remove commented-out dead code during refactors.

## Testing Guidelines
No formal unit-test framework is required yet. Minimum validation for each change:

1. Run recursive `py_compile`.
2. Validate touched runtime path(s) with a small real or mock sample.
3. For CSV/DB changes, verify schema compatibility and missing-column fallback behavior.

If adding tests later, place them in `tests/` and name files `test_*.py`.

## Commit & Pull Request Guidelines
Use small, focused commits. Recommended format:

- `feat(detectors): extract shared CSV polygon loader`
- `fix(services): ignore 模型输出 column during push`
- `refactor(config): centralize csv path constants`

PRs should include scope, affected modules, behavior changes, rollback notes, and validation evidence (commands run, sample logs/screenshots when relevant).

## Security & Configuration Tips
- Do not hardcode secrets; load them via environment variables in `config/配置.py`.
- Preserve Docker-mounted path compatibility (for example `/app/road_property_rightsmodel/...`).
- Treat `模型输出` as audit-only data unless explicitly required by business rules.
