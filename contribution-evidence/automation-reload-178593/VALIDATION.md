# Validation

Source commit: 3b5ab3f413a4bbca365f0fb7bfb588700b5fe768
Base: 3f8efe14b2bec286e44f0bf7769567844ad806c4
Python: 3.14.10

## Regression proof

On unchanged production code from the base, with the new tests:
`uv run --no-sync python -m pytest -q --timeout=10 tests/components/automation/test_init.py -k 'reload_from_changed_automation or reload_cancellation_preserves_serialization'`

Result: 3 failed, 146 deselected.
Both self-reload cases failed because no automation_reloaded event was fired.
The cancellation/serialization case failed because the second reload entered async_process_config before the first reload was allowed to finish (await_count 2 instead of 1).

With the final fix:
Result: 3 passed, 146 deselected in 0.48s.

All reload tests:
Result: 34 passed, 115 deselected in 1.64s.

## Broader tests

`uv run --no-sync python -m pytest -q tests/components/automation tests/components/script tests/components/config/test_automation.py tests/components/websocket_api/test_commands.py tests/helpers/test_service.py tests/helpers/test_script.py`

Result: 693 passed in 33.30s; 2 snapshots passed.
Initial run had 3 dependency-loading failures from an older hass-nabucasa. Installing the repository-pinned hass-nabucasa==2.8.1 resolved them.

## Static checks

- git diff --check: passed.
- Ruff check and Ruff format: passed.
- Codespell and Prettier: passed.
- Pylint with -j 1 --ignore-missing-annotations=y on both changed files: passed, exit 0.
- mypy --num-workers 0 --no-native-parser homeassistant/components/automation/services.py: Success: no issues found in 1 source file.
- Global prek run --all-files: executed. Ruff, format, codespell, zizmor, JSON, branch guard, YAML, Prettier, requirement generation, instruction generation, hassfest metadata and mypy config generation passed.
- Parallel mypy/Pylint/hassfest hooks could not complete because this environment denies Unix sockets. Serial mypy also required --no-native-parser because psutil could not inspect the process PID. These are local environment limitations, not a successful full-global-check claim.

## Environment setup

script/setup was run. Installing all integration dependencies stopped building DTLSSocket (via pytradfri), because autoconf is not installed. Attempting the OS package installation failed due to environment restrictions. Development/test requirements and editable project packages were installed separately; translations were generated for all integrations. No project dependency files were changed.

No upstream CI result exists yet: no PR has been opened.
