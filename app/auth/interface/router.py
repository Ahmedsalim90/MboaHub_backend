from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.auth_service import AuthService
from app.auth.interface.schemas import LoginRequest, MessageResponse, RefreshRequest, RegisterRequest, TokenResponse, VerifyOtpRequest
from app.common.dependencies import get_current_user
from app.core.config import get_settings
from app.core.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, response: Response, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    tokens = await AuthService(session).register(payload.email, payload.password, payload.full_name, payload.phone)
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        httponly=True,
        secure=get_settings().is_production,
        samesite="strict",
    )
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    tokens = await AuthService(session).login(payload.email, payload.password)
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        httponly=True,
        secure=get_settings().is_production,
        samesite="strict",
    )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    return await AuthService(session).refresh(payload.refresh_token)


@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(payload: VerifyOtpRequest, current_user=Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="OTP verification endpoint is ready for SMS provider integration.")


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response, current_user=Depends(get_current_user)) -> MessageResponse:
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Logged out successfully.")
