import pytest
from unittest.mock import MagicMock
from playwright.sync_api import Page

from openclaw_gemini_web.auth.login_flow import is_logged_in, require_login
from openclaw_gemini_web.exceptions import LoginRequiredError


def test_is_logged_in_accounts_google():
    page = MagicMock(spec=Page)
    page.url = "https://accounts.google.com/login"
    assert is_logged_in(page) is False


def test_is_logged_in_consent_google():
    page = MagicMock(spec=Page)
    page.url = "https://consent.google.com/something"
    assert is_logged_in(page) is False


def test_is_logged_in_app_url():
    page = MagicMock(spec=Page)
    page.url = "https://gemini.google.com/app"
    assert is_logged_in(page) is True


def test_is_logged_in_storybook_url():
    page = MagicMock(spec=Page)
    page.url = "https://gemini.google.com/gem/storybook"
    assert is_logged_in(page) is True


def test_is_logged_in_sign_in_text():
    page = MagicMock(spec=Page)
    page.url = "https://gemini.google.com/some_other_page"
    mock_locator = MagicMock()
    mock_locator.count.return_value = 1
    page.get_by_text.return_value = mock_locator
    assert is_logged_in(page) is False
    page.get_by_text.assert_called_once_with("Sign in", exact=False)


def test_is_logged_in_true_default():
    page = MagicMock(spec=Page)
    page.url = "https://gemini.google.com/some_other_page"
    mock_locator = MagicMock()
    mock_locator.count.return_value = 0
    page.get_by_text.return_value = mock_locator
    assert is_logged_in(page) is True


def test_require_login_raises():
    page = MagicMock(spec=Page)
    page.url = "https://accounts.google.com/login"
    with pytest.raises(LoginRequiredError) as exc_info:
        require_login(page)
    assert "Gemini session is not authenticated." in str(exc_info.value)


def test_require_login_passes():
    page = MagicMock(spec=Page)
    page.url = "https://gemini.google.com/app"
    # Should not raise
    require_login(page)
