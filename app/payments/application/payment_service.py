from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.common.exceptions import BadRequestException, UnauthorizedException
from app.orders.infrastructure.repository import OrderRepository
from app.payments.infrastructure.models import Payment, PaymentProvider, Wallet, WalletTransaction
from app.payments.infrastructure.repository import PaymentRepository, WalletRepository
from app.payments.interface.schemas import PaymentWebhook


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.wallets = WalletRepository(session)
        self.payments = PaymentRepository(session)
        self.orders = OrderRepository(session)

    async def get_wallet(self, user: User) -> Wallet:
        return await self.wallets.get_or_create(user.id)

    async def list_transactions(self, user: User) -> list[WalletTransaction]:
        wallet = await self.get_wallet(user)
        return await self.wallets.list_transactions(wallet.id)

    async def withdraw(self, user: User, amount_cents: int, idempotency_key: str | None) -> WalletTransaction:
        if not idempotency_key:
            raise BadRequestException("Idempotency-Key header is required for withdrawals.")
        wallet = await self.wallets.get_or_create(user.id)
        if wallet.balance_cents < amount_cents:
            raise BadRequestException("Your wallet balance is too low for this withdrawal.")
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type="DEBIT",
            amount_cents=amount_cents,
            reference_type="PAYOUT",
            reference_id=user.id,
            status="PENDING",
            idempotency_key=idempotency_key,
        )
        wallet.balance_cents -= amount_cents
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def process_webhook(
        self,
        provider: PaymentProvider,
        payload: PaymentWebhook,
        signature: str | None,
        expected_signature: str,
    ) -> Payment:
        if expected_signature and signature != expected_signature:
            raise UnauthorizedException("Invalid payment webhook signature.")
        existing = await self.payments.get_by_provider_reference(payload.provider_reference)
        if existing is not None:
            return existing
        order = await self.orders.get_by_id(payload.order_id)
        if order is None:
            raise BadRequestException("Webhook references an unknown order.")
        payment = Payment(
            order_id=payload.order_id,
            provider=provider,
            provider_reference=payload.provider_reference,
            amount_cents=payload.amount_cents,
            status=payload.status,
            raw_webhook_payload=payload.payload,
        )
        return await self.payments.create(payment)
