from typing import Optional
import socketio

_SIO: Optional[socketio.AsyncServer] = None


def set_sio(sio: socketio.AsyncServer) -> None:
    global _SIO
    _SIO = sio


def get_sio() -> Optional[socketio.AsyncServer]:
    return _SIO
