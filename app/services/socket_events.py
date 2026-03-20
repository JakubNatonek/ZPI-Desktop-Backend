"""WebSocket event handlers for chat and real-time notifications."""

import socketio

from app.services.websocket_manager import chat_ws_manager


class ChatSocketEvents:
    """Centralized chat WebSocket event handlers."""
    
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
    
    async def on_connect(self, sid: str, environ, auth):
        """Handle new WebSocket connection."""
        # Extract user_id from auth token
        user_id = auth.get("user_id") if auth else None

        if user_id is None:
            return False  # Reject connection if no user_id

        try:
            parsed_user_id = int(user_id)
        except (TypeError, ValueError):
            return False

        chat_ws_manager.connect(sid, parsed_user_id)
        print(f"[CONNECT] User {parsed_user_id} via {sid}")
        return True
    
    async def on_disconnect(self, sid: str):
        """Handle WebSocket disconnection."""
        chat_ws_manager.disconnect(sid)
        print(f"[DISCONNECT] Session {sid}")
    
    async def on_message_sent(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle new message sent event.
        Broadcast to all members of the conversation.
        
        Expected data:
        {
            "conversation_id": int,
            "message_id": int,
            "sender_id": int,
            "content": str,
            "created_at": str
        }
        """
        conversation_id = data.get("conversation_id")
        message_id = data.get("message_id")
        
        # Broadcast to everyone in the conversation room
        await self.sio.emit(
            "message_received",
            {
                "message_id": message_id,
                "sender_id": data.get("sender_id"),
                "conversation_id": conversation_id,
                "content": data.get("content"),
                "created_at": data.get("created_at"),
            },
            room=f"conv_{conversation_id}",
        )
    
    async def on_typing(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle typing indicator event.
        Notify other users in conversation that someone is typing.
        
        Expected data:
        {
            "conversation_id": int,
            "is_typing": bool,
            "user_id": int
        }
        """
        user_id = chat_ws_manager.connection_user.get(sid)
        conversation_id = data.get("conversation_id")
        is_typing = data.get("is_typing", False)
        
        if not user_id or not conversation_id:
            return
        
        # Broadcast to everyone except sender
        await self.sio.emit(
            "user_typing",
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "is_typing": is_typing,
            },
            room=f"conv_{conversation_id}",
            skip_sid=sid,
        )
    
    async def on_message_delivered(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle message delivery acknowledgment.
        
        Expected data:
        {
            "message_id": int,
            "conversation_id": int
        }
        """
        conversation_id = data.get("conversation_id")
        message_id = data.get("message_id")
        
        await self.sio.emit(
            "message_delivered",
            {
                "message_id": message_id,
                "conversation_id": conversation_id,
            },
            room=f"conv_{conversation_id}",
        )
    
    async def on_message_read(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle message read acknowledgment.
        
        Expected data:
        {
            "message_id": int,
            "conversation_id": int
        }
        """
        conversation_id = data.get("conversation_id")
        message_id = data.get("message_id")
        user_id = chat_ws_manager.connection_user.get(sid)
        
        if not user_id:
            return
        
        await self.sio.emit(
            "message_read",
            {
                "message_id": message_id,
                "conversation_id": conversation_id,
                "read_by": user_id,
            },
            room=f"conv_{conversation_id}",
        )
    
    async def on_join_conversation(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle user joining a conversation room.
        User should call this after connecting to start receiving updates.
        
        Expected data:
        {
            "conversation_id": int
        }
        """
        user_id = chat_ws_manager.connection_user.get(sid)
        conversation_id = data.get("conversation_id")
        
        if not user_id or not conversation_id:
            return

        room_name = f"conv_{conversation_id}"
        await self.sio.enter_room(sid, room_name)
        print(f"[JOIN] User {user_id} joined room {room_name}")
        
        # Notify others that user is online in this conversation
        await self.sio.emit(
            "user_online",
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
            },
            room=room_name,
            skip_sid=sid,
        )
    
    async def on_leave_conversation(
        self,
        sid: str,
        data: dict,
    ):
        """
        Handle user leaving a conversation room.
        
        Expected data:
        {
            "conversation_id": int
        }
        """
        user_id = chat_ws_manager.connection_user.get(sid)
        conversation_id = data.get("conversation_id")
        
        if not user_id or not conversation_id:
            return

        room_name = f"conv_{conversation_id}"
        await self.sio.leave_room(sid, room_name)
        print(f"[LEAVE] User {user_id} left room {room_name}")
        
        # Notify others that user went offline in this conversation
        await self.sio.emit(
            "user_offline",
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
            },
            room=room_name,
        )


def create_socket_events(sio: socketio.AsyncServer) -> ChatSocketEvents:
    """Factory function to create and register socket event handlers."""
    events = ChatSocketEvents(sio)
    
    # Register all event handlers
    sio.on("connect")(events.on_connect)
    sio.on("disconnect")(events.on_disconnect)
    sio.on("message_sent")(events.on_message_sent)
    sio.on("typing")(events.on_typing)
    sio.on("message_delivered")(events.on_message_delivered)
    sio.on("message_read")(events.on_message_read)
    sio.on("join_conversation")(events.on_join_conversation)
    sio.on("leave_conversation")(events.on_leave_conversation)
    
    return events
