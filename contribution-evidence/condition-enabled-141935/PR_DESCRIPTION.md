<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Breaking change
<!--
  If your PR contains a breaking change for existing users, it is important
  to tell them what breaks, how to make it work again and why we did this.
  This piece of text is published with the release notes, so it helps if you
  write it towards our users, not us.
  Note: Remove this section if this PR is NOT a breaking change.
-->

No breaking change. Condition `enabled` templates keep their limited-template restrictions.

## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->

Condition `enabled` templates are currently rendered while the condition is set up, before automation trigger variables are available. For example, `enabled: "{{ enable_condition }}"` can silently disable a condition even when the trigger variable is true, allowing actions that the condition should block.

Render the template when the condition is checked, using the variables supplied for that run. A wrapper preserves disabled-condition results, forwards subscriptions and unloading to the child, and shares the child's trace entry. It applies to legacy and platform conditions, including nested logical conditions and cached script conditions.

Templates remain limited. Rendering errors are now reported at check time and stop the action through the existing condition error handling. A condition with a templated `enabled` value is set up regardless of the eventual template result; literal `enabled: false` retains its existing behavior.

Validation:

- All 788 tests in `tests/helpers/test_condition.py`, `tests/helpers/test_script.py`, `tests/components/automation`, and `tests/components/websocket_api/test_commands.py` pass.
- The four new automation regression cases fail against the unmodified base and pass with this change.
- Coverage includes reloads, AND/OR/NOT, legacy and platform conditions, repeated runs of cached if/choose conditions, rendering errors, traces, child lifecycle, WebSocket variables, and subscription error delivery without repeated events.
- Ruff check/format and serial Pylint pass for all six changed files.
- The full `prek run --all-files` run was attempted but did not pass in this environment. Worker processes encountered socket restrictions; serial mypy encountered an internal psutil PID error. Full setup also encountered a missing `autoconf` dependency while building dtlssocket. These are not reported as passing checks.

- Six unrelated test failures in WattWächter, Spin BLE, LibreSync, and Airzone also reproduce in a clean checkout of the unmodified base `d3a387482754d29ecc1eb8a27bd3d8ad4b0f8de0`. [Reproduction and validation evidence](https://github.com/jslponcev-ui/core/blob/review/condition-enabled-141935/contribution-evidence/condition-enabled-141935/CI_VALIDATION.txt).

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature (which adds functionality to an existing integration)
- [ ] Deprecation (breaking change to happen in the future)
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality improvements to existing code or addition of tests

## Additional information
<!--
  Details are important, and help maintainers processing your PR.
  Please be sure to fill out additional details, if applicable.
-->

- This PR fixes or closes issue: fixes #141935
- This PR is related to issue: #187013 (script-step enabled templates; this change keeps condition templates limited)
- Link to documentation pull request: 
- Link to contributors documentation pull request: 
- Link to frontend pull request: 

## Checklist
<!--
  Put an `x` in the boxes that apply. You can also fill these out after
  creating the PR. If you're unsure about any of them, don't hesitate to ask.
  We're here to help! This is simply a reminder of what we are going to look
  for before merging your code.

  AI tools are welcome, but contributors are responsible for *fully*
  understanding the code before submitting a PR. Please follow our AI policy:
  https://contributors.home-assistant.io/start/ai-policy/
-->

- [x] I understand the code I am submitting and can explain how it works.
- [x] The code change is tested and works locally.
- [x] Local tests pass. **Your PR cannot be merged unless tests pass**
- [x] There is no commented out code in this PR.
- [ ] I have followed the [development checklist][dev-checklist]
- [ ] I have followed the [perfect PR recommendations][perfect-pr]
- [x] The code has been formatted using Ruff (`ruff format homeassistant tests`)
- [x] Tests have been added to verify that the new code works.
- [x] Any generated code has been carefully reviewed for correctness and compliance with project standards.

If user exposed functionality or configuration variables are added/changed:

- [ ] Documentation added/updated for [www.home-assistant.io][docs-repository]

If the code communicates with devices, web services, or third-party tools:

- [ ] The [manifest file][manifest-docs] has all fields filled out correctly.  
      Updated and included derived files by running: `python3 -m script.hassfest`.
- [ ] New or updated dependencies have been added to `requirements_all.txt`.  
      Updated by running `python3 -m script.gen_requirements_all`.
- [ ] For the updated dependencies a diff between library versions and ideally a link to the changelog/release notes is added to the PR description.

<!--
  This project is very active and we have a high turnover of pull requests.

  Unfortunately, the number of incoming pull requests is higher than what our
  reviewers can review and merge so there is a long backlog of pull requests
  waiting for review. You can help here!
  
  By reviewing another pull request, you will help raise the code quality of
  that pull request and the final review will be faster. This way the general
  pace of pull request reviews will go up and your wait time will go down.
  
  When picking a pull request to review, try to choose one that hasn't yet
  been reviewed.

  Thanks for helping out!
-->

To help with the load of incoming pull requests:

- [ ] I have reviewed two other [open pull requests][prs] in this repository.

[prs]: https://github.com/home-assistant/core/pulls?q=is%3Aopen+is%3Apr+-author%3A%40me+-draft%3Atrue+-label%3Awaiting-for-upstream+sort%3Acreated-desc+review%3Anone+-status%3Afailure

<!--
  Thank you for contributing <3

  Below, some useful links you could explore:
-->
[dev-checklist]: https://contributors.home-assistant.io/core/development/checklist/
[manifest-docs]: https://contributors.home-assistant.io/core/integrations/manifest/
[quality-scale]: https://contributors.home-assistant.io/core/quality-scale/
[docs-repository]: https://github.com/home-assistant/home-assistant.io
[perfect-pr]: https://contributors.home-assistant.io/start/pull-requests/#before-you-open-it
