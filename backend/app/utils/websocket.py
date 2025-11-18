"""
WebSocket manager for real-time communication
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
import asyncio
from datetime import datetime

from app.schemas.common import NotificationMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.connection_user: Dict[str, str] = {}  # connection_id -> user_id
        self.user_roles: Dict[str, str] = {}  # user_id -> role
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket, user_id: str, role: str = None):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        
        connection_id = f"{user_id}_{self.connection_count}"
        self.active_connections[connection_id] = websocket
        self.connection_user[connection_id] = user_id
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        if role:
            self.user_roles[user_id] = role
        
        self.connection_count += 1
        
        logger.info(f"WebSocket connected: {connection_id} for user {user_id}")
        
        # Send welcome message
        await self.send_personal_message(
            user_id,
            NotificationMessage(
                type="connection",
                title="Connected",
                message="Successfully connected to real-time updates",
                data={"connection_id": connection_id}
            )
        )
        
        # Notify others about user online status
        await self.broadcast_to_role(
            "hospital_staff",
            NotificationMessage(
                type="user_online",
                title="User Online",
                message=f"User {user_id} is now online",
                data={"user_id": user_id, "role": role}
            ),
            exclude_user=user_id
        )
    
    async def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id not in self.active_connections:
            return
        
        user_id = self.connection_user.get(connection_id)
        websocket = self.active_connections[connection_id]
        
        # Remove connection
        del self.active_connections[connection_id]
        del self.connection_user[connection_id]
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                if user_id in self.user_roles:
                    del self.user_roles[user_id]
                
                # Notify others about user offline status
                await self.broadcast_to_role(
                    "hospital_staff",
                    NotificationMessage(
                        type="user_offline",
                        title="User Offline",
                        message=f"User {user_id} is now offline",
                        data={"user_id": user_id}
                    ),
                    exclude_user=user_id
                )
        
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket {connection_id}: {str(e)}")
        
        logger.info(f"WebSocket disconnected: {connection_id} for user {user_id}")
    
    async def send_personal_message(self, user_id: str, message: NotificationMessage):
        """Send message to specific user"""
        if user_id not in self.user_connections:
            logger.warning(f"User {user_id} not connected")
            return
        
        disconnected_connections = set()
        for connection_id in self.user_connections[user_id]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(message.json())
                except Exception as e:
                    logger.error(f"Error sending message to {connection_id}: {str(e)}")
                    disconnected_connections.add(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)
    
    async def send_to_connection(self, connection_id: str, message: NotificationMessage):
        """Send message to specific connection"""
        if connection_id not in self.active_connections:
            logger.warning(f"Connection {connection_id} not found")
            return
        
        websocket = self.active_connections[connection_id]
        try:
            await websocket.send_text(message.json())
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {str(e)}")
            await self.disconnect(connection_id)
    
    async def broadcast_to_role(self, role: str, message: NotificationMessage, exclude_user: str = None):
        """Broadcast message to all users with specific role"""
        for user_id, user_role in self.user_roles.items():
            if user_role == role and user_id != exclude_user:
                await self.send_personal_message(user_id, message)
    
    async def broadcast_to_all(self, message: NotificationMessage, exclude_user: str = None):
        """Broadcast message to all connected users"""
        for user_id in self.user_connections:
            if user_id != exclude_user:
                await self.send_personal_message(user_id, message)
    
    async def broadcast_to_users(self, user_ids: List[str], message: NotificationMessage):
        """Broadcast message to specific users"""
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)
    
    async def disconnect_user(self, user_id: str):
        """Disconnect all connections for a user"""
        if user_id not in self.user_connections:
            return
        
        connection_ids = list(self.user_connections[user_id])
        for connection_id in connection_ids:
            await self.disconnect(connection_id)
    
    async def disconnect_all(self):
        """Disconnect all connections"""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            await self.disconnect(connection_id)
    
    def get_connected_users(self) -> List[Dict[str, any]]:
        """Get list of connected users"""
        users = []
        for user_id, connections in self.user_connections.items():
            role = self.user_roles.get(user_id)
            users.append({
                "user_id": user_id,
                "role": role,
                "connections": len(connections),
                "connected_at": datetime.utcnow().isoformat()
            })
        return users
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """Get connection IDs for a user"""
        return list(self.user_connections.get(user_id, set()))
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if user is connected"""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "connections_by_role": self._get_connections_by_role()
        }
    
    def _get_connections_by_role(self) -> Dict[str, int]:
        """Get connection count by role"""
        role_counts = {}
        for user_id, role in self.user_roles.items():
            role_counts[role] = role_counts.get(role, 0) + len(self.user_connections[user_id])
        return role_counts


