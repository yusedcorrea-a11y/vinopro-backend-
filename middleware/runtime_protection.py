from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RuntimeProtectionMiddleware(BaseHTTPMiddleware):
    """
    Protección ligera para free tier:
    - rate limit general por sesión/IP
    - límites más estrictos para rutas calientes
    - métricas básicas de tiempo y errores por ruta
    """

    def __init__(
        self,
        app,
        *,
        default_limit: int = 90,
        hot_limit: int = 12,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.default_limit = max(1, int(default_limit))
        self.hot_limit = max(1, int(hot_limit))
        self.window_seconds = max(5, int(window_seconds))
        self.hits: dict[str, deque[float]] = defaultdict(deque)
        self.hot_paths = (
            "/escanear",
            "/api/translate-comment",
            "/api/preguntar-local",
            "/api/chat",
        )
        self.skip_prefixes = ("/static",)
        self.skip_exact = {"/health", "/ready", "/api/status", "/favicon.ico", "/favicon.svg"}

    def _client_key(self, request: Request) -> str:
        session_id = (request.headers.get("X-Session-ID") or "").strip()
        ip = request.client.host if request.client else "anon"
        path = request.url.path
        return f"{session_id or ip}:{path}"

    def _limit_for_path(self, path: str) -> int:
        return self.hot_limit if any(path.startswith(prefix) for prefix in self.hot_paths) else self.default_limit

    def _is_skipped(self, path: str) -> bool:
        if path in self.skip_exact:
            return True
        return any(path.startswith(prefix) for prefix in self.skip_prefixes)

    def _ensure_metrics(self, request: Request) -> dict:
        metrics = getattr(request.app.state, "runtime_metrics", None)
        if not isinstance(metrics, dict):
            metrics = {
                "started_at": time.time(),
                "total_requests": 0,
                "rate_limited": 0,
                "errors_5xx": 0,
                "by_path": {},
            }
            request.app.state.runtime_metrics = metrics
        return metrics

    def _update_metrics(self, request: Request, path: str, elapsed_ms: float, status_code: int) -> None:
        metrics = self._ensure_metrics(request)
        metrics["total_requests"] = int(metrics.get("total_requests", 0)) + 1
        if status_code >= 500:
            metrics["errors_5xx"] = int(metrics.get("errors_5xx", 0)) + 1
        by_path = metrics.setdefault("by_path", {})
        entry = by_path.setdefault(
            path,
            {"count": 0, "errors_5xx": 0, "last_status": 0, "avg_ms": 0.0, "max_ms": 0.0},
        )
        count = int(entry.get("count", 0)) + 1
        prev_avg = float(entry.get("avg_ms", 0.0))
        entry["count"] = count
        entry["last_status"] = status_code
        entry["avg_ms"] = round(((prev_avg * (count - 1)) + elapsed_ms) / count, 2)
        entry["max_ms"] = round(max(float(entry.get("max_ms", 0.0)), elapsed_ms), 2)
        if status_code >= 500:
            entry["errors_5xx"] = int(entry.get("errors_5xx", 0)) + 1

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        start = time.perf_counter()

        if self._is_skipped(path):
            response = await call_next(request)
            self._update_metrics(request, path, (time.perf_counter() - start) * 1000, response.status_code)
            return response

        key = self._client_key(request)
        bucket = self.hits[key]
        now = time.time()
        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        limit = self._limit_for_path(path)
        if len(bucket) >= limit:
            metrics = self._ensure_metrics(request)
            metrics["rate_limited"] = int(metrics.get("rate_limited", 0)) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes en poco tiempo. Espera unos segundos e inténtalo de nuevo.",
                    "path": path,
                },
            )

        bucket.append(now)
        response = await call_next(request)
        self._update_metrics(request, path, (time.perf_counter() - start) * 1000, response.status_code)
        return response
