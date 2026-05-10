from unittest.mock import MagicMock, patch
import pytest

from openclaw_gemini_web.client import GeminiWebClient, GeminiStorybookClient
from openclaw_gemini_web.config import GeminiWebConfig
from openclaw_gemini_web.models import GeminiImageRequest, GeminiWebCreateRequest

@pytest.fixture
def mock_config():
    return MagicMock(spec=GeminiWebConfig)

@patch("openclaw_gemini_web.client.GeminiWebConfig.from_env")
@patch("openclaw_gemini_web.client.DiagnosticsManager")
@patch("openclaw_gemini_web.client.StorybookRunner")
@patch("openclaw_gemini_web.client.ChatImageRunner")
def test_client_init_default(mock_chat_image_runner, mock_storybook_runner, mock_diagnostics_manager, mock_from_env):
    mock_from_env.return_value = MagicMock(spec=GeminiWebConfig)
    client = GeminiWebClient()
    mock_from_env.assert_called_once()
    mock_diagnostics_manager.assert_called_once()
    mock_storybook_runner.assert_called_once()
    mock_chat_image_runner.assert_called_once()
    assert client.config == mock_from_env.return_value

@patch("openclaw_gemini_web.client.DiagnosticsManager")
@patch("openclaw_gemini_web.client.StorybookRunner")
@patch("openclaw_gemini_web.client.ChatImageRunner")
def test_client_init_with_config(mock_chat_image_runner, mock_storybook_runner, mock_diagnostics_manager, mock_config):
    client = GeminiWebClient(config=mock_config)
    mock_diagnostics_manager.assert_called_once()
    mock_storybook_runner.assert_called_once()
    mock_chat_image_runner.assert_called_once()
    assert client.config == mock_config

@pytest.fixture
def mock_client(mock_config):
    with patch("openclaw_gemini_web.client.DiagnosticsManager"), \
         patch("openclaw_gemini_web.client.StorybookRunner") as MockStorybookRunner, \
         patch("openclaw_gemini_web.client.ChatImageRunner") as MockChatImageRunner:
        client = GeminiWebClient(config=mock_config)
        client.storybook_runner = MockStorybookRunner.return_value
        client.chat_image_runner = MockChatImageRunner.return_value
        yield client

def test_login(mock_client):
    mock_client.login()
    mock_client.storybook_runner.login.assert_called_once()

def test_doctor(mock_client):
    mock_result = {"status": "ok"}
    mock_client.storybook_runner.doctor.return_value = mock_result
    result = mock_client.doctor()
    mock_client.storybook_runner.doctor.assert_called_once()
    assert result == mock_result

def test_debug_open(mock_client):
    mock_client.debug_open()
    mock_client.storybook_runner.debug_open.assert_called_once()

def test_create(mock_client):
    request = MagicMock(spec=GeminiWebCreateRequest)
    mock_result = MagicMock()
    mock_client.storybook_runner.create.return_value = mock_result

    result = mock_client.create(request)
    mock_client.storybook_runner.create.assert_called_once_with(request)
    assert result == mock_result

def test_inspect_home(mock_client):
    mock_result = {"user": "test"}
    mock_client.storybook_runner.inspect_home.return_value = mock_result

    result = mock_client.inspect_home()
    mock_client.storybook_runner.inspect_home.assert_called_once()
    assert result == mock_result

def test_create_image(mock_client):
    request = MagicMock(spec=GeminiImageRequest)
    mock_result = MagicMock()
    mock_client.chat_image_runner.create_image.return_value = mock_result

    result = mock_client.create_image(request)
    mock_client.chat_image_runner.create_image.assert_called_once_with(request)
    assert result == mock_result

def test_ask_chat(mock_client):
    prompt = "Hello"
    timeout_seconds = 60
    new_thread = True
    mock_result = MagicMock()
    mock_client.chat_image_runner.ask_chat.return_value = mock_result

    result = mock_client.ask_chat(prompt=prompt, timeout_seconds=timeout_seconds, new_thread=new_thread)
    mock_client.chat_image_runner.ask_chat.assert_called_once_with(
        prompt=prompt, timeout_seconds=timeout_seconds, new_thread=new_thread
    )
    assert result == mock_result

def test_ask_chat_defaults(mock_client):
    prompt = "Hello"
    mock_result = MagicMock()
    mock_client.chat_image_runner.ask_chat.return_value = mock_result

    result = mock_client.ask_chat(prompt=prompt)
    mock_client.chat_image_runner.ask_chat.assert_called_once_with(
        prompt=prompt, timeout_seconds=120, new_thread=False
    )
    assert result == mock_result

def test_gemini_storybook_client_alias():
    assert GeminiStorybookClient is GeminiWebClient
