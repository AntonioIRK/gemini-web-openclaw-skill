from unittest.mock import MagicMock
from openclaw_gemini_web.web.base_runner import GeminiWebRunnerBase

def test_html_text_excerpt_security():
    runner = GeminiWebRunnerBase(MagicMock(), MagicMock())
    page = MagicMock()
    # If unescape happens before stripping tags, it should produce <script>alert(1)</script>
    # which is then stripped out completely by re.sub(r"<script.*?</script>").
    page.content.return_value = "&lt;script&gt;alert(1)&lt;/script&gt;Safe Text"
    excerpt = runner._html_text_excerpt(page)
    assert "alert(1)" not in excerpt
    assert "Safe Text" in excerpt

def test_html_text_excerpt_normal():
    runner = GeminiWebRunnerBase(MagicMock(), MagicMock())
    page = MagicMock()
    page.content.return_value = "<html><body><p>Hello &amp; Welcome</p></body></html>"
    excerpt = runner._html_text_excerpt(page)
    assert excerpt == "Hello & Welcome"
