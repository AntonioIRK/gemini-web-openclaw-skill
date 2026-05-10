from unittest.mock import patch

from openclaw_gemini_web.models import GeminiImageRequest, GeminiWebCreateRequest
from openclaw_gemini_web.skill.openclaw_adapter import run_openclaw_skill


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_run_openclaw_skill_chat_ask(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.ask_chat.return_value.to_dict.return_value = {"status": "success", "response": "chat response"}

    result = run_openclaw_skill(
        {
            "mode": "chat-ask",
            "prompt": "hello",
            "timeout_seconds": "60",
            "new_thread": True,
        }
    )

    assert result == {"status": "success", "response": "chat response"}
    mock_instance.ask_chat.assert_called_once_with(prompt="hello", timeout_seconds=60, new_thread=True)


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_run_openclaw_skill_image_create(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create_image.return_value.to_dict.return_value = {"status": "success", "url": "http://image"}

    result = run_openclaw_skill({"mode": "image-create", "prompt": "draw a cat", "timeout_seconds": 150})

    assert result == {"status": "success", "url": "http://image"}
    request = mock_instance.create_image.call_args.args[0]
    assert isinstance(request, GeminiImageRequest)
    assert request.prompt == "draw a cat"
    assert request.mode == "image-create"
    assert request.timeout_seconds == 150
    assert request.new_thread is False
    assert request.files == []


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_run_openclaw_skill_image_edit(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create_image.return_value.to_dict.return_value = {"status": "success", "url": "http://image"}

    result = run_openclaw_skill(
        {
            "mode": "image-edit",
            "prompt": "make it blue",
            "files": ["/path/to/img"],
            "new_thread": True,
        }
    )

    assert result == {"status": "success", "url": "http://image"}
    request = mock_instance.create_image.call_args.args[0]
    assert isinstance(request, GeminiImageRequest)
    assert request.prompt == "make it blue"
    assert request.mode == "image-edit"
    assert request.files == ["/path/to/img"]
    assert request.new_thread is True


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_run_openclaw_skill_default_create(mock_client_class):
    mock_instance = mock_client_class.return_value
    mock_instance.create.return_value.to_dict.return_value = {"status": "success", "link": "http://share"}

    result = run_openclaw_skill(
        {
            "mode": "create",
            "prompt": "write a story",
            "return_mode": "pdf",
            "output_path": "/tmp/out.pdf",
            "debug": True,
        }
    )

    assert result == {"status": "success", "link": "http://share"}
    request = mock_instance.create.call_args.args[0]
    assert isinstance(request, GeminiWebCreateRequest)
    assert request.prompt == "write a story"
    assert request.return_mode == "pdf"
    assert request.output_path == "/tmp/out.pdf"
    assert request.timeout_seconds == 300
    assert request.debug is True
    assert request.files == []
