from __future__ import annotations

from playwright.sync_api import Page

from ..exceptions import LoginRequiredError


def is_logged_in(page: Page) -> bool:
    url = page.url.lower()
    if "accounts.google.com" in url or "consent.google.com" in url:
        return False
    if "/app" in url or "/gem/storybook" in url:
        return True
    login_text = page.get_by_text("Sign in", exact=False)
    if login_text.count() > 0:
        return False
    return True


def require_login(page: Page) -> None:
    if not is_logged_in(page):
        raise LoginRequiredError(
            "Gemini session is not authenticated. Run the login command first, sign into Google in the opened browser window, and wait until Gemini home finishes loading."
        )
