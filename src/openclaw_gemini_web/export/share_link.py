from __future__ import annotations

import re
from playwright.sync_api import Page
from urllib.parse import urlparse

from ..exceptions import ShareLinkNotFoundError
from ..web.selectors import SelectorBundle


def _read_clipboard(page: Page) -> str | None:
    try:
        value = page.evaluate("""
            async () => {
                try {
                    return await Promise.race([
                        navigator.clipboard.readText(),
                        new Promise((resolve) => setTimeout(() => resolve(null), 800))
                    ]);
                } catch (e) {
                    return null;
                }
            }
        """)
    except Exception:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def extract_share_link(page: Page, selectors: SelectorBundle) -> str:
    _open_share_surfaces(page, selectors)

    direct = _find_share_link_in_dom(page)
    if direct:
        return direct

    for text in selectors.share_texts:
        button = page.get_by_role("button", name=text, exact=False)
        if button.count() > 0:
            button.first.click(force=True, timeout=2000)
            page.wait_for_timeout(1800)
            link = _read_clipboard(page)
            if _is_share_link(link):
                return link
            link = _find_share_link_in_dom(page)
            if link:
                return link

        locator = page.get_by_text(text, exact=False)
        if locator.count() > 0:
            href = locator.first.get_attribute("href")
            if _is_share_link(href):
                return href
            link = _find_share_link_in_dom(page)
            if link:
                return link

    for candidate in page.locator("a[href]").all()[:40]:
        try:
            href = candidate.get_attribute("href")
        except Exception:
            href = None
        if _is_share_link(href):
            return href

    raise ShareLinkNotFoundError(
        "Share link was not found in the current Storybook UI."
    )


def _open_share_surfaces(page: Page, selectors: SelectorBundle) -> None:
    for text in selectors.share_texts:
        try:
            button = page.get_by_role("button", name=text, exact=False)
            if button.count() > 0:
                button.first.click(force=True, timeout=2000)
                page.wait_for_timeout(1200)
        except Exception:
            continue

    for text in selectors.share_action_texts:
        try:
            button = page.get_by_role("button", name=text, exact=False)
            if button.count() > 0:
                button.first.click(force=True, timeout=2000)
                page.wait_for_timeout(1200)
                link = _read_clipboard(page)
                if _is_share_link(link):
                    return
        except Exception:
            continue
        try:
            menuitem = page.get_by_role("menuitem", name=text, exact=False)
            if menuitem.count() > 0:
                menuitem.first.click(force=True, timeout=2000)
                page.wait_for_timeout(1200)
                link = _read_clipboard(page)
                if _is_share_link(link):
                    return
        except Exception:
            continue


def _find_share_link_in_dom(page: Page) -> str | None:
    candidates = []

    clipboard = _read_clipboard(page)
    if clipboard:
        candidates.append(clipboard)

    try:
        dom_candidates = page.evaluate(
            """
            () => {
                const values = [];
                const push = (value) => {
                    if (typeof value !== 'string') return;
                    const trimmed = value.trim();
                    if (!trimmed) return;
                    values.push(trimmed);
                };

                for (const el of document.querySelectorAll('a[href], input, textarea, [data-url], [data-link], [data-href], [data-clipboard-text]')) {
                    push(el.getAttribute('href'));
                    push(el.getAttribute('value'));
                    push(el.value);
                    push(el.textContent);
                    push(el.getAttribute('data-url'));
                    push(el.getAttribute('data-link'));
                    push(el.getAttribute('data-href'));
                    push(el.getAttribute('data-clipboard-text'));
                }

                push(window.location.href);
                return values.slice(0, 400);
            }
            """
        )
        if isinstance(dom_candidates, list):
            candidates.extend(v for v in dom_candidates if isinstance(v, str))
    except Exception:
        pass

    try:
        html = page.content()
    except Exception:
        html = ""
    if html:
        candidates.extend(re.findall(r"https://[^\s\"'<>]+", html))

    for value in candidates:
        if _is_share_link(value):
            return value
    return None


def _is_share_link(value: str | None) -> bool:
    if not value or not value.startswith("http"):
        return False
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    if "accounts.google.com" in host:
        return False
    if "gemini.google.com" in host and "/share/" in path:
        return True
    if host == "g.co" and "gemini" in path.lower():
        return True
    return False
