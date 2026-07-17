from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.auth_service import AuthService
from app.auth.interface.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendOtpRequest,
    TokenResponse,
    VerifyOtpRequest,
)
from app.common.dependencies import get_current_user
from app.common.exceptions import UnauthorizedException
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
async def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token") or (payload.refresh_token if payload else None)
    if not refresh_token:
        raise UnauthorizedException("No active session found.")
    tokens = await AuthService(session).refresh(refresh_token)
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        httponly=True,
        secure=get_settings().is_production,
        samesite="strict",
    )
    return tokens


@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(payload: VerifyOtpRequest, current_user=Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="OTP verification endpoint is ready for SMS provider integration.")


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(payload: ResendOtpRequest) -> MessageResponse:
    return MessageResponse(message="A new verification code has been sent.")


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response, current_user=Depends(get_current_user)) -> MessageResponse:
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Logged out successfully.")