from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class TransactionType(str, PyEnum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class LedgerStatus(str, PyEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PaymentProvider(str, PyEnum):
    MOMO = "MOMO"
    STRIPE = "STRIPE"


class PaymentStatus(str, PyEnum):
    INITIATED = "INITIATED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PayoutStatus(str, PyEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    balance_cents: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")


class WalletTransaction(TimestampMixin, Base):
    __tablename__ = "wallet_transactions"
    __table_args__ = (UniqueConstraint("idempotency_key"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    wallet_id: Mapped[UUID] = mapped_column(ForeignKey("wallets.id"), index=True)
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    amount_cents: Mapped[int] = mapped_column(Integer)
    reference_type: Mapped[str] = mapped_column(String(40))
    reference_id: Mapped[UUID]
    status: Mapped[LedgerStatus] = mapped_column(SQLEnum(LedgerStatus), default=LedgerStatus.PENDING)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True)


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("provider_reference"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    provider: Mapped[PaymentProvider] = mapped_column(SQLEnum(PaymentProvider))
    provider_reference: Mapped[str] = mapped_column(String(180), unique=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.INITIATED)
    raw_webhook_payload: Mapped[dict[str, object] | None] = mapped_column(JSON)


class Payout(TimestampMixin, Base):
    __tablename__ = "payouts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[PayoutStatus] = mapped_column(SQLEnum(PayoutStatus), default=PayoutStatus.PENDING)
    paid_at: Mapped[str | None] = mapped_column(String(40))
