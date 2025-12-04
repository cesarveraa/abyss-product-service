# app/api/deps.py (o donde lo tengas)
from fastapi import HTTPException, Depends, status, Request
from supabase import Client
from app.core.config import settings
from app.core.supabase_client import get_supabase_client


class CurrentUser:
    def __init__(self, sub: str):
        self.sub = sub  # id del usuario en Supabase (UUID string)


def _get_token_from_cookie_or_header(request: Request) -> str | None:
    # 1) Cookie (lo que setea el auth-service)
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        return token

    # 2) Authorization: Bearer
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]

    return None


async def get_current_user(request: Request) -> CurrentUser:
    token = _get_token_from_cookie_or_header(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado (sin token)",
        )

    supabase: Client = get_supabase_client()

    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido (Supabase no devolvió user)",
            )

        user_id = user_response.user.id  # UUID string
        return CurrentUser(sub=user_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se pudo validar el token en Supabase: {str(e)}",
        )
