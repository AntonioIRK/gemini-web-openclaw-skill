from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import shutil
import time
import urllib.request

from playwright.sync_api import sync_playwright

from ..config import GeminiWebConfig
from ..auth.profile import ensure_profile_dir


def _fetch_cdp_ws_url(port: int, address: str = "127.0.0.1") -> str:
    with urllib.request.urlopen(f"http://{address}:{port}/json/version", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    ws_url = payload.get("webSocketDebuggerUrl")
    if not ws_url:
        raise RuntimeError(f"CDP endpoint on {address}:{port} did not return webSocketDebuggerUrl")
    return ws_url


def _prepare_browser_env() -> dict[str, str]:
    env = dict(os.environ)
    xdg_data_home = Path(env.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    (xdg_data_home / "icons" / "hicolor").mkdir(parents=True, exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg_data_home)
    return env


def _resolve_browser_executable() -> str | None:
    explicit = os.environ.get("GEMINI_WEB_BROWSER_PATH", os.environ.get("GEMINI_STORYBOOK_BROWSER_PATH", "")).strip()
    if explicit:
        return explicit
    for candidate in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


@contextmanager
def _profile_lock(profile_dir: Path):
    lock_path = profile_dir / ".openclaw-browser.lock"
    timeout_seconds = float(os.environ.get("GEMINI_WEB_PROFILE_LOCK_TIMEOUT", os.environ.get("GEMINI_STORYBOOK_PROFILE_LOCK_TIMEOUT", "300")))
    deadline = time.time() + timeout_seconds
    sleep_time = 0.01
    with lock_path.open("w") as fh:
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError as err:
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out waiting for Gemini profile lock: {lock_path}") from err
                time.sleep(sleep_time)
                sleep_time = min(0.5, sleep_time * 1.5)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextmanager
def open_persistent_page(config: GeminiWebConfig):
    profile_dir = ensure_profile_dir(config.profile_dir)
    launch_env = _prepare_browser_env()
    executable_path = _resolve_browser_executable()
    with _profile_lock(profile_dir):
        with sync_playwright() as p:
            if config.remote_debugging_port and config.allow_cdp_attach:
                browser = p.chromium.connect_over_cdp(_fetch_cdp_ws_url(config.remote_debugging_port, config.remote_debugging_address))
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                try:
                    yield context, page
                finally:
                    browser.close()
                return

            launch_args = ["--disable-gpu", "--disable-software-rasterizer", "--disable-dev-shm-usage"]
            if config.remote_debugging_port and not config.allow_cdp_attach:
                launch_args.extend([
                    f"--remote-debugging-port={config.remote_debugging_port}",
                    f"--remote-debugging-address={config.remote_debugging_address}",
                ])

            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=config.headless,
                slow_mo=config.slow_mo_ms,
                accept_downloads=True,
                executable_path=executable_path,
                env=launch_env,
                args=launch_args,
            )
            page = context.pages[0] if context.pages else context.new_page()
            try:
                yield context, page
            finally:
                context.close()
