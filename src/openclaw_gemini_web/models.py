from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowState(str, Enum):
    INIT = "INIT"
    OPENING_GEMINI = "OPENING_GEMINI"
    CHECKING_LOGIN = "CHECKING_LOGIN"
    LOCATING_TARGET_SURFACE = "LOCATING_TARGET_SURFACE"
    LOCATING_STORYBOOK = "LOCATING_STORYBOOK"
    UPLOADING_FILES = "UPLOADING_FILES"
    SUBMITTING_PROMPT = "SUBMITTING_PROMPT"
    WAITING_FOR_GENERATION = "WAITING_FOR_GENERATION"
    DOWNLOADING_FINAL_IMAGE = "DOWNLOADING_FINAL_IMAGE"
    EXTRACTING_SHARE_LINK = "EXTRACTING_SHARE_LINK"
    EXPORTING_PDF = "EXPORTING_PDF"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(slots=True)
class GeminiWebCreateRequest:
    prompt: str
    files: list[str] = field(default_factory=list)
    return_mode: str = "share_link"
    output_path: str | None = None
    timeout_seconds: int = 300
    debug: bool = False


@dataclass(slots=True)
class RunDiagnostics:
    run_dir: Path
    state: WorkflowState = WorkflowState.INIT
    screenshots: list[str] = field(default_factory=list)
    html_snapshot: str | None = None
    console_log: str | None = None
    trace_path: str | None = None


@dataclass(slots=True)
class GeminiWebCreateResult:
    status: str
    share_link: str | None = None
    pdf_path: str | None = None
    title: str | None = None
    debug_artifacts_path: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not self.metadata:
            data.pop("metadata", None)
        return data


StorybookRequest = GeminiWebCreateRequest
StorybookResult = GeminiWebCreateResult


@dataclass(slots=True)
class GeminiWebResult:
    status: str
    text: str | None = None
    image_paths: list[str] = field(default_factory=list)
    title: str | None = None
    page_url: str | None = None
    debug_artifacts_path: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not self.metadata:
            data.pop("metadata", None)
        return data


@dataclass(slots=True)
class GeminiImageRequest:
    prompt: str
    files: list[str] = field(default_factory=list)
    timeout_seconds: int = 300
    new_thread: bool = False
    mode: str = "image-create"
