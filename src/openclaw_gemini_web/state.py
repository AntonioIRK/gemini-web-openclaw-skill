from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class GeminiWebState:
    path: Path

    def load(self) -> dict:
        try:
            if not self.path.exists():
                return {}
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, state: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_active_chat_url(self, mode: str) -> str | None:
        state = self.load()
        value = state.get("activeChats", {}).get(mode)
        if isinstance(value, str) and value.startswith(
            "https://gemini.google.com/app/"
        ):
            return value
        return None

    def set_active_chat_url(self, mode: str, url: str) -> None:
        if not url or not url.startswith("https://gemini.google.com/app/"):
            return
        state = self.load()
        active = state.setdefault("activeChats", {})
        active[mode] = url
        self.save(state)

    def clear_active_chat_url(self, mode: str) -> None:
        state = self.load()
        active = state.setdefault("activeChats", {})
        active.pop(mode, None)
        self.save(state)
