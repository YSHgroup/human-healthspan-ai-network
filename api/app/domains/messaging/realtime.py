"""In-process delivery for authenticated text-message WebSocket connections."""

import asyncio

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class MessageConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.setdefault(conversation_id, set()).add(websocket)

    async def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(conversation_id)
            if connections is None:
                return
            connections.discard(websocket)
            if not connections:
                self._connections.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, message: dict[str, str]) -> None:
        async with self._lock:
            connections = tuple(self._connections.get(conversation_id, ()))

        disconnected: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError, OSError):
                disconnected.append(websocket)

        for websocket in disconnected:
            await self.disconnect(conversation_id, websocket)


message_connections = MessageConnectionManager()
