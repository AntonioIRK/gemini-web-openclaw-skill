# Validation path

Use this when you want a clean, honest install verification flow.

## Validation levels

### Level 1, environment only

Run:

```bash
./scripts/setup.sh
./scripts/ensure_env.sh
```

Expected outcome:

- `.venv` exists
- Python 3.11+ is active inside the wrapper flow
- Playwright Python module is importable
- Playwright Chromium install completed

### Level 2, login and profile basics

Run:

```bash
./scripts/gemini_web_login.sh
./scripts/gemini_web_doctor.sh
```

Expected outcome:

- login completes in the opened browser window
- `doctor` returns JSON
- `doctor.logged_in_guess` is true after successful auth
- `doctor.page_url` is no longer stuck on Google sign-in pages

Important caveat:

`doctor` checks environment and profile basics. It does **not** prove that every Gemini surface or workflow is fully usable.

### Level 3, account surface visibility

Run:

```bash
./scripts/gemini_web_inspect_home.sh
```

Expected outcome:

- JSON response with `page_url`, `title`, and `suggestions_detected`
- visible Gemini surfaces match the target account reality

### Level 4, reliable workflow validation

Prefer one of these:

```bash
./scripts/gemini_web.sh chat-ask --prompt "Reply with exactly: OK"
./scripts/gemini_web_image_create.sh --prompt "A simple red kite on a blue sky"
```

Expected outcome:

- structured JSON result
- `status: success`, or a clearly diagnostic failure payload

### Level 5, experimental workflow validation

Only after the earlier levels pass:

```bash
./scripts/gemini_web_smoke.sh
```

Expected outcome:

- either success
- or a structured error such as `GOOGLE_RUNTIME_ERROR_13`

Do not treat Storybook smoke success as guaranteed across accounts.
