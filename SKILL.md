---
name: gemini-web
description: Drive the real Gemini Web UI through a persistent authenticated browser profile and Playwright automation. This skill is for browser account-session automation, not Gemini API-key usage. Use when inspecting Gemini account surfaces, running normal Gemini chat flows, generating images through the web UI, or reaching Storybook/Gems features that live in the web product surface.
---

# gemini-web

Use this skill for work on Gemini Web account-session automation, with chat and image flows as the mature core and Storybook as one specialized runner.

## What this skill is for

Use it when the task is to:

- implement or improve Gemini Web automation for OpenClaw
- run local diagnostics for session reuse, browser profile health, and Gemini UI availability
- inspect the authenticated Gemini home surface, chats, and available entry points
- drive Gemini image generation or other UI-only feature paths
- run the Storybook workflow and preserve diagnostics when Google fails

Prefer this skill when the operator has installed the repo into the OpenClaw skills directory and completed one-time Gemini login bootstrap in the persistent local profile.

This is an account-session skill. Do not frame it as a Gemini Developer API or API-key integration.

Readiness language matters here:

- `installed` means the local runtime is present
- `authenticated` means the persistent Gemini browser profile is really logged in on the runtime host
- `operator-validated` means someone has run live Gemini checks on that authenticated host
- only `chat-ask`, `image-create`, and `image-edit` belong to the stable public core today

Storybook currently belongs to operator-validated current-account evidence, not to the stable public promise.

## Authentication at a glance

- **Local install**: login happens in the browser on the local host, and the Gemini profile stays local.
- **Remote install**: login happens in the browser on the remote server, and the Gemini profile stays on that server.
- **No usable GUI on the real host**: do not pretend a headless auth path is reliable; recommend local install or add a real desktop path.

If OpenClaw is installed on a remote server, read `references/remote-install-and-auth.md` before attempting authentication. That file explains when remote auth is workable, what software is typically needed for screen access, and when local install is the better recommendation.

Before first install or troubleshooting a clean machine, also read `references/prerequisites.md` and `references/validation.md`.

For broader release or portability questions, also read `references/support-matrix.md` and `references/privacy-and-diagnostics.md`.

For current release evidence and signed-off release posture, also read `references/release-evidence.md` and `references/public-release-status.md`.

When an agent needs to explain auth to a human step by step, read `references/auth-script.md` and follow its wording closely instead of improvising.

## Current runnable surfaces

- `inspect-home` for checking what Gemini surfaces are visible in the account
- `chat-ask` for normal Gemini chat requests with thread reuse
- `chat-ask-stream` for real-time text streaming of the chat response
- `image-create` for running a real Gemini Web image-generation prompt
- `image-edit` for editing one or more local/inbound images through the real Gemini Web UI
- `document-analysis` for uploading files and querying them for text analysis
- `smoke` for a short Storybook diagnostic probe
- `create` for the structured Storybook run returning share link or PDF

Most reliable today: `chat-ask`, `chat-ask-stream`, `image-create`, `image-edit`, and `document-analysis`.

Agents should treat Storybook `smoke` as diagnostic-only. Storybook `create` is live-validated on the current account for `share_link` extraction, but it remains account-dependent and outside the stable public-release promise.

For OpenClaw integration, this repo currently exposes these payload modes through the adapter layer: `chat-ask`, `chat-ask-stream`, `image-create`, `image-edit`, `document-analysis`, and Storybook `create`.

For `chat-ask`, `document-analysis` and `image-create`, default behavior is to continue the same Gemini chat thread across assistant-driven requests. Use `--new-thread` only when you intentionally want to switch topics and start a fresh branch.

For Storybook, prefer `return_mode=share_link` first. That is the currently live-validated path.
If you need the link, the practical live path is: open Storybook, pick the book from history/root if needed, then use the Share book panel and extract the generated URL.

Storybook patience policy:

- treat `create` as a 10-minute patience flow, not a 5-minute one
- do not report "no link yet" before the full patience budget is spent
- after the first 10-minute window, send one recovery prompt in the same Gemini thread, then wait a short extra window for Share book
- if the book appears in Storybook history after a timeout, reopen the newest book from history and retry Share book before failing
- only accept a history item when its visible body matches the current prompt; otherwise keep waiting
- only after both windows and the history recovery fail should you report the run as a real failure
- if a user asks again later, rerun the same branch instead of assuming the previous attempt is final

Book-count limits:

- no published hard cap was found for the number of Storybooks a user can create
- the only clearly documented product limit found is that a Storybook is a 10-page book
- do not claim "unlimited"; say "no published hard cap found" instead

Browser recovery policy:

- if the browser/CDP loop times out or the Chrome port is already in use, stop treating it as a book failure
- restart the browser driver, reopen Storybook, and re-run the same prompt before concluding anything about the book
- if a tab silently drifts to another Gemini surface, navigate back to Storybook root before resuming

Library bookkeeping:

