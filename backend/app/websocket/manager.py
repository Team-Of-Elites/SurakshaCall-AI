import asyncio
from collections import defaultdict
from typing import Literal, Sequence

from fastapi import WebSocket

from backend.app.schemas.events import EventEnvelope


ClientKind = Literal["dashboard", "mobile"]


class WebSocketManager:
    def __init__(self, max_payload_bytes: int = 64_000) -> None:
        self.max_payload_bytes = max_payload_bytes
        self._connections: dict[str, dict[ClientKind, set[WebSocket]]] = defaultdict(
            lambda: {"dashboard": set(), "mobile": set()}
        )

    async def connect(self, session_id: str, kind: ClientKind, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[session_id][kind].add(websocket)

    def disconnect(self, session_id: str, kind: ClientKind, websocket: WebSocket) -> None:
        self._connections[session_id][kind].discard(websocket)
        if not self._connections[session_id]["dashboard"] and not self._connections[session_id]["mobile"]:
            self._connections.pop(session_id, None)

    async def broadcast(
        self, event: EventEnvelope, kinds: Sequence[ClientKind] | None = None
    ) -> None:
        payload = event.model_dump_json()
        if len(payload.encode("utf-8")) > self.max_payload_bytes:
            return
        selected_kinds = kinds or ("dashboard", "mobile")
        targets = [
            websocket
            for kind, clients in self._connections.get(event.session_id, {}).items()
            if kind in selected_kinds
            for websocket in clients
        ]
        if not targets:
            return
        results = await asyncio.gather(
            *(self._send(websocket, payload) for websocket in targets),
            return_exceptions=True,
        )
        for websocket, result in zip(targets, results, strict=False):
            if isinstance(result, Exception):
                self._remove_socket(event.session_id, websocket)

    async def _send(self, websocket: WebSocket, payload: str) -> None:
        await asyncio.wait_for(websocket.send_text(payload), timeout=1.0)

    def _remove_socket(self, session_id: str, websocket: WebSocket) -> None:
        for clients in self._connections.get(session_id, {}).values():
            clients.discard(websocket)

    def counts(self) -> dict[str, dict[str, int]]:
        return {
            session_id: {
                kind: len(connections)
                for kind, connections in groups.items()
            }
            for session_id, groups in self._connections.items()
        }
