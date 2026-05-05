# Diagnostics

When a run fails, preserve:

- `state.json`
- `console.log`
- `page.html`
- screenshot files once live capture is wired in
- trace artifact once Playwright tracing is enabled

## What to inspect first

1. `state.json` to see the last state-machine step.
2. `page.html` to detect DOM or login changes.
3. `console.log` for frontend/runtime errors.
4. Output JSON for `error_code` and `error_message`.

## Expected failure classes

- `LOGIN_REQUIRED`
- `STORYBOOK_NOT_AVAILABLE`
- `PROMPT_SUBMISSION_FAILED`
- `UPLOAD_FAILED`
- `GENERATION_TIMEOUT`
- `SHARE_LINK_NOT_FOUND`
- `PDF_EXPORT_FAILED`
- `UNKNOWN_RUNTIME_ERROR`
