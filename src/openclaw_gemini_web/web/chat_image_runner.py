from __future__ import annotations

from ..auth.login_flow import require_login
from ..models import GeminiImageRequest, GeminiWebResult, WorkflowState
from .base_runner import GeminiWebRunnerBase


class ChatImageRunner(GeminiWebRunnerBase):
    def ask_chat(
        self, prompt: str, timeout_seconds: int = 120, new_thread: bool = False
    ) -> GeminiWebResult:
        with self._workflow_session(GeminiWebResult) as session:
            diag, machine, page, console_lines = (
                session.diag,
                session.machine,
                session.page,
                session.console_lines,
            )
            machine.advance(WorkflowState.OPENING_GEMINI)
            self.diagnostics.write_state(diag, machine.current)
            resume_url = (
                None if new_thread else self.state.get_active_chat_url("chat-ask")
            )
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
            session.result = GeminiWebResult(
                status="success",
                text=answer_text,
                title=page.title(),
                page_url=page.url,
                debug_artifacts_path=str(diag.run_dir),
                metadata={"prompt": prompt},
            )
        return session.result

    def create_image(self, request: GeminiImageRequest) -> GeminiWebResult:
        mode_key = request.mode or "image-create"
        with self._workflow_session(GeminiWebResult) as session:
            diag, machine, page, console_lines = (
                session.diag,
                session.machine,
                session.page,
                session.console_lines,
            )
            machine.advance(WorkflowState.OPENING_GEMINI)
            self.diagnostics.write_state(diag, machine.current)
            resume_url = (
                None if request.new_thread else self.state.get_active_chat_url(mode_key)
            )
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

            if not resume_url:
                self._try_click_create_image(page)
            self._capture_page(diag, page, "image-mode")
            existing_images = {
                self._image_identity(img)
                for img in self._collect_candidate_images(
                    page, latest_response_only=True
                )
            }

            if request.files:
                machine.advance(WorkflowState.UPLOADING_FILES)
                self.diagnostics.write_state(
                    diag, machine.current, {"files": request.files}
                )
                self._upload_files(page, request.files)
                self._capture_page(diag, page, "files-uploaded")

            machine.advance(WorkflowState.SUBMITTING_PROMPT)
            self.diagnostics.write_state(diag, machine.current)
            self._submit_prompt(page, request.prompt)
            self._capture_page(diag, page, "prompt-submitted")

            machine.advance(WorkflowState.WAITING_FOR_GENERATION)
            self.diagnostics.write_state(diag, machine.current)
            images = self._wait_for_generated_images(
                page, request.timeout_seconds, existing_images=existing_images
            )
            self._wait_until_image_download_ready(page, request.timeout_seconds)
            self._capture_page(diag, page, "generation-finished")

            saved_paths = self._download_generated_images(page, diag.run_dir)
            if not saved_paths:
                saved_paths = self._save_images(
                    page, images, diag.run_dir, prefer_screenshot=False
                )
            self.state.set_active_chat_url(mode_key, page.url)
            machine.advance(WorkflowState.COMPLETED)
            self.diagnostics.write_state(diag, machine.current)
            self.diagnostics.write_console(diag, console_lines)
            session.result = GeminiWebResult(
                status="success",
                image_paths=saved_paths,
                title=page.title(),
                page_url=page.url,
                debug_artifacts_path=str(diag.run_dir),
                metadata={
                    "prompt": request.prompt,
                    "image_count": len(saved_paths),
                    "files": request.files,
                    "mode": mode_key,
                },
            )
        return session.result
