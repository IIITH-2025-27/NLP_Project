"""
In-memory rate limiting (sliding window per key).

Good enough for a single Render instance; counters reset when the server restarts.
Limits are applied per client IP and, where it matters, per email or per user
(those can't be spoofed by changing IP).
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

_hits = defaultdict(deque)
_lock = Lock()


def client_ip(request: Request) -> str:
    """Real client IP. Render sits behind Cloudflare, which sets CF-Connecting-IP itself."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(key: str, limit: int, window_seconds: int):
    """Raise 429 if `key` was hit `limit` times in the last `window_seconds`."""
    now = time.monotonic()
    with _lock:
        hits = _hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            retry_after = int(window_seconds - (now - hits[0])) + 1
            minutes = (retry_after + 59) // 60
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Please try again in {minutes} minute{'s' if minutes > 1 else ''}.",
                headers={"Retry-After": str(retry_after)},
            )
        hits.append(now)


def rate_limit_ip(name: str, limit: int, window_seconds: int):
    """FastAPI dependency: limit a route per client IP."""
    def dependency(request: Request):
        check_rate_limit(f"{name}:ip:{client_ip(request)}", limit, window_seconds)
    return dependency


def rate_limit_email(name: str, email: str, limit: int, window_seconds: int):
    check_rate_limit(f"{name}:email:{email.strip().lower()}", limit, window_seconds)
