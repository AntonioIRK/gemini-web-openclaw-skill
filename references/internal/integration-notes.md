# Integration notes

## Structural choices for this skill

- Keep `SKILL.md` thin and procedural.
- Put concrete runtime entrypoints in `scripts/`.
- Put architecture, limitations, and live notes in `references/`.
- Keep the Python engine under `src/openclaw_gemini_web/`.

## Product-shape rules

- Treat this as a Gemini Web account-session skill, not an API-key integration.
- Keep auth centered on a persistent browser profile owned by the operator.
- Keep diagnostics first-class because browser automation can drift.
- Keep result delivery focused on one verified final artifact, especially for image edits.

## Recommended next live-validation checks

1. Confirm whether Storybook appears as a Gem, prompt trigger, or both on the target account.
2. Capture stable selectors for prompt box, upload, generation state, share, and export.
3. Record the real failure signature for expired session.
4. Add screenshots and Playwright trace capture.

## Chat-facing image delivery preference

- For Gemini Web image edits, wait for the actually finished render and then send it immediately.
- Do not send washed-out previews, partial overlays, or screenshot-like intermediate captures.
- If the exported image is questionable, verify it first instead of sending fast.
- Avoid duplicate image sends in chat. One verified final image is the desired behavior.
- A high-priority workflow is: the user sends one or more source images into chat, then asks for edits in natural language, and the skill should use those inbound images as edit inputs without making them re-upload or restate technical details.
