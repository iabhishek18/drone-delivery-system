from typing import Optional


class AppError(Exception):
    def __init__(
        self, status_code: int, code: str, message: str, details: Optional[dict] = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    @classmethod
    def bad_request(
        cls, code: str, message: str, details: Optional[dict] = None
    ) -> "AppError":
        return cls(400, code, message, details)

    @classmethod
    def not_found(cls, resource: str, identifier: str) -> "AppError":
        return cls(404, "NOT_FOUND", f"{resource} '{identifier}' not found")

    @classmethod
    def conflict(cls, message: str) -> "AppError":
        return cls(409, "CONFLICT", message)

    @classmethod
    def validation_error(
        cls, message: str, details: Optional[dict] = None
    ) -> "AppError":
        return cls(422, "VALIDATION_ERROR", message, details)
