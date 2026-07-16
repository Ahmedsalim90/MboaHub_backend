from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.infrastructure.models import Payment, Wallet, WalletTransaction


class WalletRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, user_id: UUID, currency: str = "USD") -> Wallet:
        result = await self.session.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()
        if wallet is None:
            wallet = Wallet(user_id=user_id, currency=currency)
            self.session.add(wallet)
            await self.session.flush()
        return wallet

    async def list_transactions(self, wallet_id: UUID) -> list[WalletTransaction]:
        result = await self.session.execute(
            select(WalletTransaction).where(WalletTransaction.wallet_id == wallet_id).order_by(WalletTransaction.created_at.desc())
        )
        return list(result.scalars().all())


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_reference(self, provider_reference: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.provider_reference == provider_reference))
        return result.scalar_one_or_none()

    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.flush()
        return payment
