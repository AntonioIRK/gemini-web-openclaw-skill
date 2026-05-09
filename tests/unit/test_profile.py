from pathlib import Path
from openclaw_gemini_web.auth.profile import ensure_profile_dir

def test_ensure_profile_dir_creates_dir(tmp_path: Path):
    profile_dir = tmp_path / "new_profile"
    assert not profile_dir.exists()

    result = ensure_profile_dir(profile_dir)

    assert profile_dir.exists()
    assert profile_dir.is_dir()
    assert result == profile_dir

def test_ensure_profile_dir_creates_nested_dir(tmp_path: Path):
    profile_dir = tmp_path / "nested" / "new_profile"
    assert not profile_dir.exists()
    assert not profile_dir.parent.exists()

    result = ensure_profile_dir(profile_dir)

    assert profile_dir.exists()
    assert profile_dir.is_dir()
    assert result == profile_dir

def test_ensure_profile_dir_existing_dir(tmp_path: Path):
    profile_dir = tmp_path / "existing_profile"
    profile_dir.mkdir()
    assert profile_dir.exists()

    result = ensure_profile_dir(profile_dir)

    assert profile_dir.exists()
    assert profile_dir.is_dir()
    assert result == profile_dir
