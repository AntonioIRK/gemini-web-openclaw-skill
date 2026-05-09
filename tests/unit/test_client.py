import pytest
from unittest.mock import MagicMock, patch

from openclaw_gemini_web.client import GeminiWebClient, GeminiStorybookClient
from openclaw_gemini_web.config import GeminiWebConfig
from openclaw_gemini_web.models import GeminiWebCreateRequest, GeminiImageRequest


@pytest.fixture
def mock_config():
    config = MagicMock(spec=GeminiWebConfig)
    config.diagnostics_root = "/tmp/test_diag"
    config.diagnostics_retention_days = 10
    return config


@patch("openclaw_gemini_web.client.ChatImageRunner")
@patch("openclaw_gemini_web.client.StorybookRunner")
@patch("openclaw_gemini_web.client.DiagnosticsManager")
def test_client_init_with_config(
    mock_diagnostics, mock_storybook, mock_chat_image, mock_config
):
    client = GeminiWebClient(config=mock_config)

    assert client.config == mock_config
    mock_diagnostics.assert_called_once_with("/tmp/test_diag", 10)
    mock_storybook.assert_called_once_with(mock_config, mock_diagnostics.return_value)
    mock_chat_image.assert_called_once_with(mock_config, mock_diagnostics.return_value)


@patch("openclaw_gemini_web.client.GeminiWebConfig.from_env")
@patch("openclaw_gemini_web.client.ChatImageRunner")
@patch("openclaw_gemini_web.client.StorybookRunner")
@patch("openclaw_gemini_web.client.DiagnosticsManager")
def test_client_init_without_config(
    mock_diagnostics, mock_storybook, mock_chat_image, mock_from_env
):
    mock_config = MagicMock(spec=GeminiWebConfig)
    mock_config.diagnostics_root = "/tmp/env_diag"
    mock_config.diagnostics_retention_days = 5
    mock_from_env.return_value = mock_config

    client = GeminiWebClient()

    assert client.config == mock_config
    mock_from_env.assert_called_once()
    mock_diagnostics.assert_called_once_with("/tmp/env_diag", 5)
    mock_storybook.assert_called_once_with(mock_config, mock_diagnostics.return_value)
    mock_chat_image.assert_called_once_with(mock_config, mock_diagnostics.return_value)


@pytest.fixture
def mock_client(mock_config):
    with (
        patch("openclaw_gemini_web.client.ChatImageRunner"),
        patch("openclaw_gemini_web.client.StorybookRunner"),
        patch("openclaw_gemini_web.client.DiagnosticsManager"),
    ):
        client = GeminiWebClient(config=mock_config)
        yield client


def test_login(mock_client):
    mock_client.login()
    mock_client.storybook_runner.login.assert_called_once()


def test_doctor(mock_client):
    mock_client.doctor()
    mock_client.storybook_runner.doctor.assert_called_once()


def test_debug_open(mock_client):
    mock_client.debug_open()
    mock_client.storybook_runner.debug_open.assert_called_once()


def test_create(mock_client):
    request = GeminiWebCreateRequest(prompt="test prompt")
    mock_client.create(request)
    mock_client.storybook_runner.create.assert_called_once_with(request)


def test_inspect_home(mock_client):
    mock_client.inspect_home()
    mock_client.storybook_runner.inspect_home.assert_called_once()


def test_create_image(mock_client):
    request = GeminiImageRequest(prompt="test prompt")
    mock_client.create_image(request)
    mock_client.chat_image_runner.create_image.assert_called_once_with(request)


def test_ask_chat(mock_client):
    mock_client.ask_chat(prompt="hello", timeout_seconds=60, new_thread=True)
    mock_client.chat_image_runner.ask_chat.assert_called_once_with(
        prompt="hello", timeout_seconds=60, new_thread=True
    )


def test_client_aliases():
    assert GeminiStorybookClient is GeminiWebClient
