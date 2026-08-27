---
description: Review the current branch's changes for correctness, run the affected tests, and confirm the change matches its stated requirement.
argument-hint: [requirement or ticket description] [base-branch]
---

## Context

- Current branch changes vs main: !`git diff main --stat`
- Full diff: !`git diff main`
- Untracked files (new, not yet in the diff): !`git status --porcelain`

## Your task

Review the diff above as a senior engineer would before approving a PR. Requirement/context supplied by
the user, if any: $ARGUMENTS

1. **Identify scope.** From the diff, determine which service(s) or module(s) changed (e.g.
   `services/review-fetcher-service`, or the root `engine.py`/`engine_async.py`). Only review and test what
   actually changed plus anything that imports it.

2. **Run the tests for every changed service — do not skip this.**
   - For a Python service under `services/<name>/` with a `pytest.ini` and `tests/` dir: install/verify dev
     deps (`pip install -r requirements-dev.txt` if needed) and run `pytest` from that service's directory,
     e.g. `GOOGLE_PLACES_API_KEY=test-key pytest` for `review-fetcher-service` (see its README's Testing
     section for required env vars).
   - For root-level `engine.py`/`engine_async.py` changes, there is no test suite yet — say so explicitly
     rather than skipping silently, and note that this violates the CLAUDE.md workflow requirement to write
     tests for new functionality.
   - Report actual pass/fail counts and paste failing test output. Never claim "tests pass" without having
     run them in this turn.

3. **Check correctness in the diff itself.** Look for logic bugs, edge cases, error handling gaps, and
   anything that would break at runtime — not style nits.

4. **Check alignment with requirements.** Compare the change against:
   - Any requirement/ticket text passed in `$ARGUMENTS`.
   - The relevant README(s) (root `README.md`, and the changed service's own `README.md` if present) —
     does the implementation do what those docs claim/promise?
   - `.claude/CLAUDE.md`'s Core Principles (SOLID) and Development Workflow (feature branch, tests written,
     tests run before commit, commit message quality). Flag any violation explicitly.

5. **Report findings** as a short, prioritized list: correctness bugs first, then test-coverage/test-result
   issues, then requirement/doc misalignment, then SOLID/workflow violations. For each: file:line, what's
   wrong, and why it matters. If everything checks out, say so plainly instead of manufacturing nitpicks.

Do not fix anything unless the user asks — this command is review-only.
