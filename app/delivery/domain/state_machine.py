from app.common.exceptions import ConflictException
from app.delivery.infrastructure.models import DeliveryStatus


ALLOWED_DELIVERY_TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.REQUESTED: {DeliveryStatus.ACCEPTED},
    DeliveryStatus.ACCEPTED: {DeliveryStatus.EN_ROUTE_TO_SELLER},
    DeliveryStatus.EN_ROUTE_TO_SELLER: {DeliveryStatus.PICKED_UP},
    DeliveryStatus.PICKED_UP: {DeliveryStatus.EN_ROUTE_TO_CUSTOMER},
    DeliveryStatus.EN_ROUTE_TO_CUSTOMER: {DeliveryStatus.DELIVERED},
    DeliveryStatus.DELIVERED: {DeliveryStatus.CONFIRMED},
    DeliveryStatus.CONFIRMED: set(),
    DeliveryStatus.CANCELLED: set(),
}


def assert_delivery_transition(current: DeliveryStatus, next_status: DeliveryStatus) -> None:
    if next_status not in ALLOWED_DELIVERY_TRANSITIONS[current]:
        raise ConflictException(
            f"Delivery cannot move from {current.value} to {next_status.value}.",
            {"current_status": current.value, "next_status": next_status.value},
        )
