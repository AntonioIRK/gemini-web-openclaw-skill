from unittest.mock import patch, MagicMock

import pytest

from openclaw_gemini_web.models import GeminiImageRequest, GeminiWebCreateRequest
from openclaw_gemini_web.skill.openclaw_adapter import run_openclaw_skill


@pytest.fixture
def mock_client_class():
    with patch("openclaw_gemini_web.client.GeminiWebClient") as MockClient:
        yield MockClient


def test_run_openclaw_skill_chat_ask(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.ask_chat.return_value.to_dict.return_value = {"status": "success", "response": "chat response"}

    payload = {
        "mode": "chat-ask",
        "prompt": "hello",
        "timeout_seconds": "60",
        "new_thread": True
    }

    result = run_openclaw_skill(payload)

    assert result == {"status": "success", "response": "chat response"}
    mock_instance.ask_chat.assert_called_once_with(
        prompt="hello",
        timeout_seconds=60,
        new_thread=True
    )


def test_run_openclaw_skill_image_create(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create_image.return_value.to_dict.return_value = {"status": "success", "url": "http://image"}

    payload = {
        "mode": "image-create",
        "prompt": "draw a cat",
        "timeout_seconds": 150,
    }

    result = run_openclaw_skill(payload)

    assert result == {"status": "success", "url": "http://image"}

    mock_instance.create_image.assert_called_once()
    request = mock_instance.create_image.call_args[0][0]
    assert isinstance(request, GeminiImageRequest)
    assert request.prompt == "draw a cat"
    assert request.mode == "image-create"
    assert request.timeout_seconds == 150
    assert request.new_thread is False
    assert request.files == []


def test_run_openclaw_skill_image_edit(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create_image.return_value.to_dict.return_value = {"status": "success", "url": "http://image"}

    payload = {
        "mode": "image-edit",
        "prompt": "make it blue",
        "files": ["/path/to/img"],
        "new_thread": "True" # truthy string evaluates to True via bool(), although standard is True
    }

    result = run_openclaw_skill(payload)

    assert result == {"status": "success", "url": "http://image"}

    mock_instance.create_image.assert_called_once()
    request = mock_instance.create_image.call_args[0][0]
    assert isinstance(request, GeminiImageRequest)
    assert request.prompt == "make it blue"
    assert request.mode == "image-edit"
    assert request.files == ["/path/to/img"]


def test_run_openclaw_skill_default_create(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create.return_value.to_dict.return_value = {"status": "success", "link": "http://share"}

    payload = {
        "mode": "create",
        "prompt": "write a story",
        "return_mode": "download",
        "output_path": "/tmp/out.md",
        "debug": True
    }

    result = run_openclaw_skill(payload)

    assert result == {"status": "success", "link": "http://share"}

    mock_instance.create.assert_called_once()
    request = mock_instance.create.call_args[0][0]
    assert isinstance(request, GeminiWebCreateRequest)
    assert request.prompt == "write a story"
    assert request.return_mode == "download"
    assert request.output_path == "/tmp/out.md"
    assert request.timeout_seconds == 300
    assert request.debug is True
    assert request.files == []
