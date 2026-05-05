# Validation

## Minimal validation flow

```bash
./scripts/gemini_web_doctor.sh
./scripts/gemini_web_inspect_home.sh
./scripts/gemini_web.sh chat-ask --prompt "Say hello in one sentence"
```

## Stronger validation flow

Also test:

- `image-create`
- `image-edit`

Treat Storybook as experimental even when it works on the current authenticated account.

For the full validation path, see `../references/validation.md`.
