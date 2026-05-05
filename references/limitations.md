# Known limitations

## Current scaffold limitations

- Storybook selectors now have live current-account validation for the share-link path, but they are still brittle and not strong enough for a broad cross-account guarantee.
- Storybook file-upload wiring is still incomplete. Image create and image edit upload paths are live-wired; Storybook-specific upload remains partially scaffolded.
- Share-link extraction now follows the observed Storybook history/root → open book → Share book path on the current account, but it remains account-dependent.
- PDF export may need a more stable route than direct `page.pdf()` depending on the final page structure.

## Product limitations

- Storybook may not be enabled in every Gemini account.
- Login/session state may expire because of Google re-verification or device checks.
- DOM labels and text anchors may change without notice.
- This skill must not bypass CAPTCHA, 2FA, or anti-bot checks.
- This project is a better fit for self-hosted or operator-side use than for multi-user SaaS auth flows.
