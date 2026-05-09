from openclaw_gemini_web.models import (
    GeminiWebCreateRequest,
    GeminiWebCreateResult,
    StorybookRequest,
    StorybookResult,
)


def test_request_defaults():
    req = GeminiWebCreateRequest(prompt="hello")
    assert req.return_mode == "share_link"
    assert req.files == []


def test_result_to_dict_hides_empty_metadata():
    result = GeminiWebCreateResult(status="success")
    data = result.to_dict()
    assert "metadata" not in data


def test_gemini_web_aliases_match_storybook_contract():
    req = GeminiWebCreateRequest(prompt="hello")
    result = GeminiWebCreateResult(status="success")
    assert StorybookRequest is GeminiWebCreateRequest
    assert StorybookResult is GeminiWebCreateResult
    assert isinstance(req, StorybookRequest)
    assert isinstance(result, StorybookResult)


def test_primary_names_are_gemini_web_first():
    req = GeminiWebCreateRequest(prompt="hello")
    result = GeminiWebCreateResult(status="success")
    assert req.__class__.__name__ == "GeminiWebCreateRequest"
    assert result.__class__.__name__ == "GeminiWebCreateResult"
