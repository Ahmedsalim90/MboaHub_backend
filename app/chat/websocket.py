from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websockets"])


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms[room_id].add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        self.rooms[room_id].discard(websocket)

    async def broadcast(self, room_id: str, message: dict[str, object]) -> None:
        for websocket in list(self.rooms[room_id]):
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def chat_socket(websocket: WebSocket, conversation_id: UUID) -> None:
    room = f"chat:{conversation_id}"
    await manager.connect(room, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            await manager.broadcast(room, payload)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)


@router.websocket("/ws/delivery/{delivery_id}")
async def delivery_socket(websocket: WebSocket, delivery_id: UUID) -> None:
    room = f"delivery:{delivery_id}"
    await manager.connect(room, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            await manager.broadcast(room, payload)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)


@router.websocket("/ws/notifications")
async def notifications_socket(websocket: WebSocket) -> None:
    room = "notifications"
    await manager.connect(room, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            await manager.broadcast(room, payload)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
