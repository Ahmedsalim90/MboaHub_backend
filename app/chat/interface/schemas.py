from uuid import UUID

from pydantic import Field

from app.chat.infrastructure.models import ConversationType, MessageType
from app.common.schemas import StrictBaseModel


class ConversationResponse(StrictBaseModel):
    id: UUID
    type: ConversationType


class MessageCreateRequest(StrictBaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(StrictBaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str | None
    attachment_url: str | None
    type: MessageType
