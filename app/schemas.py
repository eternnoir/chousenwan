from pydantic import BaseModel
from typing import Optional

class CreateSessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    message: str
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    # 可以根據需要擴充更多欄位，例如 tokens_used, debug info 等
