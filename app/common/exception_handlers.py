from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.exceptions import AppException


def error_body(code: str, message: str, status_code: int, details: dict[str, object] | None = None) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "status_code": status_code, "details": details or {}}}


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.status_code, exc.details),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = [
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_body(
            "VALIDATION_ERROR",
            "Please check the highlighted fields and try again.",
            422,
            {"fields": fields},
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body("HTTP_ERROR", str(exc.detail), exc.status_code),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Ensures every 500 (including DB/driver errors, missing tables, etc.)
    # comes back as the same JSON error shape as everything else, instead
    # of a bare "Internal Server Error" text response.
    return JSONResponse(
        status_code=500,
        content=error_body(
            "INTERNAL_ERROR",
            "Something went wrong on our end. Please try again shortly.",
            500,
            {"exception_type": type(exc).__name__},
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
