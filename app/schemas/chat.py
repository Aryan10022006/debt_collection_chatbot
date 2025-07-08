from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ChatMessageRequest(BaseModel):
    session_token: str
    message: str
    language: Optional[str] = None

class ChatMessageResponse(BaseModel):
    success: bool
    response: str
    language: str
    intent: Optional[str] = None
    suggested_actions: List[str] = []
    session_token: str

class ChatSessionCreate(BaseModel):
    phone: Optional[str] = None
    account_number: Optional[str] = None
    platform: str = "web"
    language: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    success: bool
    messages: List[Dict]
