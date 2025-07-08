"""
WhatsApp Business API service for AI Debt Collection Chatbot
Pure Python implementation using httpx
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WhatsAppMessage:
    to: str
    message_type: str
    content: str
    timestamp: str

@dataclass
class WhatsAppTemplate:
    name: str
    language: str
    components: List[Dict]

class WhatsAppService:
    def __init__(self, access_token: str, phone_number_id: str, verify_token: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("WhatsApp service initialized")
    
    async def send_text_message(self, to: str, message: str) -> bool:
        """Send text message via WhatsApp"""
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp not configured - message not sent")
            return False
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": message}
            }
            
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent to {to}")
                return True
            else:
                logger.error(f"WhatsApp send failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return False
    
    async def send_template_message(self, to: str, template_name: str, language: str = "hi", parameters: List[str] = None) -> bool:
        """Send template message via WhatsApp"""
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp not configured - template message not sent")
            return False
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            template_components = []
            if parameters:
                template_components.append({
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language},
                    "components": template_components
                }
            }
            
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp template message sent to {to}")
                return True
            else:
                logger.error(f"WhatsApp template send failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp template send error: {e}")
            return False
    
    async def send_interactive_message(self, to: str, header: str, body: str, buttons: List[Dict]) -> bool:
        """Send interactive message with buttons"""
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp not configured - interactive message not sent")
            return False
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            interactive_buttons = []
            for i, button in enumerate(buttons[:3]):  # WhatsApp allows max 3 buttons
                interactive_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{i}",
                        "title": button.get("title", f"Option {i+1}")
                    }
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": {"type": "text", "text": header},
                    "body": {"text": body},
                    "action": {"buttons": interactive_buttons}
                }
            }
            
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp interactive message sent to {to}")
                return True
            else:
                logger.error(f"WhatsApp interactive send failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp interactive send error: {e}")
            return False
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[int]:
        """Verify WhatsApp webhook"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return int(challenge)
        else:
            logger.warning("WhatsApp webhook verification failed")
            return None
    
    def parse_webhook_message(self, webhook_data: Dict) -> List[Dict]:
        """Parse incoming webhook message"""
        messages = []
        
        try:
            if webhook_data.get("entry"):
                for entry in webhook_data["entry"]:
                    if "changes" in entry:
                        for change in entry["changes"]:
                            if change.get("field") == "messages" and "messages" in change.get("value", {}):
                                for message in change["value"]["messages"]:
                                    parsed_message = {
                                        "from": message.get("from"),
                                        "id": message.get("id"),
                                        "timestamp": message.get("timestamp"),
                                        "type": message.get("type", "text"),
                                        "content": ""
                                    }
                                    
                                    # Extract content based on message type
                                    if message.get("type") == "text":
                                        parsed_message["content"] = message.get("text", {}).get("body", "")
                                    elif message.get("type") == "interactive":
                                        if "button_reply" in message.get("interactive", {}):
                                            parsed_message["content"] = message["interactive"]["button_reply"].get("title", "")
                                        elif "list_reply" in message.get("interactive", {}):
                                            parsed_message["content"] = message["interactive"]["list_reply"].get("title", "")
                                    
                                    if parsed_message["content"]:
                                        messages.append(parsed_message)
        
        except Exception as e:
            logger.error(f"Failed to parse webhook message: {e}")
        
        return messages
    
    async def get_media_url(self, media_id: str) -> Optional[str]:
        """Get media URL from media ID"""
        if not self.access_token:
            return None
        
        try:
            url = f"{self.base_url}/{media_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("url")
            else:
                logger.error(f"Failed to get media URL: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Media URL error: {e}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("WhatsApp service closed")
