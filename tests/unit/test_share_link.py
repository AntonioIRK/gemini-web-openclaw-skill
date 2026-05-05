from openclaw_gemini_web.export.share_link import _is_share_link


def test_accepts_gemini_share_links():
    assert _is_share_link("https://gemini.google.com/share/abc123")
    assert _is_share_link("https://g.co/gemini/share/abc123")


def test_rejects_non_share_google_links():
    assert not _is_share_link("https://accounts.google.com/ServiceLogin?continue=https://gemini.google.com/gem/storybook")
    assert not _is_share_link("https://gemini.google.com/gem/storybook")
    assert not _is_share_link(None)
