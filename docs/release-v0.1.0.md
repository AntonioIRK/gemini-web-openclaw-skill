# Release notes — v0.1.0

## Public contract

This is an operator-oriented, self-hosted Gemini Web automation skill for OpenClaw.

### Stable public core

- `chat-ask`
- `image-create`
- `image-edit`

### Experimental

- Storybook `smoke`
- Storybook `create --return-mode share_link`
- Storybook file upload
- Storybook PDF export

## Authentication model

This release uses a real Gemini Web browser session on the runtime host.
It is not a Gemini API-key integration.

## Safety posture

- no CAPTCHA/2FA bypass
- no cookie scraping or silent credential import
- diagnostics should be treated as private

## Notes

Storybook has meaningful current-account live evidence, but it remains outside the stable public promise.
