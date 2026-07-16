from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.application.chat_service import ChatService
from app.chat.interface.schemas import ConversationResponse, MessageCreateRequest, MessageResponse
from app.common.dependencies import get_current_user
from app.core.database import get_session

router = APIRouter(tags=["chat"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await ChatService(session).list_conversations()


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[MessageResponse]:
    return await ChatService(session).list_messages(conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    conversation_id: UUID,
    payload: MessageCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    return await ChatService(session).send_message(current_user, conversation_id, payload.content)
