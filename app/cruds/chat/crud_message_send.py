from sqlalchemy.orm import Session
from app.models.chat.model_message import Message
from datetime import datetime, timezone
import json


def save_message(db: Session, conversation_id: int, sender_id: int, content: str) -> Message:
    """
    Save a message. If `content` is a JSON string containing encrypted fields
    (`ciphertext`, `iv`, `wrapped_key`), store those into dedicated columns
    and keep `content` column as plaintext (or None if not provided).
    """
    ciphertext = None
    iv = None
    wrapped_key = None
    plaintext_content = None

    if content is None:
        plaintext_content = None
    else:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and (
                "ciphertext" in parsed or "wrapped_key" in parsed or "iv" in parsed
            ):
                ciphertext = parsed.get("ciphertext")
                iv = parsed.get("iv")
                wrapped_key = parsed.get("wrapped_key") or parsed.get("wrappedKey") or parsed.get("encrypted_aes_key")
                plaintext_content = parsed.get("content") or parsed.get("plaintext") or None
            else:
                plaintext_content = content
        except Exception:
            plaintext_content = content

    msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=plaintext_content,
        ciphertext=ciphertext,
        iv=iv,
        wrapped_key=wrapped_key,
        created_at=datetime.now(timezone.utc),
        is_read=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
