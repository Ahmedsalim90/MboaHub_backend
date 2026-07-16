from uuid import UUID

from pydantic import Field

from app.common.schemas import StrictBaseModel
from app.payments.infrastructure.models import LedgerStatus, PaymentProvider, PaymentStatus, TransactionType


class WalletResponse(StrictBaseModel):
    id: UUID
    user_id: UUID
    balance_cents: int
    currency: str


class WalletTransactionResponse(StrictBaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount_cents: int
    reference_type: str
    reference_id: UUID
    status: LedgerStatus
    idempotency_key: str


class WithdrawRequest(StrictBaseModel):
    amount_cents: int = Field(gt=0)


class PaymentWebhook(StrictBaseModel):
    provider_reference: str = Field(min_length=1, max_length=180)
    order_id: UUID
    amount_cents: int = Field(gt=0)
    status: PaymentStatus
    payload: dict[str, object] = {}


class PaymentResponse(StrictBaseModel):
    id: UUID
    order_id: UUID
    provider: PaymentProvider
    provider_reference: str
    amount_cents: int
    status: PaymentStatus
