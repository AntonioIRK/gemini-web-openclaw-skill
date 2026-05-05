# Support matrix

This matrix is intentionally conservative.

## Supported target shape today

| Area | Status | Notes |
|---|---|---|
| Linux desktop or desktop-capable host | Supported | Best fit for local install and operator-managed use |
| Ubuntu 22.04 / 24.04 | Best-tested | Preferred baseline for current docs |
| Python 3.11 / 3.12 | Supported | Required by package and setup flow |
| OpenClaw install under `~/.openclaw/workspace/skills/gemini-web` | Supported | Recommended skill checkout path |
| Local Gemini login in the host browser | Supported | Recommended auth path |
| Remote server with real GUI desktop access | Supported with caution | Requires honest server-side login model |

## Honest operator/public contract

| Area | Status | Notes |
|---|---|---|
| Public GitHub release | Supported with caution | Suitable for operator-oriented self-hosted release, not mass-market onboarding |
| Free/public expectation | Limited | No guarantee that every account, region, or plan exposes the same Gemini surfaces |
| Required auth model | Required | A real Gemini Web browser session must exist on the actual runtime host |
| Stable public promise | Supported | `chat-ask`, `image-create`, `image-edit` |
| Storybook/Gems availability | Not guaranteed | Treat as account-dependent and non-core for public release |

## Reliable feature surfaces today

| Surface | Status | Notes |
|---|---|---|
| `chat-ask` | Reliable | Best current text workflow |
| `image-create` | Reliable with runtime caveats | Can still be affected by Google-side latency/timeouts |
| `image-edit` | Reliable | Strongest image path observed so far |
| `doctor` | Basic validation only | Environment and session heuristic, not full readiness proof |
| `inspect-home` | Reliable | Good surface visibility check after login |

## Experimental surfaces today

| Surface | Status | Notes |
|---|---|---|
| Storybook `smoke` | Experimental diagnostic only | Useful probe, not guaranteed workflow |
| Storybook `create --return-mode share_link` | Experimental, live-validated on current account | Real current-account evidence exists, but not strong enough for the stable public promise |
| Storybook file upload | Not public-release-ready | Still partially scaffolded |
| Storybook PDF export | Not public-release-ready | Not yet a stable public promise |

## Not recommended

| Environment | Status | Why |
|---|---|---|
| Headless VPS with no GUI access | Not recommended | No honest Gemini login path |
| Python 3.10 or lower | Unsupported | Fails package requirement |
| Users unwilling to sign into Google on the actual runtime host | Not recommended | Breaks the persistent-profile model |
| Expecting plug-and-play SaaS onboarding | Not recommended | This is an operator-oriented self-hosted tool |
