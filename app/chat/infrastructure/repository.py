from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.infrastructure.models import Conversation, Message


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_conversations(self) -> list[Conversation]:
        result = await self.session.execute(select(Conversation))
        return list(result.scalars().all())

    async def list_messages(self, conversation_id: UUID) -> list[Message]:
        result = await self.session.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_message(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        return message
