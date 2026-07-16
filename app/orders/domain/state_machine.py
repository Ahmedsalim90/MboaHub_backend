from app.common.exceptions import ConflictException
from app.orders.infrastructure.models import OrderStatus


ALLOWED_ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT: {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID: {OrderStatus.PREPARING, OrderStatus.CANCELLED, OrderStatus.DISPUTED},
    OrderStatus.PREPARING: {OrderStatus.RIDER_REQUESTED},
    OrderStatus.RIDER_REQUESTED: {OrderStatus.RIDER_ASSIGNED},
    OrderStatus.RIDER_ASSIGNED: {OrderStatus.EN_ROUTE_TO_SELLER},
    OrderStatus.EN_ROUTE_TO_SELLER: {OrderStatus.PICKED_UP},
    OrderStatus.PICKED_UP: {OrderStatus.EN_ROUTE_TO_CUSTOMER},
    OrderStatus.EN_ROUTE_TO_CUSTOMER: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: {OrderStatus.CONFIRMED, OrderStatus.DISPUTED},
    OrderStatus.CONFIRMED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.DISPUTED: set(),
}


def assert_order_transition(current: OrderStatus, next_status: OrderStatus) -> None:
    if next_status not in ALLOWED_ORDER_TRANSITIONS[current]:
        raise ConflictException(
            f"Order cannot move from {current.value} to {next_status.value}.",
            {"current_status": current.value, "next_status": next_status.value},
        )
