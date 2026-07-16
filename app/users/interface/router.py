from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user
from app.core.database import get_session
from app.users.application.user_service import UserService
from app.users.interface.schemas import AddressCreateRequest, AddressResponse, CurrentUserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> CurrentUserResponse:
    return UserService(session).summarize(current_user)


@router.patch("/me", response_model=CurrentUserResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CurrentUserResponse:
    return await UserService(session).update_me(current_user, payload.full_name, payload.phone)


@router.get("/me/addresses", response_model=list[AddressResponse])
async def list_addresses(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[AddressResponse]:
    return await UserService(session).list_addresses(current_user)


@router.post("/me/addresses", response_model=AddressResponse, status_code=201)
async def create_address(
    payload: AddressCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AddressResponse:
    return await UserService(session).create_address(current_user, payload)
