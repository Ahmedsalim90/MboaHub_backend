from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.chat.infrastructure.models import Message
from app.chat.infrastructure.repository import ChatRepository


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ChatRepository(session)
        self.session = session

    async def list_conversations(self):
        return await self.repository.list_conversations()

    async def list_messages(self, conversation_id: UUID):
        return await self.repository.list_messages(conversation_id)

    async def send_message(self, user: User, conversation_id: UUID, content: str) -> Message:
        return await self.repository.create_message(
            Message(conversation_id=conversation_id, sender_id=user.id, content=content)
        )
