# Contributing

Thanks for helping improve this repo.

## Scope

This project is an operator-oriented, self-hosted Gemini Web automation skill for OpenClaw.

Please keep contributions aligned with the public contract:
- stable public core: `chat-ask`, `image-create`, `image-edit`
- account-session browser automation, not API-key integration
- no bypassing CAPTCHA, 2FA, device checks, or anti-bot protections
- no claims stronger than the current live validation evidence

## Local setup

```bash
./scripts/setup.sh
```

This creates the local `.venv`, installs Python dependencies, and installs Playwright Chromium.

## Before opening a PR

Run the smallest relevant checks for your change:

```bash
./scripts/ensure_env.sh
./scripts/gemini_web_doctor.sh
./scripts/validate_install.sh   # post-login checks only
```

If your environment has pytest available, also run:

```bash
pytest -q
```

For documentation-only changes, verify affected commands, paths, and feature claims against the current repo state.

## Validation expectations

Be explicit about what was actually verified:
- local setup only
- post-login doctor/inspect-home
- chat flow
- image-create flow
- image-edit flow
- experimental Storybook path

Do not imply live validation for surfaces you did not test.

## Privacy and secrets

Treat all browser profiles, diagnostics, screenshots, HTML dumps, and downloaded artifacts as private.

Never commit:
- `.gemini-web-profile/`
- `.gemini-storybook-profile/`
- `tmp/`
- diagnostics artifacts
- cookies, session files, exported account data, or local auth material

Before proposing changes that touch diagnostics, auth, or profile handling, read:
- `references/privacy-and-diagnostics.md`
- `references/remote-install-and-auth.md`
- `SECURITY.md`

## PR style

Prefer small, reviewable changes.

When changing public-facing wording, keep these layers consistent:
- `README.md`
- `SKILL.md`
- relevant `references/*.md`

When changing runtime behavior, include:
- what changed
- why it changed
- what you verified
- what remains unverified or experimental
