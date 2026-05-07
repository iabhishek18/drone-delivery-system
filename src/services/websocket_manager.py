from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, drone_id: str):
        await websocket.accept()
        if drone_id not in self.active_connections:
            self.active_connections[drone_id] = []
        self.active_connections[drone_id].append(websocket)

    def disconnect(self, websocket: WebSocket, drone_id: str):
        if drone_id in self.active_connections:
            self.active_connections[drone_id] = [ws for ws in self.active_connections[drone_id] if ws != websocket]

    async def broadcast_position(self, drone_id: str, data: dict):
        if drone_id in self.active_connections:
            for connection in self.active_connections[drone_id]:
                try:
                    await connection.send_json({"drone_id": drone_id, **data})
                except:
                    pass

manager = ConnectionManager()
