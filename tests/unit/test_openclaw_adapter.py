from unittest.mock import MagicMock, patch

from openclaw_gemini_web.models import GeminiWebCreateResult, GeminiWebResult
from openclaw_gemini_web.skill.openclaw_adapter import run_openclaw_skill


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_openclaw_adapter_chat_ask(mock_client_class):
    mock_client = MagicMock()
    mock_client.ask_chat.return_value = GeminiWebResult(status="success", text="Hello world")
    mock_client_class.return_value = mock_client

    payload = {"mode": "chat-ask", "prompt": "Say hello", "timeout_seconds": 60, "new_thread": True}

    result = run_openclaw_skill(payload)

    assert result["status"] == "success"
    assert result["text"] == "Hello world"
    mock_client.ask_chat.assert_called_once_with(prompt="Say hello", timeout_seconds=60, new_thread=True)


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_openclaw_adapter_chat_ask_stream(mock_client_class):
    mock_client = MagicMock()

    def mock_stream(*args, **kwargs):
        yield "Hello "
        yield "world!"

    mock_client.ask_chat_stream.side_effect = mock_stream
    mock_client_class.return_value = mock_client

    payload = {"mode": "chat-ask-stream", "prompt": "Say hello", "timeout_seconds": 60, "new_thread": True}

    result_gen = run_openclaw_skill(payload)
    result_list = list(result_gen)

    assert result_list == ["Hello ", "world!"]
    mock_client.ask_chat_stream.assert_called_once_with(prompt="Say hello", timeout_seconds=60, new_thread=True)


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_openclaw_adapter_image_create(mock_client_class):
    mock_client = MagicMock()
    mock_client.create_image.return_value = GeminiWebResult(status="success", image_paths=["/tmp/img1.png"])
    mock_client_class.return_value = mock_client

    payload = {"mode": "image-create", "prompt": "Draw a cat", "files": ["/tmp/ref.png"]}

    result = run_openclaw_skill(payload)

    assert result["status"] == "success"
    assert result["image_paths"] == ["/tmp/img1.png"]

    # Verify request creation
    args, kwargs = mock_client.create_image.call_args
    request_obj = args[0]
    assert request_obj.prompt == "Draw a cat"
    assert request_obj.mode == "image-create"
    assert request_obj.files == ["/tmp/ref.png"]


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_openclaw_adapter_document_analysis(mock_client_class):
    mock_client = MagicMock()
    mock_client.create_image.return_value = GeminiWebResult(status="success", text="Document summary")
    mock_client_class.return_value = mock_client

    payload = {"mode": "document-analysis", "prompt": "Summarize this", "files": ["/tmp/doc.pdf"]}

    result = run_openclaw_skill(payload)

    assert result["status"] == "success"
    assert result["text"] == "Document summary"

    # Verify request creation
    args, kwargs = mock_client.create_image.call_args
    request_obj = args[0]
    assert request_obj.prompt == "Summarize this"
    assert request_obj.mode == "document-analysis"
    assert request_obj.files == ["/tmp/doc.pdf"]


@patch("openclaw_gemini_web.skill.openclaw_adapter.GeminiWebClient")
def test_openclaw_adapter_storybook_create(mock_client_class):
    mock_client = MagicMock()
    mock_client.create.return_value = GeminiWebCreateResult(status="success", share_link="https://gemini.google.com/share/123")
    mock_client_class.return_value = mock_client

    payload = {"mode": "create", "prompt": "Create a storybook", "return_mode": "share_link"}

    result = run_openclaw_skill(payload)

    assert result["status"] == "success"
    assert result["share_link"] == "https://gemini.google.com/share/123"

    # Verify request creation
    args, kwargs = mock_client.create.call_args
    request_obj = args[0]
    assert request_obj.prompt == "Create a storybook"
    assert request_obj.return_mode == "share_link"
