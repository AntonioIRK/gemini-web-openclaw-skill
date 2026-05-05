class GeminiWebError(RuntimeError):
    code = "UNKNOWN_RUNTIME_ERROR"


StorybookError = GeminiWebError


class LoginRequiredError(GeminiWebError):
    code = "LOGIN_REQUIRED"


class StorybookNotAvailableError(GeminiWebError):
    code = "STORYBOOK_NOT_AVAILABLE"


class PromptSubmissionError(GeminiWebError):
    code = "PROMPT_SUBMISSION_FAILED"


class UploadFailedError(GeminiWebError):
    code = "UPLOAD_FAILED"


class GenerationTimeoutError(GeminiWebError):
    code = "GENERATION_TIMEOUT"


class GoogleRuntimeError13(GeminiWebError):
    code = "GOOGLE_RUNTIME_ERROR_13"


class GoogleRuntimeError(GeminiWebError):
    code = "GOOGLE_RUNTIME_ERROR"


class ShareLinkNotFoundError(GeminiWebError):
    code = "SHARE_LINK_NOT_FOUND"


class PdfExportFailedError(GeminiWebError):
    code = "PDF_EXPORT_FAILED"
