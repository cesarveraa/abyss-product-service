import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Awaitable
from fastapi import status
from fastapi.responses import JSONResponse

# rate limit muy simple en memoria (para demo)
_request_counter: dict[str, int] = {}
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_IP = 300


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        method = request.method
        path = request.url.path
        status_code = response.status_code
        # aquí podrías mandar a Prometheus, Loki, etc.
        print(f"{method} {path} -> {status_code} [{duration:.2f} ms]")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.window_start = time.time()

    async def dispatch(self, request: Request, call_next):
        global _request_counter
        now = time.time()

        # reseteo de ventana
        if now - self.window_start > WINDOW_SECONDS:
            _request_counter = {}
            self.window_start = now

        ip = request.client.host if request.client else "unknown"
        _request_counter[ip] = _request_counter.get(ip, 0) + 1

        if _request_counter[ip] > MAX_REQUESTS_PER_IP:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"},
            )

        return await call_next(request)
