import asyncio
import json
import uuid
from typing import Dict, Any, List
from fastapi import WebSocket
from app.core.logger import logger

class NotificationManager:
    """
    SOLID Singleton for managing real-time notifications via WebSocket.
    Broadcasting events from Binance Stream and Bot Logic to Frontend.
    Now with unique connection IDs and robust leak prevention.
    """
    def __init__(self):
        # Map of connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        conn_id = str(uuid.uuid4())[:8]
        self.active_connections[conn_id] = websocket
        logger.info(f"[WS] Client {conn_id} connected. Total: {len(self.active_connections)}")
        
        # Send initial success message with connection ID
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to Binance Tracker Real-Time Monitor",
            "connection_id": conn_id
        })
        return conn_id

    def disconnect(self, conn_id: str):
        if conn_id in self.active_connections:
            del self.active_connections[conn_id]
            logger.info(f"[WS] Client {conn_id} disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Push updates to all connected frontend clients.
        Example event_type: 'order_update', 'ticker_update', 'error'
        """
        if not self.active_connections:
            return

        payload = {
            "type": event_type,
            "data": data
        }
        
        message = json.dumps(payload)
        
        # Identify clients that fail to receive messages for pruning
        failed_ids: List[str] = []
        
        # We wrap in a list to safely iterate over current keys
        for conn_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(message)
            except Exception as e:
                # Silently mark for removal without bloating logs if it's just a closure
                failed_ids.append(conn_id)

        # Cleanup failed connections
        for cid in failed_ids:
            self.disconnect(cid)

# Global notification manager instance
notification_manager = NotificationManager()
