# Gemini Web mode status

## Verified modes

- **inspect-home**: works, confirms authenticated Gemini home and visible entry points.
- **image-create**: works, generates images through Gemini Web UI, downloads the produced full-size image, and can now take one or more local/inbound files as edit inputs.
- **image-edit**: works as an explicit command path for editing inbound/local images and returning the downloaded full-size result. Single-image live test passed. Multi-image upload wiring is implemented, but a two-image live run currently hit Google-side `GOOGLE_RUNTIME_ERROR_13`.
- **chat-ask**: works, sends a normal Gemini chat prompt and returns extracted answer text.

## Partially working modes

- **smoke / Storybook create**: local automation path is stable, and Storybook share-link extraction is live-validated on the current account. A fresh successful `smoke` run on 2026-04-29 returned a real Gemini share link after the P0 hardening pass. Practical retrieval path is Storybook history/root → open book → Share book panel. The flow is still account-dependent and can be flaky on other Gemini sessions.

## Known Google-side instability

- `GOOGLE_RUNTIME_ERROR_13` can appear on Storybook and sometimes on the plain Gemini `/app` path.
- Because of that, a passing `chat-ask` or `image-create` run should be treated as a current-success signal, not a permanent product guarantee.

## Thread reuse policy

- `chat-ask` and `image-create` reuse the last good Gemini thread by default.
- New threads should be started only intentionally with `--new-thread`.
- Broken transient chat URLs should not be kept as the active thread baseline.
