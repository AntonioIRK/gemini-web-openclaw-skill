from __future__ import annotations

from pathlib import Path


def ensure_profile_dir(profile_dir: Path) -> Path:
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir
