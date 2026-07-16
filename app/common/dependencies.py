from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.repository import UserRepository
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.core.database import get_session
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
):
    if credentials is None:
        raise UnauthorizedException()
    try:
        payload = decode_token(credentials.credentials)
        user_id = UUID(str(payload["sub"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise UnauthorizedException("Your session has expired. Please log in again.") from exc
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("Your account could not be found.")
    return user


def require_role(*roles: str) -> Callable[..., object]:
    async def dependency(current_user=Depends(get_current_user)):
        current_roles = {role.role for role in current_user.roles}
        if not current_roles.intersection(set(roles)):
            raise ForbiddenException()
        return current_user

    return dependency
