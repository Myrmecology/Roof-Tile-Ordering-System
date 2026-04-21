# ============================================================
# ROOF TILE ORDERING SYSTEM — WebSocket Connection Manager
# ============================================================

import json
from typing import List
from fastapi import WebSocket
import asyncio


# ============================================================
# CONNECTION MANAGER
# ============================================================
class WebSocketManager:
    """
    Manages all active WebSocket connections.
    Handles connect, disconnect, and broadcasting
    messages to every connected client simultaneously.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    # ----------------------------------------------------------
    # CONNECT
    # ----------------------------------------------------------
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and register it."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"🔌 WebSocket connected — "
              f"{len(self.active_connections)} active connection(s).")

    # ----------------------------------------------------------
    # DISCONNECT
    # ----------------------------------------------------------
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from the active pool."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected — "
              f"{len(self.active_connections)} active connection(s).")

    # ----------------------------------------------------------
    # BROADCAST TO ALL
    # ----------------------------------------------------------
    async def broadcast(self, message: dict):
        """
        Send a JSON message to every active connected client.
        Automatically removes any dead connections encountered.
        """
        if not self.active_connections:
            return

        payload     = json.dumps(message)
        dead        = []

        async with self._lock:
            connections = list(self.active_connections)

        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception:
                dead.append(websocket)

        # Clean up any connections that failed
        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self.active_connections:
                        self.active_connections.remove(ws)
            print(f"🧹 Cleaned {len(dead)} dead WebSocket connection(s).")

    # ----------------------------------------------------------
    # SEND TO ONE CLIENT
    # ----------------------------------------------------------
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send a JSON message to a single specific client."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"⚠️  Failed to send personal message: {e}")
            await self.disconnect(websocket)

    # ----------------------------------------------------------
    # BROADCAST EVENT HELPERS
    # ----------------------------------------------------------
    async def broadcast_new_order(self, order_data: dict):
        """Broadcast a newly generated order to all clients."""
        await self.broadcast({
            "event":   "new_order",
            "payload": order_data
        })

    async def broadcast_order_fulfilled(self, order_data: dict):
        """Broadcast an order fulfillment event to all clients."""
        await self.broadcast({
            "event":   "order_fulfilled",
            "payload": order_data
        })

    async def broadcast_order_cancelled(self, order_data: dict):
        """Broadcast an order cancellation event to all clients."""
        await self.broadcast({
            "event":   "order_cancelled",
            "payload": order_data
        })

    async def broadcast_low_stock(self, item_data: dict):
        """Broadcast a low stock alert to all clients."""
        await self.broadcast({
            "event":   "low_stock_alert",
            "payload": item_data
        })

    async def broadcast_budget_update(self, budget_data: dict):
        """Broadcast a budget change to all clients."""
        await self.broadcast({
            "event":   "budget_update",
            "payload": budget_data
        })

    async def broadcast_restock_placed(self, restock_data: dict):
        """Broadcast a restock order placement to all clients."""
        await self.broadcast({
            "event":   "restock_placed",
            "payload": restock_data
        })

    # ----------------------------------------------------------
    # CONNECTION COUNT
    # ----------------------------------------------------------
    @property
    def connection_count(self) -> int:
        """Return the number of currently active connections."""
        return len(self.active_connections)


# ============================================================
# GLOBAL INSTANCE
# Imported and shared across the entire application
# ============================================================
manager = WebSocketManager()