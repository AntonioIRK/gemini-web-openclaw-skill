import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from openclaw_gemini_web.export.pdf_export import export_pdf
from openclaw_gemini_web.web.base_runner import GeminiWebRunnerBase
from openclaw_gemini_web.web.storybook_runner import StorybookRunner
from openclaw_gemini_web.config import GeminiWebConfig


def test_export_pdf_path_traversal(tmp_path):
    page = Mock()
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()

    # Valid path
    valid_path = workspace_root / "valid.pdf"
    result = export_pdf(page, str(valid_path), workspace_root)
    assert result == str(valid_path.resolve())

    # Invalid path (path traversal)
    invalid_path = tmp_path / "invalid.pdf"
    with pytest.raises(ValueError, match="Path traversal detected"):
        export_pdf(page, str(invalid_path), workspace_root)

    # Invalid path via relative traversal
    invalid_path_relative = workspace_root / ".." / "invalid2.pdf"
    with pytest.raises(ValueError, match="Path traversal detected"):
        export_pdf(page, str(invalid_path_relative), workspace_root)


def test_base_runner_upload_files_path_traversal(tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    config = MagicMock(spec=GeminiWebConfig)
    config.workspace_root = workspace_root

    runner = GeminiWebRunnerBase(config, MagicMock())
    page = Mock()

    # Valid file
    valid_file = workspace_root / "valid.txt"
    valid_file.touch()

    # Should not raise ValueError for path traversal, but may raise PromptSubmissionError because mock page has no UI
    try:
        runner._upload_files(page, [str(valid_file)])
    except Exception as e:
        assert "Path traversal detected" not in str(e)

    # Invalid file (path traversal)
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.touch()
    with pytest.raises(ValueError, match="Path traversal detected for file"):
        runner._upload_files(page, [str(invalid_file)])

def test_storybook_runner_upload_files_path_traversal(tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    config = MagicMock(spec=GeminiWebConfig)
    config.workspace_root = workspace_root

    runner = StorybookRunner(config, MagicMock())
    page = Mock()

    # Valid file
    valid_file = workspace_root / "valid.txt"
    valid_file.touch()

    # Should not raise ValueError for path traversal
    try:
        runner._upload_files(page, [str(valid_file)])
    except Exception as e:
        assert "Path traversal detected" not in str(e)

    # Invalid file (path traversal)
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.touch()
    with pytest.raises(ValueError, match="Path traversal detected for file"):
        runner._upload_files(page, [str(invalid_file)])
