from pydantic import BaseModel

class SendMessageRequest(BaseModel):
    content: str
