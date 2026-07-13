class AppError(Exception):
    """Base class for expected, user-facing application errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationAppError(AppError):
    status_code = 400
    code = "validation_error"


class NotFoundAppError(AppError):
    status_code = 404
    code = "not_found"


class UrlFetchError(AppError):
    status_code = 502
    code = "url_fetch_failed"


class LlmError(AppError):
    status_code = 502
    code = "llm_error"


class EmbeddingError(AppError):
    status_code = 500
    code = "embedding_error"
