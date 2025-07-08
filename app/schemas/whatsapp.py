from pydantic import BaseModel
from typing import Optional, List, Dict

class WhatsAppMessageRequest(BaseModel):
    to: str
    message: str
    message_type: str = "text"

class WhatsAppWebhookVerify(BaseModel):
    hub_mode: str
    hub_verify_token: str
    hub_challenge: str

class WhatsAppTemplateRequest(BaseModel):
    to: str
    template_name: str
    parameters: Optional[List[str]] = None
