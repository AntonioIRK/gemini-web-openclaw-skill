# Research notes

This file is the evolving landing zone for internal architecture conclusions.

## Consolidated conclusions

- MVP should use Playwright UI automation against the real Gemini Web Storybook workflow.
- Session reuse should rely on a dedicated persistent Chromium profile path, not raw cookie scraping.
- The project should expose both a local CLI and an OpenClaw-friendly structured adapter.
- Diagnostics must be first-class: screenshot, HTML, console log, optional trace, and state snapshot.
- Network-layer reverse engineering can be explored later, but only after a working UI flow is validated.
- The best project shape is a hybrid OpenClaw skill shell plus Python engine: `SKILL.md`, `scripts/`, `references/`, and `src/openclaw_gemini_web/`.

## Architecture takeaways

Take:
- unofficial-web-client discipline
- CLI + wrapper split
- explicit troubleshooting and live-integration notes
- browser profile reuse for consented account-session access
- result modeling for exported artifacts

Do not take:
- any assumption that a generic Gemini transport automatically covers Storybook workflow specifics
- any assumption that an API-style access layer can replace the web-account workflow for this skill
