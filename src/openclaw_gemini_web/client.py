from __future__ import annotations

from .config import GeminiWebConfig
from .diagnostics import DiagnosticsManager
from .models import GeminiImageRequest, GeminiWebCreateRequest, GeminiWebCreateResult, GeminiWebResult
from .web.chat_image_runner import ChatImageRunner
from .web.storybook_runner import StorybookRunner


class GeminiWebClient:
    def __init__(self, config: GeminiWebConfig | None = None):
        self.config = config or GeminiWebConfig.from_env()
        diagnostics = DiagnosticsManager(self.config.diagnostics_root, self.config.diagnostics_retention_days)
        self.storybook_runner = StorybookRunner(self.config, diagnostics)
        self.chat_image_runner = ChatImageRunner(self.config, diagnostics)

    def login(self) -> None:
        self.storybook_runner.login()

    def doctor(self) -> dict:
        return self.storybook_runner.doctor()

    def debug_open(self) -> None:
        self.storybook_runner.debug_open()

    def create(self, request: GeminiWebCreateRequest) -> GeminiWebCreateResult:
        return self.storybook_runner.create(request)

    def inspect_home(self) -> dict:
        return self.storybook_runner.inspect_home()

    def create_image(self, request: GeminiImageRequest) -> GeminiWebResult:
        return self.chat_image_runner.create_image(request)

    def ask_chat(self, prompt: str, timeout_seconds: int = 120, new_thread: bool = False) -> GeminiWebResult:
        return self.chat_image_runner.ask_chat(prompt=prompt, timeout_seconds=timeout_seconds, new_thread=new_thread)

    def ask_chat_stream(self, prompt: str, timeout_seconds: int = 120, new_thread: bool = False):
        return self.chat_image_runner.ask_chat_stream(prompt=prompt, timeout_seconds=timeout_seconds, new_thread=new_thread)


GeminiStorybookClient = GeminiWebClient
