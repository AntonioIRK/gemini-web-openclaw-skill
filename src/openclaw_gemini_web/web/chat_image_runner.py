from __future__ import annotations

from ..auth.login_flow import require_login
from ..exceptions import GeminiWebError
import time
from typing import Iterator
from ..models import GeminiImageRequest, GeminiWebResult, WorkflowState
from .base_runner import GeminiWebRunnerBase
from .browser import open_persistent_page
from .state_machine import GeminiWebStateMachine


class ChatImageRunner(GeminiWebRunnerBase):
    def ask_chat(self, prompt: str, timeout_seconds: int = 120, new_thread: bool = False) -> GeminiWebResult:
        diag = self.diagnostics.create()
        machine = GeminiWebStateMachine()
        console_lines: list[str] = []
        page = None
        try:
            with open_persistent_page(self.config) as (_context, page):
                page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
                machine.advance(WorkflowState.OPENING_GEMINI)
                self.diagnostics.write_state(diag, machine.current)
                resume_url = None if new_thread else self.state.get_active_chat_url("chat-ask")
                page.goto(resume_url or self.config.base_url, wait_until="domcontentloaded")
                if resume_url and self._chat_missing(page):
                    self.state.clear_active_chat_url("chat-ask")
                    page.goto(self.config.base_url, wait_until="domcontentloaded")
                self._capture_page(diag, page, "opening-gemini")

                machine.advance(WorkflowState.CHECKING_LOGIN)
                self.diagnostics.write_state(diag, machine.current)
                require_login(page)
                page.wait_for_timeout(3000)

                machine.advance(WorkflowState.SUBMITTING_PROMPT)
                self.diagnostics.write_state(diag, machine.current)
                self._submit_prompt(page, prompt)
                self._capture_page(diag, page, "prompt-submitted")

                machine.advance(WorkflowState.WAITING_FOR_GENERATION)
                self.diagnostics.write_state(diag, machine.current)
                answer_text = self._wait_for_text_response(page, timeout_seconds)
                self._capture_page(diag, page, "generation-finished")

                self.state.set_active_chat_url("chat-ask", page.url)
                machine.advance(WorkflowState.COMPLETED)
                self.diagnostics.write_state(diag, machine.current)
                self.diagnostics.write_console(diag, console_lines)
                return GeminiWebResult(
                    status="success",
                    text=answer_text,
                    title=page.title(),
                    page_url=page.url,
                    debug_artifacts_path=str(diag.run_dir),
                    metadata={"prompt": prompt},
                )
        except GeminiWebError as exc:
            machine.advance(WorkflowState.FAILED)
            self.diagnostics.write_state(diag, machine.current)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, exc.code, str(exc)))
            return GeminiWebResult(
                status="error", debug_artifacts_path=str(diag.run_dir), error_code=exc.code, error_message=str(exc), page_url=getattr(page, "url", None)
            )
        except Exception as exc:
            machine.advance(WorkflowState.FAILED)
            self.diagnostics.write_state(diag, machine.current)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, "UNKNOWN_RUNTIME_ERROR", str(exc)))
            return GeminiWebResult(
                status="error",
                debug_artifacts_path=str(diag.run_dir),
                error_code="UNKNOWN_RUNTIME_ERROR",
                error_message=str(exc),
                page_url=getattr(page, "url", None),
            )

    def ask_chat_stream(self, prompt: str, timeout_seconds: int = 120, new_thread: bool = False) -> Iterator[str]:
        self.diagnostics.create()
        machine = GeminiWebStateMachine()
        console_lines: list[str] = []
        page = None
        try:
            with open_persistent_page(self.config) as (_context, page):
                page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
                machine.advance(WorkflowState.OPENING_GEMINI)
                resume_url = None if new_thread else self.state.get_active_chat_url("chat-ask")
                page.goto(resume_url or self.config.base_url, wait_until="domcontentloaded")
                if resume_url and self._chat_missing(page):
                    self.state.clear_active_chat_url("chat-ask")
                    page.goto(self.config.base_url, wait_until="domcontentloaded")

                machine.advance(WorkflowState.CHECKING_LOGIN)
                require_login(page)
                page.wait_for_timeout(3000)

                machine.advance(WorkflowState.SUBMITTING_PROMPT)
                self._submit_prompt(page, prompt)

                machine.advance(WorkflowState.WAITING_FOR_GENERATION)
                deadline = time.time() + timeout_seconds
                last_text = ""

                while time.time() < deadline:
                    body_text = self._read_body_text(page)
                    google_error = self._detect_google_error(body_text)
                    if google_error:
                        yield f"\n[Error: {str(google_error)}]"
                        return

                    try:
                        latest_responses = page.locator("model-response")
                        if latest_responses.count() > 0:
                            current_text = latest_responses.last.inner_text().strip()
                            if current_text and current_text != last_text:
                                # Yield only the new part of the text
                                new_part = current_text[len(last_text) :]
                                if new_part:
                                    yield new_part
                                last_text = current_text
                    except Exception:
                        pass

                    try:
                        import re

                        stop_buttons = page.get_by_role("button", name=re.compile("Остановить|Stop", re.I))
                        stop_visible = stop_buttons.count() > 0
                    except Exception:
                        stop_visible = False

                    # To avoid premature exit, ensure we have text and no "generating" indicators
                    is_generating = any(text in body_text for text in self.selectors.generating_texts)
                    if not stop_visible and not is_generating and len(last_text) > 0:
                        # Extra wait to ensure UI is fully settled
                        page.wait_for_timeout(1000)
                        final_text = ""
                        try:
                            if latest_responses.count() > 0:
                                final_text = latest_responses.last.inner_text().strip()
                        except Exception:
                            pass

                        if final_text and final_text != last_text:
                            new_part = final_text[len(last_text) :]
                            if new_part:
                                yield new_part

                        self.state.set_active_chat_url("chat-ask", page.url)
                        machine.advance(WorkflowState.COMPLETED)
                        return

                    page.wait_for_timeout(500)

                yield f"\n[Error: GenerationTimeoutError within {timeout_seconds} seconds]"
        except Exception as exc:
            yield f"\n[Error: {str(exc)}]"

    def create_image(self, request: GeminiImageRequest) -> GeminiWebResult:
        diag = self.diagnostics.create()
        machine = GeminiWebStateMachine()
        console_lines: list[str] = []
        page = None
        mode_key = request.mode or "image-create"
        is_document_analysis = mode_key == "document-analysis"
        try:
            with open_persistent_page(self.config) as (_context, page):
                page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
                machine.advance(WorkflowState.OPENING_GEMINI)
                self.diagnostics.write_state(diag, machine.current)
                resume_url = None if request.new_thread else self.state.get_active_chat_url(mode_key)
                page.goto(resume_url or self.config.base_url, wait_until="domcontentloaded")
                if resume_url and self._chat_missing(page):
                    self.state.clear_active_chat_url(mode_key)
                    resume_url = None
                    page.goto(self.config.base_url, wait_until="domcontentloaded")
                self._capture_page(diag, page, "opening-gemini")

                machine.advance(WorkflowState.CHECKING_LOGIN)
                self.diagnostics.write_state(diag, machine.current)
                require_login(page)
                page.wait_for_timeout(3000)

                if not resume_url and not is_document_analysis:
                    self._try_click_create_image(page)
                self._capture_page(diag, page, "image-mode")
                existing_images = {self._image_identity(img) for img in self._collect_candidate_images(page, latest_response_only=True)}

                if request.files:
                    machine.advance(WorkflowState.UPLOADING_FILES)
                    self.diagnostics.write_state(diag, machine.current, {"files": request.files})
                    self._upload_files(page, request.files)
                    self._capture_page(diag, page, "files-uploaded")

                machine.advance(WorkflowState.SUBMITTING_PROMPT)
                self.diagnostics.write_state(diag, machine.current)
                self._submit_prompt(page, request.prompt)
                self._capture_page(diag, page, "prompt-submitted")

                machine.advance(WorkflowState.WAITING_FOR_GENERATION)
                self.diagnostics.write_state(diag, machine.current)

                if is_document_analysis:
                    answer_text = self._wait_for_text_response(page, request.timeout_seconds)
                    self._capture_page(diag, page, "generation-finished")
                    self.state.set_active_chat_url(mode_key, page.url)
                    machine.advance(WorkflowState.COMPLETED)
                    self.diagnostics.write_state(diag, machine.current)
                    self.diagnostics.write_console(diag, console_lines)
                    return GeminiWebResult(
                        status="success",
                        text=answer_text,
                        title=page.title(),
                        page_url=page.url,
                        debug_artifacts_path=str(diag.run_dir),
                        metadata={"prompt": request.prompt, "files": request.files, "mode": mode_key},
                    )
                else:
                    images = self._wait_for_generated_images(page, request.timeout_seconds, existing_images=existing_images)
                    self._wait_until_image_download_ready(page, request.timeout_seconds)
                    self._capture_page(diag, page, "generation-finished")

                    saved_paths = self._download_generated_images(page, diag.run_dir)
                    if not saved_paths:
                        saved_paths = self._save_images(page, images, diag.run_dir, prefer_screenshot=False)
                    self.state.set_active_chat_url(mode_key, page.url)
                    machine.advance(WorkflowState.COMPLETED)
                    self.diagnostics.write_state(diag, machine.current)
                    self.diagnostics.write_console(diag, console_lines)
                    return GeminiWebResult(
                        status="success",
                        image_paths=saved_paths,
                        title=page.title(),
                        page_url=page.url,
                        debug_artifacts_path=str(diag.run_dir),
                        metadata={"prompt": request.prompt, "image_count": len(saved_paths), "files": request.files, "mode": mode_key},
                    )
        except GeminiWebError as exc:
            machine.advance(WorkflowState.FAILED)
            self.diagnostics.write_state(diag, machine.current)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, exc.code, str(exc)))
            return GeminiWebResult(
                status="error", debug_artifacts_path=str(diag.run_dir), error_code=exc.code, error_message=str(exc), page_url=getattr(page, "url", None)
            )
        except Exception as exc:
            machine.advance(WorkflowState.FAILED)
            self.diagnostics.write_state(diag, machine.current)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, "UNKNOWN_RUNTIME_ERROR", str(exc)))
            return GeminiWebResult(
                status="error",
                debug_artifacts_path=str(diag.run_dir),
                error_code="UNKNOWN_RUNTIME_ERROR",
                error_message=str(exc),
                page_url=getattr(page, "url", None),
            )
