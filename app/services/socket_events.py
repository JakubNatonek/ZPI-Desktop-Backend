"""WebSocket event handlers for chat and real-time notifications."""

from http.cookies import SimpleCookie

import socketio
from jose import ExpiredSignatureError, JWTError

from app.auth.jwt_utils import decode_access_token
from app.core.database import SessionLocal
from app.cruds.crud_user import get_user_by_id
from app.services.websocket_manager import chat_ws_manager


def _extract_token_from_environ(environ: dict) -> str | None:
    """Extract access_token from HTTP cookies sent during WebSocket handshake."""
    cookie_header = environ.get("HTTP_COOKIE", "")
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    try:
        cookie.load(cookie_header)
    except Exception:
        return None

    morsel = cookie.get("access_token")
    return morsel.value if morsel else None


def _authenticate_ws_connection(environ: dict, auth: dict | None) -> int | None:
    """
    Authenticate a WebSocket connection using JWT.

    Token resolution order:
      1. ``access_token`` httpOnly cookie (sent automatically by the browser)
      2. ``auth.token`` field provided by the Socket.IO client

    Returns the verified ``user_id`` or ``None`` if authentication fails.
    """

    # 1) Try cookie first (preferred — httpOnly, automatic)
    token = _extract_token_from_environ(environ)

    # 2) Fallback: client-supplied token in auth payload
    if not token and auth:
        token = auth.get("token")

    if not token:
        print("[WS AUTH] No access_token found in cookies or auth payload")
        return None

    # 3) Decode & validate JWT
    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        print("[WS AUTH] Access token expired")
        return None
    except JWTError as exc:
        print(f"[WS AUTH] Invalid access token: {exc}")
        return None

    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None or role is None:
        print("[WS AUTH] Token payload missing user_id or role")
        return None

    # 4) Verify user exists in the database
    db = SessionLocal()
    try:
        user = get_user_by_id(db, int(user_id))
        if user is None:
            print(f"[WS AUTH] User {user_id} not found in database")
            return None

        # Optional: verify role hasn't changed since token was issued
        user_role_value = user.role.name if user.role else str(user.role)
        if user_role_value != str(role):
            print(f"[WS AUTH] Token role mismatch for user {user_id}")
            return None
    finally:
        db.close()

    return int(user_id)


class ChatSocketEvents:
    """Centralized chat WebSocket event handlers."""
    
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
    
    async def on_connect(self, sid: str, environ, auth):
        """
        Handle new WebSocket connection.

        Authenticates via JWT token extracted from httpOnly cookie or
        the auth.token field. Rejects connections without a valid token.
        """
        user_id = _authenticate_ws_connection(environ, auth)

        if user_id is None:
            print(f"[CONNECT] Rejected unauthenticated connection (sid: {sid})")
            return False  # Reject — Socket.IO will disconnect the client

        chat_ws_manager.connect(sid, user_id)
        print(f"[CONNECT] User {user_id} authenticated via JWT (sid: {sid})")
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