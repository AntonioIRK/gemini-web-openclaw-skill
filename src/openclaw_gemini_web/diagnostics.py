from __future__ import annotations

from datetime import datetime, UTC
from datetime import timedelta
from pathlib import Path
import json
import shutil
import re

from .models import RunDiagnostics, WorkflowState


class DiagnosticsManager:
    def __init__(self, diagnostics_root: Path, retention_days: int = 7):
        self.diagnostics_root = diagnostics_root
        self.retention_days = retention_days
        self.diagnostics_root.mkdir(parents=True, exist_ok=True)
        self._prune_old_runs()

    def create(self) -> RunDiagnostics:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_dir = self.diagnostics_root / f"gemini-web-run-{stamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return RunDiagnostics(run_dir=run_dir)

    def _prune_old_runs(self) -> None:
        retention_days = self.retention_days
        if retention_days <= 0:
            return
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        for path in self.diagnostics_root.glob("gemini-web-run-*"):
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime, UTC)
            except FileNotFoundError:
                continue
            if mtime < cutoff:
                shutil.rmtree(path, ignore_errors=True)

    def write_state(self, diag: RunDiagnostics, state: WorkflowState, extra: dict | None = None) -> None:
        diag.state = state
        payload = {"state": state.value}
        if extra:
            payload["extra"] = extra
        (diag.run_dir / "state.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        with (diag.run_dir / "state-history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def write_console(self, diag: RunDiagnostics, lines: list[str]) -> None:
        path = diag.run_dir / "console.log"
        path.write_text("\n".join(lines), encoding="utf-8")
        diag.console_log = str(path)

    def write_html(self, diag: RunDiagnostics, html: str) -> None:
        path = diag.run_dir / "page.html"
        clean_html = re.sub(r"<(script|style).*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL)
        path.write_text(clean_html, encoding="utf-8")
        diag.html_snapshot = str(path)

    def write_screenshot(self, diag: RunDiagnostics, page, name: str = "page.png") -> str:
        path = diag.run_dir / name
        page.screenshot(path=str(path), full_page=True)
        diag.screenshots.append(str(path))
        return str(path)

    def write_json(self, diag: RunDiagnostics, name: str, payload: dict) -> str:
        path = diag.run_dir / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
