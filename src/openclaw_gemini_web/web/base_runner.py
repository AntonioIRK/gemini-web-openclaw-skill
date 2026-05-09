from __future__ import annotations

from pathlib import Path
import base64
import html
import mimetypes
import re
import time

from ..auth.login_flow import is_logged_in, require_login
from ..config import GeminiWebConfig
from ..diagnostics import DiagnosticsManager
from ..exceptions import GenerationTimeoutError, GeminiWebError, GoogleRuntimeError, GoogleRuntimeError13, PromptSubmissionError
from ..state import GeminiWebState
from ..web.browser import open_persistent_page
from ..web.selectors import SelectorBundle
from ..web.state_machine import GeminiWebStateMachine
from ..models import WorkflowState


class GeminiWebRunnerBase:
    def __init__(self, config: GeminiWebConfig, diagnostics: DiagnosticsManager):
        self.config = config
        self.diagnostics = diagnostics
        self.selectors = SelectorBundle()
        self.state = GeminiWebState(config.state_path)

    def login(self) -> None:
        with open_persistent_page(self.config) as (_context, page):
            page.goto(self.config.base_url, wait_until="domcontentloaded")
            if is_logged_in(page):
                print("Gemini is already authenticated in the persistent profile.")
                return

            timeout_seconds = max(self.config.timeout_seconds, 600)
            deadline = time.time() + timeout_seconds
            print("Sign into Google in the opened browser window. This command will finish automatically when Gemini is authenticated.")
            print("If Google asks for 2FA or confirmation on another device, complete it there and come back here.")

            last_url = None
            while time.time() < deadline:
                try:
                    current_url = page.url
                except Exception:
                    current_url = None
                if current_url and current_url != last_url:
                    print(f"Waiting for Gemini login, current page: {current_url}")
                    last_url = current_url
                if is_logged_in(page):
                    print(f"Gemini login completed. Persistent profile saved at: {self.config.profile_dir}")
                    return
                try:
                    page.wait_for_timeout(1500)
                except Exception:
                    break

            raise TimeoutError(
                f"Timed out waiting for Gemini login after {timeout_seconds} seconds. Re-run login and complete the Google sign-in flow in the opened browser."
            )

    def doctor(self) -> dict:
        diag = self.diagnostics.create()
        machine = GeminiWebStateMachine()
        with open_persistent_page(self.config) as (_context, page):
            machine.advance(WorkflowState.OPENING_GEMINI)
            self.diagnostics.write_state(diag, machine.current)
            page.goto(self.config.base_url, wait_until="domcontentloaded")
            logged_in = "accounts.google.com" not in page.url.lower()
            self.diagnostics.write_html(diag, page.content())
            return {
                "base_url": self.config.base_url,
                "profile_dir": str(self.config.profile_dir),
                "logged_in_guess": logged_in,
                "page_url": page.url,
                "diagnostics": str(diag.run_dir),
            }

    def debug_open(self) -> None:
        with open_persistent_page(self.config) as (_context, page):
            page.goto(self.config.base_url, wait_until="domcontentloaded")
            print(f"Opened Gemini in persistent profile: {self.config.profile_dir}")
            page.wait_for_timeout(120000)

    def inspect_home(self) -> dict:
        diag = self.diagnostics.create()
        with open_persistent_page(self.config) as (_context, page):
            page.goto(self.config.base_url, wait_until="domcontentloaded")
            require_login(page)
            page.wait_for_timeout(3000)
            self._capture_page(diag, page, "gemini-home")
            body = self._read_body_text(page)
            suggestions = [
                text
                for text in ["Создать изображение", "Create image", "Создать музыку", "Storybook", "Gem-боты", "Мой контент"]
                if text in body
            ]
            return {
                "base_url": self.config.base_url,
                "page_url": page.url,
                "title": page.title(),
                "suggestions_detected": suggestions,
                "body_excerpt": body[:2000],
                "diagnostics": str(diag.run_dir),
            }

    def _submit_prompt(self, page, prompt: str) -> None:
        # Storybook often renders starter chips first, and only reveals the
        # actual prompt field after one of them is selected. Try that path
        # before searching for the textbox itself.
        try:
            if "/gem/storybook" in (getattr(page, "url", "") or ""):
                for text in self.selectors.storybook_entry_texts:
                    starter = page.get_by_role("button", name=re.compile(re.escape(text), re.I))
                    if starter.count() > 0:
                        try:
                            starter.first.click(force=True)
                            page.wait_for_timeout(1200)
                            break
                        except Exception:
                            continue
        except Exception:
            pass

        candidates = []
        for label in self.selectors.prompt_input_labels:
            candidates.append(page.get_by_label(label, exact=False))
        for selector in self.selectors.prompt_input_selectors:
            candidates.append(page.locator(selector))
        candidates.append(page.get_by_role("textbox"))

        last_error = None
        for locator in candidates:
            try:
                if locator.count() == 0:
                    continue
                target = locator.first
                target.click(force=True)
                page.wait_for_timeout(300)
                tag_name = (target.evaluate("el => el.tagName") or "").lower()
                if tag_name == "textarea":
                    target.fill(prompt)
                else:
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.wait_for_timeout(100)
                    page.keyboard.insert_text(prompt)
                page.wait_for_timeout(500)
                self._send_prompt(page)
                page.wait_for_timeout(800)
                body_text = self._read_body_text(page)
                if self._looks_unsent(page, body_text):
                    page.keyboard.press("Enter")
                return
            except Exception:
                last_error = True
                continue

        # One more pass after a short wait, because the Storybook prompt field
        # can appear a moment after the starter chip is clicked.
        page.wait_for_timeout(1500)
        for locator in candidates:
            try:
                if locator.count() == 0:
                    continue
                target = locator.first
                target.click(force=True)
                page.wait_for_timeout(300)
                tag_name = (target.evaluate("el => el.tagName") or "").lower()
                if tag_name == "textarea":
                    target.fill(prompt)
                else:
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.wait_for_timeout(100)
                    page.keyboard.insert_text(prompt)
                page.wait_for_timeout(500)
                self._send_prompt(page)
                page.wait_for_timeout(800)
                body_text = self._read_body_text(page)
                if self._looks_unsent(page, body_text):
                    page.keyboard.press("Enter")
                return
            except Exception:
                last_error = True
                continue

        raise PromptSubmissionError("Prompt input was not found in Gemini UI")

    def _wait_for_generation(self, page, timeout_seconds: int) -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            body_text = self._read_body_text(page)
            try:
                stop_visible = page.get_by_role("button", name=re.compile("Остановить|Stop", re.I)).count() > 0
            except Exception:
                stop_visible = False
            generating = any(text in body_text for text in self.selectors.generating_texts) or stop_visible
            if any(text in body_text for text in self.selectors.share_texts):
                return
            if generating:
                page.wait_for_timeout(2000)
                continue
            page.wait_for_timeout(2000)
        raise GenerationTimeoutError(f"Storybook generation did not finish within {timeout_seconds} seconds")

    def _wait_for_generated_images(self, page, timeout_seconds: int, existing_images: set[str] | None = None) -> list[dict]:
        deadline = time.time() + timeout_seconds
        existing_images = existing_images or set()
        while time.time() < deadline:
            body_text = self._read_body_text(page)
            google_error = self._detect_google_error(body_text)
            if google_error:
                raise google_error
            images = self._collect_candidate_images(page, latest_response_only=True)
            new_images = [img for img in images if self._image_identity(img) not in existing_images]
            if new_images:
                return new_images
            page.wait_for_timeout(4000)
        raise GenerationTimeoutError(f"Gemini image generation did not finish within {timeout_seconds} seconds")

    def _wait_for_text_response(self, page, timeout_seconds: int) -> str:
        deadline = time.time() + timeout_seconds
        saw_generating = False
        while time.time() < deadline:
            body_text = self._read_body_text(page)
            google_error = self._detect_google_error(body_text)
            if google_error:
                raise google_error
            if any(text in body_text for text in self.selectors.generating_texts):
                saw_generating = True
                page.wait_for_timeout(2500)
                continue
            answer = self._extract_answer_text(body_text)
            if answer and (saw_generating or "Ответ Gemini" in body_text or "Gemini response" in body_text):
                return answer
            page.wait_for_timeout(2500)
        raise GenerationTimeoutError(f"Gemini chat response did not finish within {timeout_seconds} seconds")

    def _try_click_create_image(self, page) -> None:
        for text in ("Создать изображение", "Create image"):
            locator = page.get_by_text(text, exact=False)
            if locator.count() > 0:
                try:
                    locator.first.click(force=True)
                    page.wait_for_timeout(1500)
                    return
                except Exception:
                    continue

    def _collect_candidate_images(self, page, latest_response_only: bool = False) -> list[dict]:
        try:
            if latest_response_only:
                images = page.evaluate(
                    """
                    () => {
                      const responses = Array.from(document.querySelectorAll('model-response'));
                      const root = responses.at(-1);
                      if (!root) return [];
                      return Array.from(root.querySelectorAll('single-image img.image, generated-image img.image, img')).map((e, i) => ({
                        index: i,
                        latest_response_only: true,
                        src: e.src || '',
                        alt: e.alt || '',
                        w: e.naturalWidth || 0,
                        h: e.naturalHeight || 0,
                      }));
                    }
                    """
                )
            else:
                images = page.locator("img").evaluate_all(
                    "els => els.map((e, i) => ({index: i, src: e.src || '', alt: e.alt || '', w: e.naturalWidth || 0, h: e.naturalHeight || 0}))"
                )
        except Exception:
            return []
        candidates = []
        for image in images:
            if image.get("w", 0) < 256 or image.get("h", 0) < 256:
                continue
            src = image.get("src", "")
            if not src:
                continue
            if src.startswith("blob:") or src.startswith("data:") or "googleusercontent.com" in src or "gstatic.com" in src:
                candidates.append(image)
        return candidates

    def _image_identity(self, image: dict) -> str:
        src = image.get("src", "")
        index = image.get("index", "")
        return f"{index}:{src}"

    def _extract_answer_text(self, body_text: str) -> str | None:
        if not body_text:
            return None
        markers = ["Ответ Gemini", "Gemini response"]
        for marker in markers:
            if marker not in body_text:
                continue
            tail = body_text.rsplit(marker, 1)[1]
            stop_markers = [
                "Gemini – это ИИ.",
                "Gemini\xa0– это ИИ.",
                "Gemini and your privacy",
                "Откроется в новом окне",
                "Open in a new window",
                "Инструменты",
                "Быстрая",
                "Pro",
                "Добавить файлы",
                "Отправить",
            ]
            end = len(tail)
            for stop in stop_markers:
                pos = tail.find(stop)
                if pos != -1 and pos < end:
                    end = pos
            answer = tail[:end].strip()
            answer = re.sub(r"\n{3,}", "\n\n", answer)
            answer = re.sub(r"(?:\n|\s)*(Инструменты|Быстрая|Pro)\s*$", "", answer).strip()
            if answer:
                return answer
        return None

    def _save_images(self, page, images: list[dict], output_dir: Path, prefer_screenshot: bool = False) -> list[str]:
        saved: list[str] = []
        for idx, image in enumerate(images, start=1):
            if prefer_screenshot:
                screenshot_path = self._screenshot_image_element(page, image, output_dir, idx)
                if screenshot_path:
                    saved.append(screenshot_path)
                    continue
            blob = self._fetch_image_bytes(page, image.get("src", ""))
            if not blob:
                screenshot_path = self._screenshot_image_element(page, image, output_dir, idx)
                if screenshot_path:
                    saved.append(screenshot_path)
                continue
            mime = blob.get("mime") or "image/png"
            ext = mimetypes.guess_extension(mime) or ".png"
            path = output_dir / f"generated-image-{idx}{ext}"
            path.write_bytes(base64.b64decode(blob["base64"]))
            saved.append(str(path))
        return saved

    def _download_generated_images(self, page, output_dir: Path) -> list[str]:
        saved: list[str] = []
        try:
            buttons = page.locator("model-response").last.get_by_role("button", name=re.compile("Скачать изображение|Скачать в полном размере|Download", re.I))
            count = buttons.count()
        except Exception:
            count = 0
        for idx in range(count):
            try:
                button = buttons.nth(idx)
                with page.expect_download(timeout=120000) as dl:
                    button.click(force=True)
                download = dl.value
                suggested = download.suggested_filename or f"generated-image-{idx + 1}.png"
                ext = Path(suggested).suffix or ".png"
                path = output_dir / f"generated-image-{idx + 1}{ext}"
                download.save_as(str(path))
                saved.append(str(path))
            except Exception:
                continue
        return saved

    def _screenshot_image_element(self, page, image: dict, output_dir: Path, idx: int) -> str | None:
        try:
            if image.get("latest_response_only"):
                locator = page.locator("model-response").last.locator("single-image img.image, generated-image img.image, img").nth(int(image.get("index", idx - 1)))
            else:
                locator = page.locator("img").nth(int(image.get("index", idx - 1)))
            path = output_dir / f"generated-image-{idx}.png"
            locator.screenshot(path=str(path))
            return str(path)
        except Exception:
            return None

    def _fetch_image_bytes(self, page, src: str) -> dict | None:
        if not src:
            return None
        try:
            return page.evaluate(
                """
                async (src) => {
                  try {
                    const res = await fetch(src);
                    const blob = await res.blob();
                    const buf = await blob.arrayBuffer();
                    let binary = '';
                    const bytes = new Uint8Array(buf);
                    const chunk = 0x8000;
                    for (let i = 0; i < bytes.length; i += chunk) {
                      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
                    }
                    return { mime: blob.type || 'image/png', base64: btoa(binary) };
                  } catch (e) {
                    return null;
                  }
                }
                """,
                src,
            )
        except Exception:
            return None

    def _upload_files(self, page, files: list[str]) -> None:
        missing = [f for f in files if not Path(f).exists()]
        if missing:
            raise PromptSubmissionError(f"Input files do not exist: {missing}")
        normalized = [str(Path(f).resolve()) for f in files]

        try:
            file_input = page.locator("input[type=file]")
            if file_input.count() > 0:
                file_input.first.set_input_files(normalized)
                page.wait_for_timeout(1500)
                return
        except Exception:
            pass

        try:
            open_menu = page.get_by_role("button", name=re.compile("Открыть меню загрузки файлов|Open upload file menu", re.I))
            if open_menu.count() > 0:
                for menu_label in [
                    re.compile("Загрузить файлы|Upload files", re.I),
                    re.compile("Фото|Photos", re.I),
                ]:
                    try:
                        open_menu.first.click(force=True)
                        page.wait_for_timeout(500)
                        with page.expect_file_chooser(timeout=15000) as fc:
                            page.get_by_role("menuitem", name=menu_label).first.click(force=True)
                        chooser = fc.value
                        chooser.set_files(normalized)
                        page.wait_for_timeout(1500)
                        return
                    except Exception:
                        continue
        except Exception:
            pass

        for selector in [
            '[data-test-id="hidden-local-image-upload-button"]',
            '[data-test-id="hidden-local-file-upload-button"]',
            '[xapfileselectortrigger]'
        ]:
            try:
                trigger = page.locator(selector)
                if trigger.count() == 0:
                    continue
                with page.expect_file_chooser(timeout=15000) as fc:
                    trigger.first.click(force=True)
                chooser = fc.value
                chooser.set_files(normalized)
                page.wait_for_timeout(1500)
                return
            except Exception:
                continue

        button_patterns = [
            re.compile("Открыть меню загрузки файлов|Open upload file menu", re.I),
            re.compile("Добавить файлы|Add files|Upload|Загрузить", re.I),
            re.compile("Фото|Photos|Images|Изображ", re.I),
        ]
        for pattern in button_patterns:
            try:
                button = page.get_by_role("button", name=pattern)
                if button.count() == 0:
                    continue
                with page.expect_file_chooser(timeout=15000) as fc:
                    button.first.click(force=True)
                chooser = fc.value
                chooser.set_files(normalized)
                page.wait_for_timeout(1500)
                return
            except Exception:
                continue

        raise PromptSubmissionError("Upload control was not found in Gemini UI")

    def _wait_until_image_download_ready(self, page, timeout_seconds: int) -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            body_text = self._read_body_text(page)
            google_error = self._detect_google_error(body_text)
            if google_error:
                raise google_error
            try:
                stop = page.get_by_role("button", name=re.compile("Остановить|Stop", re.I))
                stop_visible = stop.count() > 0
            except Exception:
                stop_visible = False
            try:
                download_buttons = page.locator("model-response").last.get_by_role("button", name=re.compile("Скачать изображение|Скачать в полном размере|Download", re.I))
                ready = download_buttons.count() > 0
            except Exception:
                ready = False
            if ready and not stop_visible:
                page.wait_for_timeout(1000)
                return
            page.wait_for_timeout(2000)
        raise GenerationTimeoutError(f"Gemini image download controls did not become ready within {timeout_seconds} seconds")

    def _chat_missing(self, page) -> bool:
        body = self._read_body_text(page)
        return "Не удалось загрузить этот чат" in body or "This chat couldn't be loaded" in body

    def _send_prompt(self, page) -> None:
        for label in self.selectors.send_button_labels:
            button = page.get_by_role("button", name=label, exact=False)
            if button.count() > 0:
                button.first.click(force=True)
                return
        for selector in self.selectors.send_button_selectors:
            button = page.locator(selector)
            if button.count() > 0:
                button.first.click(force=True)
                return
        page.keyboard.press("Enter")

    def _looks_unsent(self, page, body_text: str) -> bool:
        url = getattr(page, "url", "") or ""
        if any(text in body_text for text in self.selectors.generating_texts):
            return False
        if "Ваш запрос" in body_text or "Gemini response" in body_text or "Ответ Gemini" in body_text:
            return False
        return url.rstrip("/") in {"https://gemini.google.com/app", "https://gemini.google.com"}

    def _read_body_text(self, page) -> str:
        try:
            return page.locator("body").inner_text(timeout=2000)
        except Exception:
            try:
                value = page.evaluate("() => document.body ? document.body.innerText : ''")
                if value:
                    return value
            except Exception:
                pass
        return self._html_text_excerpt(page)

    def _html_text_excerpt(self, page) -> str:
        try:
            raw = page.content()
        except Exception:
            return ""
        raw_unescaped = html.unescape(raw)
        stripped = re.sub(r"<script.*?</script>", " ", raw_unescaped, flags=re.IGNORECASE | re.DOTALL)
        stripped = re.sub(r"<style.*?</style>", " ", stripped, flags=re.IGNORECASE | re.DOTALL)
        stripped = re.sub(r"<[^>]+>", " ", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        return stripped[:12000]

    def _detect_google_error(self, body_text: str) -> GeminiWebError | None:
        if not body_text:
            return None
        for text in self.selectors.error_13_texts:
            if text in body_text:
                return GoogleRuntimeError13(text)
        if re.search(r"(something went wrong|что-то пошло не так).{0,40}\(13\)", body_text, flags=re.IGNORECASE | re.DOTALL):
            return GoogleRuntimeError13("Google Gemini returned Something went wrong (13)")
        for text in self.selectors.generic_error_texts:
            if text in body_text:
                return GoogleRuntimeError(text)
        return None

    def _capture_page(self, diag, page, stem: str) -> None:
        try:
            self.diagnostics.write_html(diag, page.content())
        except Exception:
            pass
        try:
            self.diagnostics.write_screenshot(diag, page, f"{stem}.png")
        except Exception:
            pass

    def _capture_error_context(self, diag, page, machine, exc: Exception) -> None:
        if page is None:
            return
        try:
            self._capture_page(diag, page, f"failed-{machine.current.value.lower()}")
        except Exception:
            pass

    def _error_payload(self, page, machine, code: str, message: str) -> dict:
        payload = {"code": code, "message": message, "state": machine.current.value}
        if page is not None:
            try:
                payload["page_url"] = page.url
            except Exception:
                pass
            try:
                body_text = self._read_body_text(page)
                if body_text:
                    payload["body_text_excerpt"] = body_text[:4000]
                else:
                    html_excerpt = self._html_text_excerpt(page)
                    if html_excerpt:
                        payload["body_text_excerpt"] = html_excerpt[:4000]
            except Exception:
                pass
        return payload
