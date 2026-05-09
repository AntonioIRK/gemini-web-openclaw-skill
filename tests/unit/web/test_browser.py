import io
import json
from unittest.mock import patch
import pytest

from openclaw_gemini_web.web.browser import _fetch_cdp_ws_url

def test_fetch_cdp_ws_url_success():
    mock_payload = {"webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/12345"}
    mock_response = io.BytesIO(json.dumps(mock_payload).encode("utf-8"))

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_response
        ws_url = _fetch_cdp_ws_url(9222)
        assert ws_url == "ws://127.0.0.1:9222/devtools/browser/12345"

def test_fetch_cdp_ws_url_failure():
    mock_payload = {}
    mock_response = io.BytesIO(json.dumps(mock_payload).encode("utf-8"))

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_response
        with pytest.raises(RuntimeError, match="CDP endpoint on port 9222 did not return webSocketDebuggerUrl"):
            _fetch_cdp_ws_url(9222)
