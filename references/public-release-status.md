# Public release status

## Current release posture

- Private operator release: approved
- Broader public release: possible only when framed as an early public self-hosted/operator release with `chat-ask`, `image-create`, and `image-edit` as the stable core

## Signed-off checklist snapshot

### Completed for the current pass

- [x] sanitized repo snapshot prepared
- [x] runtime artifacts excluded from git
- [x] secret scans performed on sanitized tree
- [x] prerequisites documented
- [x] support matrix documented
- [x] auth script documented
- [x] remote install/auth runbook documented
- [x] privacy guidance for diagnostics documented
- [x] validation path documented
- [x] lightweight CI sanity workflow added
- [x] private release framing clarified at top of README
- [x] contributing guidance added
- [x] support guidance added
- [x] GitHub issue and PR templates added

### Still intentionally limited

- [ ] strong automated post-login E2E against real Gemini accounts
- [x] Gemini-Web-first runtime naming established, with Storybook-era names reduced to compatibility aliases
- [ ] broad end-user release confidence
- [x] honest operator-oriented public-release contract documented

## Recommended public framing

If made public in the current state, frame it as:

> an operator-oriented, self-hosted Gemini Web automation skill for OpenClaw, with `chat-ask`, `image-create`, and `image-edit` as the stable public core, and Storybook kept outside the public stability promise.

In other words: Storybook has meaningful current-account operator evidence, but it should still be described as experimental and account-dependent rather than part of the broad release contract.

## Storybook repeatability note

The current authenticated operator account now has fresh repeat evidence from 2026-04-29:

- one live Storybook smoke run succeeded and returned a real Gemini share link after the P0 hardening pass
- a second consecutive live Storybook smoke run also succeeded and returned a real Gemini share link
- these passing runs improve confidence for the current account/profile, but they do **not** yet justify promoting Storybook into the stable public-release promise across arbitrary accounts, regions, or future Google UI changes
