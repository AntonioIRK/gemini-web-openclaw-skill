# Security notes

## Supported usage model

This repository is intended for self-hosted or operator-side Gemini Web automation using a user-approved persistent browser profile.

## What this project should not do

- bypass CAPTCHA, 2FA, or device verification
- scrape unrelated browser cookies
- silently import or exfiltrate user credentials
- ship live browser profiles or session databases in git

## Repository hygiene

Never commit:

- `.gemini-web-profile/`
- `.gemini-storybook-profile/` (legacy compatibility path)
- `.venv/`
- `tmp/`
- `build/`
- generated `*.egg-info/`
- diagnostic artifacts that may contain session-adjacent data

Local/private artifacts to treat carefully:

- Playwright traces, screenshots, HTML snapshots, and console dumps from failed runs
- downloaded Gemini output files before you intentionally publish or share them
- ad hoc debug notes that mention account state, remote-host layout, or browser-session paths

Installed does not mean authenticated, and authenticated does not mean broadly validated. Avoid claiming more readiness than the evidence supports.

## Disclosure

If you find a security problem in this repo or a workflow that risks exposing session data, report it privately to the repository owner before public disclosure.

## Support expectations

- This is an operator-oriented self-hosted project, not a managed service.
- Debug help may require looking at private diagnostics; review and redact before sharing artifacts.
- Do not ask users to export hidden cookies, bypass Google checks, or weaken account security to make the automation work.
