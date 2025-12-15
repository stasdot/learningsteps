import uuid
import logging
from fastapi import Request

logger = logging.getLogger("request")

async def request_id_middleware(request: Request, call_next):
    # get or generate request id
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    # process request
    response = await call_next(request)

    # attach request id to response
    response.headers["X-Request-ID"] = request_id

    return response
