# Public release checklist

Use this before turning the repo public.

## Secrets and hygiene

- [ ] no browser profiles in git
- [ ] no `.venv/`, `tmp/`, `build/`, `dist/`, `__pycache__/`, or `*.egg-info/` in git
- [ ] no diagnostic artifacts accidentally committed
- [ ] no secrets found by regex scan
- [ ] no sensitive files lingering in git history

## Safe staging flow

Use an explicit staged-file review before opening the repo public.

- [ ] start with `git status --short`
- [ ] avoid blind `git add .`
- [ ] stage only intended public files explicitly
- [ ] run `git diff --cached --name-only`
- [ ] run `git diff --cached`
- [ ] confirm no profile, diagnostics, temp, or local auth artifacts are staged

## Product framing

- [ ] README states that Gemini Web chat/image automation is the mature core today
- [ ] Storybook is framed as experimental
- [ ] local install is stated as the recommended path
- [ ] remote auth is explained honestly
- [ ] no text suggests magic headless auth or stealth login

## Documentation

- [ ] prerequisites are current
- [ ] support matrix is current
- [ ] auth script is current
- [ ] remote install runbook is current
- [ ] privacy guidance for diagnostics is present
- [ ] validation flow is current

## Validation

- [ ] package install works from a clean checkout
- [ ] unit tests pass
- [ ] CLI help works
- [ ] local validation path has been exercised recently
- [ ] at least one real Gemini account was used for post-login validation

## Naming and release polish

- [ ] public-facing naming is coherent enough
- [ ] transitional Storybook-era naming is either cleaned up or clearly documented
- [ ] tags, topics, and repo description match the real scope
- [ ] README still matches the actual maturity split: chat/image stable core, Storybook visible but still maturing
