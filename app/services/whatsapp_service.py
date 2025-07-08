import httpx
import json
from typing import Dict, List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_message(self, to: str, message: str, message_type: str = "text") -> Dict:
        """Send WhatsApp message"""
        try:
            # Format phone number
            formatted_phone = self._format_phone_number(to)
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": message_type,
                "text": {
                    "body": message,
                    "preview_url": False
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"WhatsApp message sent to {formatted_phone}")
                    return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
                else:
                    logger.error(f"WhatsApp send error: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"WhatsApp service error: {e}")
            return {"success": False, "error": str(e)}

    async def send_template_message(self, to: str, template_name: str, parameters: List[str] = None) -> Dict:
        """Send WhatsApp template message"""
        try:
            formatted_phone = self._format_phone_number(to)
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en" if "english" in template_name else "hi"
                    }
                }
            }
            
            if parameters:
                payload["template"]["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                }]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"WhatsApp template error: {e}")
            return {"success": False, "error": str(e)}

    async def send_interactive_message(self, to: str, message: str, buttons: List[Dict]) -> Dict:
        """Send interactive message with buttons"""
        try:
            formatted_phone = self._format_phone_number(to)
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {
                        "buttons": buttons[:3]  # WhatsApp allows max 3 buttons
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                return {"success": response.status_code == 200, "response": response.json()}
                
        except Exception as e:
            logger.error(f"WhatsApp interactive message error: {e}")
            return {"success": False, "error": str(e)}

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for WhatsApp API"""
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, phone))
        
        # Handle Indian phone numbers
        if len(digits) == 10:
            return f"91{digits}"
        elif len(digits) == 12 and digits.startswith("91"):
            return digits
        elif len(digits) == 11 and digits.startswith("0"):
            return f"91{digits[1:]}"
        
        return digits

    async def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify WhatsApp webhook"""
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        return None

    async def process_webhook(self, webhook_data: Dict) -> Dict:
        """Process incoming WhatsApp webhook"""
        try:
            if not webhook_data.get("entry"):
                return {"status": "no_entry"}
            
            for entry in webhook_data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            await self._process_message_change(change["value"])
                        elif change.get("field") == "message_deliveries":
                            await self._process_delivery_status(change["value"])
            
            return {"status": "processed"}
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {"status": "error", "error": str(e)}

    async def _process_message_change(self, value: Dict):
        """Process incoming message"""
        if "messages" in value:
            for message in value["messages"]:
                from_number = message.get("from")
                message_id = message.get("id")
                
                if message.get("type") == "text":
                    text_content = message["text"]["body"]
                    await self._handle_text_message(from_number, text_content, message_id)
                elif message.get("type") == "interactive":
                    await self._handle_interactive_response(from_number, message["interactive"], message_id)

    async def _handle_text_message(self, from_number: str, text: str, message_id: str):
        """Handle incoming text message"""
        logger.info(f"Received message from {from_number}: {text}")
        # This will be handled by the chat service
        
    async def _handle_interactive_response(self, from_number: str, interactive: Dict, message_id: str):
        """Handle interactive button response"""
        if interactive.get("type") == "button_reply":
            button_id = interactive["button_reply"]["id"]
            button_title = interactive["button_reply"]["title"]
            logger.info(f"Button clicked by {from_number}: {button_title} ({button_id})")

    async def _process_delivery_status(self, value: Dict):
        """Process message delivery status"""
        if "statuses" in value:
            for status in value["statuses"]:
                message_id = status.get("id")
                status_type = status.get("status")
                logger.info(f"Message {message_id} status: {status_type}")

# Global instance
whatsapp_service = WhatsAppService()