- when the user wants a book library, maintain a Google Drive folder plus a spreadsheet index
- each completed book should be recorded with: creation date, title, Storybook link, PDF Drive link, and notes
- before generating a replacement for a numbered/library book, first search existing Gemini history/share links and verify the visible book content; only generate when no matching existing book is found
- accept a Storybook only after visible title/body/page content matches the intended theme; do not rely on history-card title, unique share link, or local PDF hash alone
- if PDF export is available, download the PDF locally first, verify it, upload it to Drive, store its Drive link in the sheet, then remove the local PDF and temporary verification files from the server
- Storybook PDF export is viewport/layout sensitive: before clicking Download, open the existing book branch, use a wide/fullscreen reader state, then verify page count plus rendered page thumbnails for normal text/image proportions; reject UI screenshots and distorted exports
- if PDF export is not available or fails validation, keep the Storybook link in the sheet and mark PDF as pending rather than inventing a file link
- treat library updates as part of the successful delivery flow, not as a separate optional cleanup step

## Storybook contract

Storybook is an additional specialized surface, not the primary definition of the repo.
It remains experimental and is not part of the stable public-release promise.

Input:

```json
{
  "prompt": "string",
  "files": ["optional file paths"],
  "return_mode": "share_link | pdf",
  "output_path": "optional path",
  "timeout_seconds": 300,
  "debug": false
}
```

Output:

```json
{
  "status": "success | error",
  "share_link": "optional string",
  "pdf_path": "optional string",
  "title": "optional string",
  "debug_artifacts_path": "optional string",
  "error_code": "optional string",
  "error_message": "optional string"
}
```

## Default workflow

1. Read `references/internal/spec.md` and `references/internal/prompt.md` for the current target behavior.
2. Read `references/internal/research-notes.md` and `references/internal/integration-notes.md` only before changing architecture or transport assumptions.
3. If the repo was installed directly under `~/.openclaw/workspace/skills/`, prefer the local wrapper flow and use `scripts/setup.sh` for first-time setup or after a fresh install.
4. Use `scripts/ensure_env.sh` before local runs.
5. Use `scripts/gemini_web_doctor.sh` to validate python, Playwright, and profile setup.
6. Use `scripts/gemini_web_login.sh` for first-time manual login bootstrap.
7. Use `scripts/gemini_web_inspect_home.sh` to inspect the normal Gemini Web landing surface.
8. Use `scripts/gemini_web_image_create.sh ...` for a real Gemini image-generation check.
9. Use `scripts/gemini_web_create.sh ...` only when the Storybook surface is explicitly the target.
10. If a run fails, inspect the generated diagnostics directory before changing selectors.

When the host is remote, insert one more decision before login: confirm that the server actually has a usable GUI access path. If it does not, do not bluff a headless auth solution. Recommend local install or a proper remote desktop setup instead.

## Safety rules

- Do not bypass CAPTCHA, 2FA, device integrity checks, or anti-bot systems.
- Reuse an existing user-approved Gemini session; do not scrape hidden cookies from unrelated browsers.
- Treat Gemini Web as a browser account workflow first. Do not reframe it as an API-key product.
- Preserve failure artifacts instead of guessing when the DOM changes.
- Keep CDP attach disabled unless an operator explicitly opts in.
- Treat diagnostics as private, and prefer the default retention window instead of leaving runs around forever.

## References

Use these public-first references by default:

- `references/auth-script.md` — exact local-vs-remote authentication wording and step-by-step guidance for agents
- `references/prerequisites.md` — exact prerequisites, supported baseline, and when to stop on unsupported hosts
- `references/support-matrix.md` — conservative support matrix for environments, feature maturity, and the honest operator/public contract
- `references/privacy-and-diagnostics.md` — how to handle screenshots, HTML dumps, and other diagnostic artifacts safely
- `references/validation.md` — clean install validation path and expected outcomes
- `references/remote-install-and-auth.md` — remote-server install and authentication runbook, including GUI access patterns and decision points
- `references/release-evidence.md` — current evidence snapshot behind the repo's release claims
- `references/public-release-status.md` — current signed-off release posture and remaining intentional limits
- `references/mode-status.md` — currently verified Gemini Web modes and their live status

Deeper internal build notes can stay in `references/`, but they are not part of the public-first reading path.

## Scripts

- `scripts/ensure_env.sh` — validate local environment and optional Playwright install state
- `scripts/setup.sh` — create `.venv`, install Python deps, and install Playwright Chromium
- `scripts/validate_install.sh` — quick validation wrapper for env, doctor, and inspect-home
- `scripts/gemini_web.sh` — primary generic wrapper for login, doctor, debug-open, inspect-home, image-create, smoke, create
- `scripts/gemini_web_login.sh` — primary first-time manual login bootstrap wrapper
- `scripts/gemini_web_doctor.sh` — primary session/profile diagnostics wrapper
- `scripts/gemini_web_debug_open.sh` — primary wrapper to open Gemini in the persistent profile for manual inspection
- `scripts/gemini_web_inspect_home.sh` — primary wrapper to inspect the authenticated Gemini home surface
- `scripts/gemini_web_image_create.sh` — primary Gemini Web image-generation wrapper
- `scripts/gemini_web_image_edit.sh` — primary Gemini Web image-edit wrapper against one or more local/inbound files
- `scripts/gemini_web_create.sh` — primary structured Storybook create wrapper
- legacy `scripts/gemini_storybook*.sh` wrappers remain only as compatibility aliases
