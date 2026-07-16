from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.auth.infrastructure.repository import UserRepository
from app.auth.interface.schemas import TokenResponse, UserSummary
from app.common.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, email: str, password: str, full_name: str, phone: str | None) -> TokenResponse:
        existing_user = await self.users.get_by_email(email)
        if existing_user is not None:
            raise ConflictException("This email is already registered. Try logging in instead.")
        user = await self.users.create_user(email, hash_password(password), full_name, phone)
        return self._tokens_for(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedException("The email or password is incorrect.")
        return self._tokens_for(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user = await self.users.get_by_id(UUID(str(payload["sub"])))
        except (KeyError, TypeError, ValueError) as exc:
            raise UnauthorizedException("Your session has expired. Please log in again.") from exc
        if user is None:
            raise UnauthorizedException("Your account could not be found.")
        return self._tokens_for(user)

    def _tokens_for(self, user: User) -> TokenResponse:
        roles = [role.role for role in user.roles]
        summary = UserSummary(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=roles,
        )
        return TokenResponse(
            access_token=create_access_token(str(user.id), {"roles": roles}),
            refresh_token=create_refresh_token(str(user.id)),
            user=summary,
        )
