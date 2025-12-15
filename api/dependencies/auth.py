from fastapi import Depends, HTTPException, status, Request

async def get_current_user(request: Request):
    """
    Authentication placeholder.
    Later this will validate JWT / OAuth / etc.
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # fake user for now (stub)
    return {
        "id": "stub-user",
        "role": "user",
    }
