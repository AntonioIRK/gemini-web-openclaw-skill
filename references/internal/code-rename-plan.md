# Code-facing rename plan

This plan is for a safe transition from Storybook-era internal naming toward Gemini-Web-first naming without breaking the current working runtime.

## Goal

Make the implementation surface match the current product framing:

- product identity: Gemini Web account-session skill
- mature core: `chat-ask`, `image-create`, `image-edit`
- Storybook: additional specialized or experimental surface

## What should not happen

- do not break working wrappers all at once
- do not remove old entrypoints before aliases exist
- do not rename code and docs in one risky sweep without a compatibility layer
- do not let public naming claim the rename is finished before the runtime agrees

## Current Storybook-heavy layers

### Layer 1, public-safe to keep aliased for now

- `gemini-storybook-skill` CLI alias
- `scripts/gemini_storybook_*.sh`

These can stay as compatibility entrypoints while new primary names are introduced.

### Layer 2, should get Gemini-Web-first primary names next

- Python package `openclaw_gemini_storybook`
- `GeminiStorybookClient`
- `StorybookConfig`
- `StorybookRequest`
- `StorybookResult`
- `StorybookStateMachine`
- `StorybookError`
- `LOCATING_STORYBOOK` as a shared workflow state
- diagnostics directory names like `storybook-run-*`

### Layer 3, can stay Storybook-specific

- `StorybookRunner`
- `StorybookNotAvailableError`
- `export/share_link.py`
- `export/pdf_export.py`
- selectors and code that are genuinely Storybook-only

Those are allowed to remain Storybook-specific because they model the actual Storybook surface.

## Recommended migration order

### Phase A, add Gemini-Web-first aliases first

Low-risk goal: introduce new primary names while keeping current names working.

Recommended additions:

- package alias path or migration shim toward `openclaw_gemini_web`
- `GeminiWebClient` alias for `GeminiStorybookClient`
- `GeminiWebConfig` alias for `StorybookConfig`
- `GeminiWebRequest` / `GeminiWebCreateRequest` alias for current Storybook request shape
- `GeminiWebCreateResult` alias for current Storybook result shape
- `GeminiWebStateMachine` alias for `StorybookStateMachine`
- `GeminiWebError` base alias for `StorybookError`

At this phase, old names remain valid and tests should cover both names where practical.

### Phase B, switch internal call sites to new primary names

After aliases exist, update internal imports and public docs to prefer Gemini-Web-first names.

Priority order:

1. `client.py`
2. `cli.py`
3. `skill/openclaw_adapter.py`
4. tests
5. config and diagnostics helpers
6. shared workflow/state definitions

Expected outcome:

- docs and code samples stop importing Storybook-first core classes
- Storybook names remain only in Storybook-specific runner code and aliases

### Phase C, add new wrapper primaries

Introduce new primary wrapper names while keeping old ones as passthrough aliases.

Recommended new wrappers:

- `scripts/gemini_web.sh`
- `scripts/gemini_web_login.sh`
- `scripts/gemini_web_doctor.sh`
- `scripts/gemini_web_inspect_home.sh`
- `scripts/gemini_web_image_create.sh`
- `scripts/gemini_web_image_edit.sh`
- `scripts/gemini_web_create.sh`
- `scripts/gemini_web_smoke.sh`

Keep `gemini_storybook_*` wrappers as compatibility shims that exec the new primary wrappers.

### Phase D, reduce Storybook-heavy shared terminology

Rename shared concepts that affect all modes:

- `LOCATING_STORYBOOK` -> `LOCATING_TARGET_SURFACE`
- diagnostics folder `storybook-run-*` -> `gemini-web-run-*`
- generic timeout text mentioning Storybook during non-Storybook flows

Do not rename Storybook-specific runner methods that truly belong only to that surface.

### Phase E, package-path transition

This is the highest-risk step and should happen last.

Possible target:

- new package: `openclaw_gemini_web`

Safe approach:

1. add new package path as thin re-export layer
2. point `gemini-web-skill` entrypoint to the new package path
3. keep old package path as compatibility bridge
4. migrate imports gradually
5. only later consider removing old path

## Minimal safe first implementation pass

If doing only one small code rename pass now, do this:

1. add `GeminiWebClient` alias
2. add `GeminiWebConfig` alias
3. add `GeminiWebError` alias
4. add `GeminiWebStateMachine` alias
5. change docs and adapter imports to prefer those names
6. add `gemini_web*.sh` primary wrappers, keep old wrappers as aliases

This yields visible coherence without destabilizing the working runtime.

## Risk boundaries

### Low risk

- new aliases
- new wrapper names delegating to old runtime
- docs switching to Gemini-Web-first names
- diagnostic directory rename with compatibility read path if needed

### Medium risk

- changing shared workflow state names
- changing model names used in tests and adapters
- switching default import paths across the repo

### High risk

- renaming the package directory itself
- changing console entrypoints without alias preservation
- changing env var names without fallback support

## Environment variable strategy

Current env vars are Storybook-heavy. Do not hard-break them.

Recommended migration pattern:

- support new `GEMINI_WEB_*` names first
- keep reading `GEMINI_STORYBOOK_*` as fallback
- document that old names are compatibility aliases

## Definition of done for the rename project

The rename transition is in a good state when:

- primary docs use Gemini-Web-first names consistently
- primary wrappers use `gemini_web*`
- client/config/error/state shared names are Gemini-Web-first
- Storybook names remain only where the code is truly Storybook-specific
- old Storybook names still work as compatibility aliases
- tests cover at least the primary new names and one legacy alias path
