# structure notes

## What is worth preserving in this repo's structure

- **Thin orchestration layer**: keep the skill entrypoint small and push specifics into references and helpers.
- **Live integration notes**: maintain a concrete host-validated note file with what was actually tested.
- **Transport map**: document which wrapper command maps to which underlying runtime behavior.
- **Mode-based thinking**: treat each surface (`chat`, `image`, `storybook`) as a separate mode with explicit expectations.

## What this skill still needs

- browser-automation-aware state handling
- selector and failure management richer than a normal API wrapper needs
- clear separation between mature chat/image flows and experimental Storybook flows

## Practical conclusion

The current direction is correct. The main structural priorities remain:

1. shared base runner
2. per-mode runners
3. live mode status notes
4. explicit wrapper-to-mode mapping
