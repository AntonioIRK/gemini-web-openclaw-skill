from __future__ import annotations

from pathlib import Path
from playwright.sync_api import Page

from ..exceptions import PdfExportFailedError


def export_pdf(page: Page, output_path: str | None, workspace_root: Path) -> str:
    if not output_path:
        raise PdfExportFailedError("output_path is required for return_mode=pdf")
    path = Path(output_path).resolve()
    if not path.is_relative_to(workspace_root):
        raise ValueError("Path traversal detected")
    try:
        page.pdf(path=str(path), print_background=True)
    except Exception as exc:  # pragma: no cover - depends on live runtime
        raise PdfExportFailedError(str(exc)) from exc
    return str(path)