# Global connection manager instance
websocket_manager = ConnectionManager()


class WebSocketMessageHandler:
    """Handler for different types of WebSocket messages"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.handlers = {
            "ping": self._handle_ping,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "typing": self._handle_typing,
            "chat": self._handle_chat_message
        }
    
    async def handle_message(self, connection_id: str, user_id: str, message: dict):
        """Route message to appropriate handler"""
        message_type = message.get("type", "unknown")
        handler = self.handlers.get(message_type)
        
        if handler:
            try:
                await handler(connection_id, user_id, message)
            except Exception as e:
                logger.error(f"Error handling message type {message_type}: {str(e)}")
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def _handle_ping(self, connection_id: str, user_id: str, message: dict):
        """Handle ping messages"""
        await self.connection_manager.send_to_connection(
            connection_id,
            NotificationMessage(
                type="pong",
                title="Pong",
                message="Server response to ping",
                data={"timestamp": datetime.utcnow().isoformat()}
            )
        )
    
    async def _handle_subscribe(self, connection_id: str, user_id: str, message: dict):
        """Handle subscription messages"""
        channel = message.get("channel")
        if not channel:
            return
        
        # Store subscription (implement subscription logic as needed)
        await self.connection_manager.send_to_connection(
            connection_id,
            NotificationMessage(
                type="subscribed",
                title="Subscribed",
                message=f"Subscribed to {channel}",
                data={"channel": channel}
            )
        )
    
    async def _handle_unsubscribe(self, connection_id: str, user_id: str, message: dict):
        """Handle unsubscribe messages"""
        channel = message.get("channel")
        if not channel:
            return
        
        # Remove subscription (implement unsubscribe logic as needed)
        await self.connection_manager.send_to_connection(
            connection_id,
            NotificationMessage(
                type="unsubscribed",
                title="Unsubscribed",
                message=f"Unsubscribed from {channel}",
                data={"channel": channel}
            )
        )
    
    async def _handle_typing(self, connection_id: str, user_id: str, message: dict):
        """Handle typing indicators"""
        # Broadcast typing indicator to relevant users
        await self.connection_manager.broadcast_to_users(
            message.get("recipients", []),
            NotificationMessage(
                type="typing",
                title="Typing",
                message=f"{user_id} is typing...",
                data={"user_id": user_id, "is_typing": True}
            ),
            exclude_user=user_id
        )
    
    async def _handle_chat_message(self, connection_id: str, user_id: str, message: dict):
        """Handle chat messages"""
        content = message.get("content")
        recipients = message.get("recipients", [])
        
        if not content:
            return
        
        chat_message = NotificationMessage(
            type="chat",
            title="New Message",
            message=content,
            data={
                "sender_id": user_id,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        if recipients:
            await self.connection_manager.broadcast_to_users(recipients, chat_message)
        else:
            await self.connection_manager.broadcast_to_all(chat_message, exclude_user=user_id)


# Message handler instance
message_handler = WebSocketMessageHandler(websocket_manager)


async def send_system_notification(message: str, notification_type: str = "system", target_roles: List[str] = None):
    """Send system-wide notification"""
    notification = NotificationMessage(
        type=notification_type,
        title="System Notification",
        message=message,
        data={"system": True}
    )
    
    if target_roles:
        for role in target_roles:
            await websocket_manager.broadcast_to_role(role, notification)
    else:
        await websocket_manager.broadcast_to_all(notification)


async def send_appointment_notification(user_id: str, appointment_data: dict):
    """Send appointment-related notification"""
    notification = NotificationMessage(
        type="appointment",
        title="Appointment Update",
        message=appointment_data.get("message", "Your appointment has been updated"),
        data=appointment_data
    )
    await websocket_manager.send_personal_message(user_id, notification)


async def send_prescription_notification(user_id: str, prescription_data: dict):
    """Send prescription-related notification"""
    notification = NotificationMessage(
        type="prescription",
        title="Prescription Update",
        message=prescription_data.get("message", "Your prescription has been updated"),
        data=prescription_data
    )
    await websocket_manager.send_personal_message(user_id, notification)


async def send_order_notification(role: str, order_data: dict):
    """Send order-related notification to staff"""
    notification = NotificationMessage(
        type="order",
        title="New Order",
        message=order_data.get("message", "A new order has been placed"),
        data=order_data
    )
    await websocket_manager.broadcast_to_role(role, notification)


async def send_inventory_alert(role: str, inventory_data: dict):
    """Send inventory-related notification"""
    notification = NotificationMessage(
        type="inventory",
        title="Inventory Alert",
        message=inventory_data.get("message", "Inventory alert"),
        data=inventory_data
    )
    await websocket_manager.broadcast_to_role(role, notification)
