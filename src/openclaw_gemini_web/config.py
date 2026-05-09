from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class GeminiWebConfig:
    workspace_root: Path
    profile_dir: Path
    diagnostics_root: Path
    state_path: Path
    base_url: str = "https://gemini.google.com/"
    timeout_seconds: int = 300
    headless: bool = False
    slow_mo_ms: int = 0
    remote_debugging_port: int | None = None
    allow_cdp_attach: bool = False
    diagnostics_retention_days: int = 7

    @classmethod
    def from_env(cls) -> "GeminiWebConfig":
        workspace_root = Path(
            os.environ.get(
                "GEMINI_WEB_ROOT", os.environ.get("GEMINI_STORYBOOK_ROOT", Path.cwd())
            )
        ).resolve()
        default_profile_dir = workspace_root / ".gemini-web-profile"
        legacy_profile_dir = workspace_root / ".gemini-storybook-profile"
        profile_dir = Path(
            os.environ.get(
                "GEMINI_WEB_PROFILE_DIR",
                os.environ.get(
                    "GEMINI_STORYBOOK_PROFILE_DIR",
                    legacy_profile_dir
                    if legacy_profile_dir.exists()
                    else default_profile_dir,
                ),
            )
        ).resolve()
        diagnostics_root = Path(
            os.environ.get(
                "GEMINI_WEB_DIAGNOSTICS_DIR",
                os.environ.get(
                    "GEMINI_STORYBOOK_DIAGNOSTICS_DIR",
                    workspace_root / "tmp" / "gemini-web-runs",
                ),
            )
        ).resolve()
        state_path = Path(
            os.environ.get(
                "GEMINI_WEB_STATE_PATH",
                os.environ.get(
                    "GEMINI_STORYBOOK_STATE_PATH",
                    workspace_root / "tmp" / "gemini-web-state.json",
                ),
            )
        ).resolve()
        timeout_seconds = int(
            os.environ.get(
                "GEMINI_WEB_TIMEOUT", os.environ.get("GEMINI_STORYBOOK_TIMEOUT", "300")
            )
        )
        headless = os.environ.get(
            "GEMINI_WEB_HEADLESS", os.environ.get("GEMINI_STORYBOOK_HEADLESS", "0")
        ) in {"1", "true", "TRUE"}
        slow_mo_ms = int(
            os.environ.get(
                "GEMINI_WEB_SLOW_MO_MS",
                os.environ.get("GEMINI_STORYBOOK_SLOW_MO_MS", "0"),
            )
        )
        remote_debugging_port = os.environ.get(
            "GEMINI_WEB_REMOTE_DEBUGGING_PORT",
            os.environ.get("GEMINI_STORYBOOK_REMOTE_DEBUGGING_PORT", ""),
        ).strip()
        allow_cdp_attach = os.environ.get(
            "GEMINI_WEB_ALLOW_CDP_ATTACH",
            os.environ.get("GEMINI_STORYBOOK_ALLOW_CDP_ATTACH", "0"),
        ) in {"1", "true", "TRUE"}
        diagnostics_retention_days = int(
            os.environ.get(
                "GEMINI_WEB_DIAGNOSTICS_RETENTION_DAYS",
                os.environ.get("GEMINI_STORYBOOK_DIAGNOSTICS_RETENTION_DAYS", "7"),
            )
        )
        return cls(
            workspace_root=workspace_root,
            profile_dir=profile_dir,
            diagnostics_root=diagnostics_root,
            state_path=state_path,
            timeout_seconds=timeout_seconds,
            headless=headless,
            slow_mo_ms=slow_mo_ms,
            remote_debugging_port=int(remote_debugging_port)
            if remote_debugging_port
            else None,
            allow_cdp_attach=allow_cdp_attach,
            diagnostics_retention_days=diagnostics_retention_days,
        )


StorybookConfig = GeminiWebConfig
