# Authentication

This repo uses a **real Gemini Web browser session** on the actual runtime host.

## Local install

Recommended.

- Login happens in the browser on the local machine.
- The persistent Gemini profile stays there.

## Remote install

Possible, but more awkward.

- Login happens in the browser profile on the remote host.
- Google may require extra verification.
- If you do not want Google login on the remote host, prefer local install.

## Safety boundary

This repo does **not** bypass:

- CAPTCHA
- 2FA
- device verification
- Google account security checks

For the full operator runbook, see `../references/remote-install-and-auth.md` and `../references/auth-script.md`.
