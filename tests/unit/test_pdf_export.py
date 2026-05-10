import pytest
from unittest.mock import Mock

from openclaw_gemini_web.export.pdf_export import export_pdf
from openclaw_gemini_web.exceptions import PdfExportFailedError

def test_export_pdf_requires_output_path(tmp_path):
    page = Mock()
    with pytest.raises(PdfExportFailedError, match="output_path is required for return_mode=pdf"):
        export_pdf(page, None, tmp_path)

    with pytest.raises(PdfExportFailedError, match="output_path is required for return_mode=pdf"):
        export_pdf(page, "", tmp_path)

def test_export_pdf_success(tmp_path):
    page = Mock()
    output_path = tmp_path / "test.pdf"

    result = export_pdf(page, str(output_path), tmp_path)

    assert result == str(output_path.resolve())
    page.pdf.assert_called_once_with(path=str(output_path.resolve()), print_background=True)


def test_export_pdf_exception(tmp_path):
    page = Mock()
    output_path = tmp_path / "test.pdf"
    page.pdf.side_effect = Exception("Simulated Playwright error")

    with pytest.raises(PdfExportFailedError, match="Simulated Playwright error"):
        export_pdf(page, str(output_path), tmp_path)

    page.pdf.assert_called_once_with(path=str(output_path.resolve()), print_background=True)
