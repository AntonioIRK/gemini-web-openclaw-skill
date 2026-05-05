# Privacy and diagnostics guidance

This repo is diagnostics-first, which is useful for brittle browser automation, but diagnostics require operator discipline.

## What diagnostics may contain

Depending on the failure point, diagnostics can include:

- screenshots
- HTML snapshots
- page text excerpts
- page URLs
- console output

These artifacts may contain session-adjacent or account-adjacent information.

## Safe handling rules

- treat diagnostics as private by default
- inspect artifacts before sharing them publicly
- do not publish screenshots or HTML dumps without reviewing them
- do not commit diagnostics into git
- clean up artifacts when they are no longer needed

## Default retention

The runtime prunes older `gemini-web-run-*` diagnostics automatically after a short retention window. This reduces accidental buildup, but it does not make the artifacts public or disposable.

If you need a longer audit trail, set a longer retention deliberately and keep the directory private.

## Operator guidance

- use diagnostics to debug selectors, auth state, and Google-side failures
- do not confuse diagnostic capture with permission to redistribute account-linked artifacts
- if you need to share a bug report, redact sensitive content first

## Public release recommendation

If this repo is ever made public, keep reminding users that diagnostics are valuable but should be handled like private debug data, not like harmless logs.
