from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class CurrentUser:
    def __init__(self, sub: str, role: str | None = None):
        self.sub = sub
        self.role = role


def _get_token_from_cookie_or_header(request: Request) -> str | None:
    # 1) cookie de sesión (Supabase / tu auth)
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
            detail="No autenticado",
        )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )
        sub: str | None = payload.get("sub")
        role: str | None = payload.get("role")

        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        return CurrentUser(sub=sub, role=role)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
        )
