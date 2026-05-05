# E2E validation notes

This repo does not claim clean-room automated E2E across all Gemini surfaces.

Use the layered validation path in `references/validation.md`.

Minimum practical validation order:

1. `./scripts/setup.sh`
2. `./scripts/ensure_env.sh`
3. `./scripts/gemini_web_login.sh`
4. `./scripts/gemini_web_doctor.sh`
5. `./scripts/gemini_web_inspect_home.sh`
6. `./scripts/gemini_web.sh chat-ask --prompt "Reply with exactly: OK"`
7. optionally `./scripts/gemini_web_image_create.sh --prompt "A simple red kite on a blue sky"`
8. only then `./scripts/gemini_web_smoke.sh`

Expected result style:

- structured JSON output
- success on reliable chat/image flows when the account is healthy
- structured diagnostic errors when Gemini or Storybook is unavailable

This needs a real Gemini account, a usable browser runtime, and, for remote installs, a genuinely workable remote desktop path.
