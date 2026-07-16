from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class OrderStatus(str, PyEnum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    PREPARING = "PREPARING"
    RIDER_REQUESTED = "RIDER_REQUESTED"
    RIDER_ASSIGNED = "RIDER_ASSIGNED"
    EN_ROUTE_TO_SELLER = "EN_ROUTE_TO_SELLER"
    PICKED_UP = "PICKED_UP"
    EN_ROUTE_TO_CUSTOMER = "EN_ROUTE_TO_CUSTOMER"
    DELIVERED = "DELIVERED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cart_id: Mapped[UUID] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents_snapshot: Mapped[int] = mapped_column(Integer)


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    shop_id: Mapped[UUID] = mapped_column(ForeignKey("shops.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, index=True)
    subtotal_cents: Mapped[int] = mapped_column(Integer)
    delivery_fee_cents: Mapped[int] = mapped_column(Integer)
    total_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    delivery_address_id: Mapped[UUID] = mapped_column(ForeignKey("addresses.id"))


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents_snapshot: Mapped[int] = mapped_column(Integer)
