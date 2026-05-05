# Release evidence snapshot

This file records the current evidence behind the repo's release framing.

## Evidence basis for the current framing

### Clean-install evidence

Observed on a separate clean test install from the sanitized repo tree:

- `./scripts/setup.sh` completed successfully
- `./scripts/ensure_env.sh` completed successfully
- unit tests passed
- CLI help worked under the public-facing `gemini-web-skill` name

Fresh hardening pass on 2026-04-24, from a clean snapshot checkout:

- `./scripts/setup.sh` completed successfully
- `./scripts/ensure_env.sh` completed successfully
- `validate_install.sh` reached the post-login phase but stopped at the expected manual-auth boundary because the fresh snapshot had not yet been authenticated in its persistent browser profile

### Post-login/runtime evidence

Observed on a live authenticated profile:

- `doctor` succeeded
- `inspect-home` succeeded
- `chat-ask` succeeded
- normal chat-style operator usage has already been exercised outside one-off smoke validation
- `image-create` succeeded in live account usage, with known Google-side caveats when latency/runtime instability appears
- `image-edit` succeeded
- image-edit and chat/image flows have already been used as real operator workflows, not only as lab-style checks

Fresh clean-snapshot caveat:

- `doctor` can report `logged_in_guess: true` before the profile is actually authenticated enough for `inspect-home` to pass, so a fresh checkout still needs a real manual login step on the runtime host before post-login validation is meaningful.

Observed caveat:

- `image-create` hit a `GENERATION_TIMEOUT` in one clean test runtime, so it remains part of the dependable core with real Google-side caveats rather than a guaranteed always-fast surface.

### Storybook evidence

Current Storybook status remains experimental.

Observed on the live authenticated profile during the 2026-04-29 P0 hardening pass:

- Storybook `smoke` reached a real `status="success"` result and returned a valid Gemini share link
- the successful run completed after the new recovery/hardening path for: quiet post-generation settle, extraction-stage diagnostics, stricter share-click timeouts, and earlier history reopen before extraction
- the successful run did **not** need the same-thread recovery prompt or history reopen on that passing attempt, but those paths are now instrumented and available when Google-side flakiness appears

Observed again immediately after, during the 2026-04-29 P1 pass:

- a second consecutive live Storybook smoke run also succeeded and returned a real Gemini share link
- this gives repeat current-account evidence rather than a single lucky pass

The repo still intentionally does **not** present Storybook create/share/pdf as a mature broad-release surface, but the current account now has fresh live evidence for successful Storybook smoke plus share-link extraction.

## Evidence interpretation rule

- treat clean-install, tests, and wrapper checks as **installation evidence**
- treat authenticated live runs as **operator production evidence**
- do not confuse either category with a universal public guarantee across arbitrary accounts or future Gemini UI revisions

## How to read this file

- treat this as a conservative evidence snapshot, not as a universal guarantee
- use `references/validation.md` for the recommended validation order
- use `references/public-release-checklist.md` before any broader release decision
