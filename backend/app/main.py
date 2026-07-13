import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import init_db
from app.exceptions import AppError
from app.logging_config import configure_logging, get_logger, log_with_fields, new_request_id, request_id_var
from app.routers import items, query

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="AI Knowledge Inbox", version="1.0.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = new_request_id()
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        log_with_fields(logger, 20, "request_started", method=request.method, path=request.url.path)
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log_with_fields(
            logger, 20, "request_completed",
            method=request.method, path=request.url.path,
            status_code=response.status_code, duration_ms=duration_ms,
        )
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        request_id_var.reset(token)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log_with_fields(logger, 30, "app_error", code=exc.code, message=exc.message, path=request.url.path)
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []) if loc != "body")
    message = f"{field}: {first_error.get('msg', 'invalid input')}" if field else "Invalid request body."
    log_with_fields(logger, 30, "request_validation_error", message=message, path=request.url.path)
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": message}})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log_with_fields(logger, 40, "unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}},
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    log_with_fields(logger, 20, "app_startup", database_path=settings.database_path)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(items.router)
app.include_router(query.router)
