from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, require_role
from app.core.config import get_settings
from app.core.database import get_session
from app.payments.application.payment_service import PaymentService
from app.payments.infrastructure.models import PaymentProvider
from app.payments.interface.schemas import (
    PaymentResponse,
    PaymentWebhook,
    WalletResponse,
    WalletTransactionResponse,
    WithdrawRequest,
)

router = APIRouter(tags=["payments"])


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> WalletResponse:
    return await PaymentService(session).get_wallet(current_user)


@router.get("/wallet/transactions", response_model=list[WalletTransactionResponse])
async def list_wallet_transactions(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[WalletTransactionResponse]:
    return await PaymentService(session).list_transactions(current_user)


@router.post("/wallet/withdraw", response_model=WalletTransactionResponse, status_code=201)
async def withdraw(
    payload: WithdrawRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user=Depends(require_role("SELLER", "RIDER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> WalletTransactionResponse:
    return await PaymentService(session).withdraw(current_user, payload.amount_cents, idempotency_key)


@router.post("/payments/webhooks/momo", response_model=PaymentResponse)
async def momo_webhook(
    payload: PaymentWebhook,
    x_momo_signature: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> PaymentResponse:
    return await PaymentService(session).process_webhook(
        PaymentProvider.MOMO,
        payload,
        x_momo_signature,
        get_settings().momo_webhook_secret,
    )


@router.post("/payments/webhooks/stripe", response_model=PaymentResponse)
async def stripe_webhook(
    payload: PaymentWebhook,
    stripe_signature: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> PaymentResponse:
    return await PaymentService(session).process_webhook(
        PaymentProvider.STRIPE,
        payload,
        stripe_signature,
        get_settings().stripe_webhook_secret,
    )
