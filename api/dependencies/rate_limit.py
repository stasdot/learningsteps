import time
from fastapi import Request, HTTPException

RATE_LIMIT = 60  # requests
WINDOW = 60      # seconds

_clients = {}

async def rate_limit(request: Request):
    ip = request.client.host
    now = time.time()

    timestamps = _clients.get(ip, [])
    timestamps = [t for t in timestamps if now - t < WINDOW]

    if len(timestamps) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="too many requests")

    timestamps.append(now)
    _clients[ip] = timestamps
