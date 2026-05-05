# Workflow

This repo's mature execution path is now Gemini Web chat/image automation first, with Storybook as an additional specialized path.

## Core execution path

1. Validate environment and browser runtime with `scripts/ensure_env.sh`.
2. Bootstrap or reuse a persistent Gemini browser profile with `scripts/gemini_web_login.sh`.
3. Confirm session health and current landing behavior with `scripts/gemini_web_doctor.sh`.
4. Optionally inspect the live UI with `scripts/gemini_web_debug_open.sh`.
5. Run one of the mature paths:
   - `scripts/gemini_web.sh chat-ask ...`
   - `scripts/gemini_web_image_create.sh ...`
   - `scripts/gemini_web_image_edit.sh ...`
6. If needed, run `scripts/gemini_web_create.sh --prompt ... --return-mode share_link|pdf` for Storybook.
7. For Storybook, use a patience budget of 10 minutes before concluding the book is not ready.
8. If no link appears after that budget, send one recovery prompt in the same thread.
9. If the book later appears in Storybook history, reopen history items until one visibly matches the current prompt, then retry Share book.
10. If the browser/CDP loop times out or the Chrome port is already in use, restart the browser driver and reopen Storybook before declaring the book failed.
11. Only after the full timeout, recovery prompt, prompt-matched history recheck, browser recovery, and share retry fail should you inspect `debug_artifacts_path` and change selectors or assumptions.

## Library bookkeeping flow

- After a successful book, if the user wants a library, upload the PDF to the Drive `PDF` folder.
- Append or update the spreadsheet index with:
  - creation date
  - book title
  - Storybook link
  - PDF Drive link
  - notes
- Keep the spreadsheet as the source of truth for the library list.
- Mark PDF as pending if export is unavailable, rather than leaving the entry ambiguous.

## Limits to state honestly

- No published hard cap was found for the number of Storybooks a user can create.
- The only clear product limit found is that a Storybook is a 10-page book.
- In docs and replies, say "no published hard cap found" rather than "unlimited".

## Image-delivery rule for live chat usage

For `image-create`, do not treat the first visible preview or screenshot layer as final output.

- Wait until the Gemini image card is fully rendered.
- Prefer the UI action equivalent to `Скачать изображение в полном размере` / full-size download over raw screenshot capture.
- Only send the image to chat after the downloaded file is verified as a real full-size asset, not a washed-out overlay, thumbnail, or mid-generation preview.
- In Telegram-facing flows, send one final image only, with no duplicate resend unless the first delivery actually failed.

## State machine target

- INIT
- OPENING_GEMINI
- CHECKING_LOGIN
- LOCATING_TARGET_SURFACE
- UPLOADING_FILES
- SUBMITTING_PROMPT
- WAITING_FOR_GENERATION
- DOWNLOADING_FINAL_IMAGE
- EXTRACTING_SHARE_LINK
- EXPORTING_PDF
- COMPLETED
- FAILED

## Research-backed constraints

- Storybook support is a UI workflow first, not a guaranteed reverse-engineered API surface.
- Session reuse should prefer a persistent dedicated profile over raw cookie extraction.
- Network inspection is phase 2 hardening, not a substitute for the UI MVP.
