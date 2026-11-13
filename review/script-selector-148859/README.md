# Script field selector validation — review

Issue: https://github.com/home-assistant/core/issues/148859
Base: `422081a19472edb52918c67fb461eef4f91101c6`.
Code commit: `56a3006949b3338cab97d4a0adafeb3b68237f88`.

## Change

Script field selectors can import platform modules while resolving feature
flags. Validating these fields in the executor prevents those imports from
blocking the event loop. Action and variable schemas stay on the event loop:
template validation explicitly requires that context.

The field schema wraps `fields` and allows already validated script options
through unchanged, so errors still identify their field path and source config
is preserved. No library, device, frontend, schema migration or additional PR
is required. This targets the complete reported script validation defect, not
every possible synchronous selector caller elsewhere in Home Assistant.

## Regression evidence

The two new thread-check cases fail on the untouched base: cover and assist
satellite feature enum imports run on the same thread as the event loop.
The fix moves both imports off that thread. The test also executes templated
variables and an action to guard against moving template validation off-loop.
The API tests verify valid field selectors are stored in original form and
invalid field types/selectors retain their error paths.

## Human review

The PR description preserves the upstream template and leaves the human
understanding and generated-code review boxes unchecked. Review the change
before submitting, as required by the repository's AGENTS.md and AI policy.

## Validation

- `uv run --no-sync pytest -q tests/components/script tests/components/config/test_script.py tests/helpers/test_selector.py tests/helpers/test_script.py`: **670 passed**, 40 warnings, 12.55 s; 4 snapshots passed.
- On unchanged base code, the two new import-thread regressions fail as expected.
- Ruff check/format, codespell, Prettier and branch check passed.
- mypy passed for the production file with `--num-workers 0 --no-native-parser`.
- Pylint passed for all three changed files with `--jobs=1 --ignore-missing-annotations=y`.
- The normal mypy/pylint hooks cannot open worker sockets in this environment, so the equivalent sequential runs above were used.
- `git diff --check` passed.
- The existing development environment was reused. Its required `script/setup` attempt had encountered a PyPI 429; the relevant pinned dependencies were installed separately, including those needed by the existing mobile-app/blueprint tests.
