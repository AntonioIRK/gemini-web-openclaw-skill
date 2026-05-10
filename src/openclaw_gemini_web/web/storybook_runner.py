from __future__ import annotations

from pathlib import Path
import re
import time

from ..auth.login_flow import require_login
from ..exceptions import GenerationTimeoutError, GeminiWebError, GoogleRuntimeError13, PromptSubmissionError, ShareLinkNotFoundError, StorybookNotAvailableError
from ..export.pdf_export import export_pdf
from ..export.share_link import extract_share_link
from ..models import GeminiWebCreateRequest, GeminiWebCreateResult, WorkflowState
from .browser import open_persistent_page
from .base_runner import GeminiWebRunnerBase
from .state_machine import GeminiWebStateMachine


class StorybookRunner(GeminiWebRunnerBase):
    STORYBOOK_PATIENCE_SECONDS = 600
    SHARE_LINK_RETRY_SECONDS = 120
    QUIET_COMPLETION_STREAK = 3
    RECOVERY_PROMPT = "Продолжи и заверши книгу в этой же ветке, не меняя тему. Когда книга будет готова, открой Share book и дай ссылку."

    def create(self, request: GeminiWebCreateRequest) -> GeminiWebCreateResult:
        diag = self.diagnostics.create()
        machine = GeminiWebStateMachine()
        console_lines: list[str] = []
        runtime_meta: dict[str, object] = {
            "patience_seconds": max(int(request.timeout_seconds), self.STORYBOOK_PATIENCE_SECONDS),
            "recovery_prompt_used": False,
            "history_reopen_used": False,
            "share_attempts": 0,
            "google_error13_retries": 0,
        }
        page = None
        try:
            with open_persistent_page(self.config) as (context, page):
                page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
                machine.advance(WorkflowState.OPENING_GEMINI)
                self.diagnostics.write_state(diag, machine.current)
                page.goto(self.config.base_url, wait_until="domcontentloaded")
                self._capture_page(diag, page, "opening-gemini")

                machine.advance(WorkflowState.CHECKING_LOGIN)
                self.diagnostics.write_state(diag, machine.current)
                require_login(page)

                machine.advance(WorkflowState.LOCATING_TARGET_SURFACE)
                self.diagnostics.write_state(diag, machine.current)
                if not self._locate_storybook(page):
                    raise StorybookNotAvailableError("Storybook entrypoint was not found in the current Gemini account")
                self._capture_page(diag, page, "storybook-located")

                if request.files:
                    machine.advance(WorkflowState.UPLOADING_FILES)
                    self.diagnostics.write_state(diag, machine.current, {"files": request.files})
                    self._upload_files(page, request.files)

                machine.advance(WorkflowState.SUBMITTING_PROMPT)
                self.diagnostics.write_state(diag, machine.current)
                self._submit_prompt(page, request.prompt)
                self._capture_page(diag, page, "prompt-submitted")

                machine.advance(WorkflowState.WAITING_FOR_GENERATION)
                self.diagnostics.write_state(diag, machine.current)
                effective_timeout = max(int(request.timeout_seconds), self.STORYBOOK_PATIENCE_SECONDS)
                try:
                    self._wait_for_storybook_generation(page, effective_timeout, request.prompt, diag, runtime_meta)
                except GenerationTimeoutError:
                    self._recover_from_timeout(page, request.prompt)
                self._capture_page(diag, page, "generation-finished")

                title = page.title()
                if request.return_mode == "pdf":
                    machine.advance(WorkflowState.EXPORTING_PDF)
                    self.diagnostics.write_state(diag, machine.current)
                    pdf_path = export_pdf(page, request.output_path)
                    machine.advance(WorkflowState.COMPLETED)
                    self.diagnostics.write_state(diag, machine.current)
                    self.diagnostics.write_console(diag, console_lines)
                    return GeminiWebCreateResult(status="success", pdf_path=pdf_path, title=title, debug_artifacts_path=str(diag.run_dir))

                machine.advance(WorkflowState.EXTRACTING_SHARE_LINK)
                self.diagnostics.write_state(diag, machine.current, runtime_meta)
                share_link = self._extract_share_link_with_retry(page, effective_timeout, request.prompt, diag, runtime_meta)
                machine.advance(WorkflowState.COMPLETED)
                runtime_meta["final_page_url"] = getattr(page, "url", None)
                self.diagnostics.write_state(diag, machine.current, runtime_meta)
                self.diagnostics.write_console(diag, console_lines)
                self.diagnostics.write_json(
                    diag,
                    "result.json",
                    {
                        "status": "success",
                        "share_link": share_link,
                        "title": title,
                        "metadata": runtime_meta,
                    },
                )
                self._write_run_summary(diag, "success", runtime_meta, title=title, share_link=share_link)
                return GeminiWebCreateResult(
                    status="success", share_link=share_link, title=title, debug_artifacts_path=str(diag.run_dir), metadata=runtime_meta
                )
        except GeminiWebError as exc:
            machine.advance(WorkflowState.FAILED)
            runtime_meta["final_page_url"] = getattr(page, "url", None)
            runtime_meta["error_code"] = exc.code
            self.diagnostics.write_state(diag, machine.current, runtime_meta)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, exc.code, str(exc)) | {"metadata": runtime_meta})
            self._write_run_summary(diag, "error", runtime_meta, error_code=exc.code, error_message=str(exc))
            return GeminiWebCreateResult(
                status="error", debug_artifacts_path=str(diag.run_dir), error_code=exc.code, error_message=str(exc), metadata=runtime_meta
            )
        except Exception as exc:
            machine.advance(WorkflowState.FAILED)
            runtime_meta["final_page_url"] = getattr(page, "url", None)
            runtime_meta["error_code"] = "UNKNOWN_RUNTIME_ERROR"
            self.diagnostics.write_state(diag, machine.current, runtime_meta)
            self._capture_error_context(diag, page, machine, exc)
            self.diagnostics.write_console(diag, console_lines)
            self.diagnostics.write_json(diag, "error.json", self._error_payload(page, machine, "UNKNOWN_RUNTIME_ERROR", str(exc)) | {"metadata": runtime_meta})
            self._write_run_summary(diag, "error", runtime_meta, error_code="UNKNOWN_RUNTIME_ERROR", error_message=str(exc))
            return GeminiWebCreateResult(
                status="error", debug_artifacts_path=str(diag.run_dir), error_code="UNKNOWN_RUNTIME_ERROR", error_message=str(exc), metadata=runtime_meta
            )

    def _locate_storybook(self, page) -> bool:
        if "/gem/storybook" in page.url:
            return True

        try:
            page.goto(f"{self.config.base_url.rstrip('/')}/gem/storybook", wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            if "/gem/storybook" in page.url:
                return True
        except Exception:
            pass

        for text in self.selectors.storybook_entry_texts:
            locator = page.get_by_text(text, exact=False)
            if locator.count() > 0:
                locator.first.click()
                page.wait_for_timeout(1000)
                if "/gem/storybook" in page.url or locator.count() > 0:
                    return True
        return False

    def _wait_for_storybook_generation(self, page, timeout_seconds: int, prompt: str, diag, runtime_meta: dict[str, object]) -> None:
        deadline = time.time() + timeout_seconds
        loop_count = 0
        quiet_streak = 0
        saw_generation = False
        recovered_error13 = False
        while time.time() < deadline:
            loop_count += 1
            body_text = self._read_body_text(page)
            google_error = self._detect_google_error(body_text)
            if google_error:
                if isinstance(google_error, GoogleRuntimeError13) and not recovered_error13:
                    recovered_error13 = True
                    runtime_meta["google_error13_retries"] = int(runtime_meta.get("google_error13_retries", 0)) + 1
                    runtime_meta["last_google_error"] = str(google_error)
                    self.diagnostics.write_state(diag, WorkflowState.WAITING_FOR_GENERATION, runtime_meta)
                    self._recover_after_google_error13(page, prompt)
                    page.wait_for_timeout(2500)
                    continue
                raise google_error
            try:
                stop_visible = page.get_by_role("button", name=re.compile("Остановить|Stop", re.I)).count() > 0
            except Exception:
                stop_visible = False
            generating = any(text in body_text for text in self.selectors.generating_texts) or stop_visible
            if generating:
                saw_generation = True
                quiet_streak = 0
            else:
                quiet_streak += 1
            if any(text in body_text for text in self.selectors.share_texts):
                runtime_meta["generation_loops"] = loop_count
                runtime_meta["generation_elapsed_seconds"] = int(timeout_seconds - max(0, deadline - time.time()))
                runtime_meta["quiet_completion_streak"] = quiet_streak
                return
            if saw_generation and quiet_streak >= self.QUIET_COMPLETION_STREAK:
                runtime_meta["generation_loops"] = loop_count
                runtime_meta["generation_elapsed_seconds"] = int(timeout_seconds - max(0, deadline - time.time()))
                runtime_meta["quiet_completion_streak"] = quiet_streak
                runtime_meta["generation_settled_without_share_text"] = True
                self.diagnostics.write_state(diag, WorkflowState.WAITING_FOR_GENERATION, runtime_meta)
                return
            if loop_count == 1 or loop_count % 4 == 0:
                runtime_meta["generation_loops"] = loop_count
                runtime_meta["generation_elapsed_seconds"] = int(timeout_seconds - max(0, deadline - time.time()))
                runtime_meta["generating_visible"] = generating
                runtime_meta["quiet_completion_streak"] = quiet_streak
                self.diagnostics.write_state(diag, WorkflowState.WAITING_FOR_GENERATION, runtime_meta)
            page.wait_for_timeout(2000)
        runtime_meta["generation_loops"] = loop_count
        runtime_meta["generation_elapsed_seconds"] = timeout_seconds
        runtime_meta["quiet_completion_streak"] = quiet_streak
        raise GenerationTimeoutError(f"Storybook generation did not finish within {timeout_seconds} seconds")

    def _recover_after_google_error13(self, page, prompt: str) -> None:
        try:
            page.goto(f"{self.config.base_url.rstrip('/')}/gem/storybook", wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
        except Exception:
            pass
        self._reopen_matching_history_item(page, prompt)

    def _upload_files(self, page, files: list[str]) -> None:
        # Placeholder for live DOM wiring.
        missing = [f for f in files if not Path(f).exists()]
        if missing:
            raise PromptSubmissionError(f"Input files do not exist: {missing}")

    def _extract_share_link_with_retry(self, page, deadline_seconds: int, prompt: str, diag, runtime_meta: dict[str, object]) -> str:
        deadline = time.time() + max(int(deadline_seconds), self.STORYBOOK_PATIENCE_SECONDS)
        last_error: Exception | None = None

        if not self._page_has_storybook_share_surface(page):
            if self._reopen_best_history_item(page, prompt):
                runtime_meta["history_reopen_used"] = True
                self.diagnostics.write_state(diag, WorkflowState.EXTRACTING_SHARE_LINK, runtime_meta)

        while time.time() < deadline:
            try:
                if self._page_matches_prompt(page, prompt) or self._page_has_storybook_share_surface(page):
                    runtime_meta["share_attempts"] = int(runtime_meta.get("share_attempts", 0)) + 1
                    self.diagnostics.write_state(diag, WorkflowState.EXTRACTING_SHARE_LINK, runtime_meta)
                    self._capture_page(diag, page, f"share-attempt-{runtime_meta['share_attempts']}")
                    return extract_share_link(page, self.selectors)
                if self._reopen_best_history_item(page, prompt):
                    runtime_meta["history_reopen_used"] = True
                    self.diagnostics.write_state(diag, WorkflowState.EXTRACTING_SHARE_LINK, runtime_meta)
                last_error = ShareLinkNotFoundError("Current Storybook page does not yet expose a prompt match or share surface.")
            except ShareLinkNotFoundError as exc:
                last_error = exc
            page.wait_for_timeout(15000)

        # One recovery pass in the same thread, per operator request, before failing.
        try:
            runtime_meta["recovery_prompt_used"] = True
            self._submit_prompt(page, self.RECOVERY_PROMPT)
            page.wait_for_timeout(2000)
        except Exception as exc:
            last_error = exc

        if self._reopen_matching_history_item(page, prompt):
            runtime_meta["history_reopen_used"] = True
            try:
                runtime_meta["share_attempts"] = int(runtime_meta.get("share_attempts", 0)) + 1
                self.diagnostics.write_state(diag, WorkflowState.EXTRACTING_SHARE_LINK, runtime_meta)
                self._capture_page(diag, page, f"share-attempt-{runtime_meta['share_attempts']}")
                return extract_share_link(page, self.selectors)
            except ShareLinkNotFoundError as exc:
                last_error = exc

        recovery_deadline = time.time() + self.SHARE_LINK_RETRY_SECONDS
        while time.time() < recovery_deadline:
            try:
                if self._page_matches_prompt(page, prompt) or self._page_has_storybook_share_surface(page):
                    runtime_meta["share_attempts"] = int(runtime_meta.get("share_attempts", 0)) + 1
                    self.diagnostics.write_state(diag, WorkflowState.EXTRACTING_SHARE_LINK, runtime_meta)
                    self._capture_page(diag, page, f"share-attempt-{runtime_meta['share_attempts']}")
                    return extract_share_link(page, self.selectors)
                last_error = ShareLinkNotFoundError("Recovered Storybook page does not yet expose a prompt match or share surface.")
            except ShareLinkNotFoundError as exc:
                last_error = exc
            page.wait_for_timeout(10000)

        if last_error:
            raise last_error
        raise ShareLinkNotFoundError("Share link was not found after the full Storybook patience budget.")

    def _recover_from_timeout(self, page, prompt: str) -> None:
        # Late completion happens on this account. Refresh the Storybook root,
        # open the newest book from history, and try to continue from there.
        try:
            page.goto(f"{self.config.base_url.rstrip('/')}/gem/storybook", wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
        except Exception:
            pass

        self._reopen_matching_history_item(page, prompt)

    def _reopen_best_history_item(self, page, prompt: str) -> bool:
        if self._reopen_matching_history_item(page, prompt):
            return True
        items = page.locator('[data-test-id="conversation"]')
        if items.count() == 0:
            return False
        for idx in range(min(items.count(), 4)):
            try:
                self._open_storybook_history_item(page, idx)
                if self._page_has_storybook_share_surface(page):
                    return True
            except Exception:
                continue
        return False

    def _open_storybook_history_item(self, page, index: int = 0) -> None:
        items = page.locator('[data-test-id="conversation"]')
        if items.count() == 0:
            return
        target = items.nth(index if index < items.count() else 0)
        target.click(force=True)
        page.wait_for_timeout(2500)

    def _reopen_matching_history_item(self, page, prompt: str) -> bool:
        items = page.locator('[data-test-id="conversation"]')
        if items.count() == 0:
            return False
        for idx in range(min(items.count(), 6)):
            try:
                target = items.nth(idx)
                target.click(force=True)
                page.wait_for_timeout(2500)
                if self._page_matches_prompt(page, prompt):
                    return True
            except Exception:
                continue
        return False

    def _page_matches_prompt(self, page, prompt: str) -> bool:
        prompt_norm = self._normalize_text(prompt)
        if not prompt_norm:
            return False
        try:
            body = self._read_body_text(page)
        except Exception:
            body = ""
        body_norm = self._normalize_text(body)
        if not body_norm:
            return False
        if prompt_norm in body_norm:
            return True

        prompt_tokens = self._meaningful_tokens(prompt)
        if len(prompt_tokens) < 4:
            return False
        body_tokens = set(self._meaningful_tokens(body))
        return len(set(prompt_tokens[:8]).intersection(body_tokens)) >= 4

    def _page_has_storybook_share_surface(self, page) -> bool:
        for text in self.selectors.share_texts:
            try:
                button = page.get_by_role("button", name=text, exact=False)
                if button.count() > 0:
                    return True
            except Exception:
                continue
        try:
            marker = page.locator('[data-test-id="share-button"]')
            if marker.count() > 0:
                return True
        except Exception:
            pass
        return False

    def _write_run_summary(self, diag, status: str, runtime_meta: dict[str, object], **extra) -> None:
        payload = {
            "status": status,
            "stage": diag.state.value,
            "share_attempts": runtime_meta.get("share_attempts", 0),
            "google_error13_retries": runtime_meta.get("google_error13_retries", 0),
            "recovery_prompt_used": runtime_meta.get("recovery_prompt_used", False),
            "history_reopen_used": runtime_meta.get("history_reopen_used", False),
            "generation_elapsed_seconds": runtime_meta.get("generation_elapsed_seconds"),
            "generating_visible": runtime_meta.get("generating_visible"),
            "final_page_url": runtime_meta.get("final_page_url"),
            "likely_cause": self._likely_cause(runtime_meta, status, extra.get("error_code")),
            "next_step": self._suggested_next_step(runtime_meta, status, extra.get("error_code")),
        }
        payload.update({k: v for k, v in extra.items() if v is not None})
        self.diagnostics.write_json(diag, "summary.json", payload)

    def _likely_cause(self, runtime_meta: dict[str, object], status: str, error_code: str | None) -> str:
        if status == "success":
            if runtime_meta.get("google_error13_retries"):
                return "google-flake-recovered"
            if runtime_meta.get("history_reopen_used"):
                return "late-book-reopened-from-history"
            if runtime_meta.get("generation_settled_without_share_text"):
                return "quiet-finish-share-surface-recovered"
            return "direct-success"
        if error_code == "GOOGLE_RUNTIME_ERROR_13":
            return "google-runtime-error-13"
        if error_code == "SHARE_LINK_NOT_FOUND":
            return "share-ui-not-exposed"
        if error_code == "GENERATION_TIMEOUT":
            return "generation-timeout"
        return "unknown"

    def _suggested_next_step(self, runtime_meta: dict[str, object], status: str, error_code: str | None) -> str:
        if status == "success":
            return "repeat-smoke-to-measure-stability"
        if error_code == "GOOGLE_RUNTIME_ERROR_13":
            return "rerun-smoke-and-check-history-reopen"
        if error_code == "SHARE_LINK_NOT_FOUND":
            return "inspect-share-attempt-screenshot-and-page-html"
        if error_code == "GENERATION_TIMEOUT":
            return "reopen-storybook-history-and-verify-late-completion"
        return "inspect-summary-and-debug-artifacts"

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _meaningful_tokens(self, text: str) -> list[str]:
        tokens = re.findall(r"[\w\u0400-\u04FF]+", text.lower())
        return [tok for tok in tokens if len(tok) > 2]
