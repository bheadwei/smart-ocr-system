"""
WebSocket connection manager service.
"""
from typing import Dict, List
from datetime import datetime

from fastapi import WebSocket


class WebSocketManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        """
        Accept and register a WebSocket connection.

        Args:
            task_id: Task ID to subscribe to
            websocket: WebSocket connection
        """
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = []

        self.active_connections[task_id].append(websocket)

    def disconnect(self, task_id: str, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            task_id: Task ID
            websocket: WebSocket connection to remove
        """
        if task_id in self.active_connections:
            try:
                self.active_connections[task_id].remove(websocket)
            except ValueError:
                pass

            # Clean up empty lists
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def send_progress(self, task_id: str, progress: int, status: str):
        """
        Send progress update to all connections subscribed to a task.

        Args:
            task_id: Task ID
            progress: Progress percentage (0-100)
            status: Current status
        """
        if task_id not in self.active_connections:
            return

        message = {
            "type": "progress",
            "task_id": task_id,
            "progress": progress,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to all connections, remove dead ones
        dead_connections = []

        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(task_id, connection)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all active connections.

        Args:
            message: Message dict to send
        """
        for task_id in list(self.active_connections.keys()):
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass
