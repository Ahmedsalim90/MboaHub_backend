class AppException(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "Something went wrong."

    def __init__(self, message: str | None = None, details: dict[str, object] | None = None) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class BadRequestException(AppException):
    status_code = 400
    code = "BAD_REQUEST"
    message = "The request could not be processed."


class UnauthorizedException(AppException):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Authentication is required."


class ForbiddenException(AppException):
    status_code = 403
    code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class NotFoundException(AppException):
    status_code = 404
    code = "NOT_FOUND"
    message = "The requested resource was not found."


class ConflictException(AppException):
    status_code = 409
    code = "CONFLICT"
    message = "The request conflicts with the current resource state."
