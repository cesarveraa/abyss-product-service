from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.security.auth import get_current_user, CurrentUser


async def get_db_session(db: AsyncSession = Depends(get_db)):
    return db


async def get_authenticated_user(
    current_user: CurrentUser = Depends(get_current_user),
):
    return current_user
