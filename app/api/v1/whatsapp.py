from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict
import json

from app.database.database import get_db
from app.database.models import Borrower, DebtAccount, ChatSession, ConversationMessage
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.services.language_service import language_service
from app.schemas.whatsapp import WhatsAppMessageRequest, WhatsAppWebhookVerify
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token") 
    challenge = request.query_params.get("hub.challenge")
    
    result = await whatsapp_service.verify_webhook(mode, token, challenge)
    if result:
        return result
    else:
        raise HTTPException(status_code=403, detail="Webhook verification failed")

@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle incoming WhatsApp webhook"""
    try:
        webhook_data = await request.json()
        logger.info(f"WhatsApp webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Process webhook
        await process_whatsapp_webhook(webhook_data, db)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {"status": "error"}

async def process_whatsapp_webhook(webhook_data: Dict, db: AsyncSession):
    """Process WhatsApp webhook data"""
    try:
        if not webhook_data.get("entry"):
            return
        
        for entry in webhook_data["entry"]:
            if "changes" not in entry:
                continue
                
            for change in entry["changes"]:
                if change.get("field") != "messages":
                    continue
                    
                value = change.get("value", {})
                
                # Process incoming messages
                if "messages" in value:
                    for message in value["messages"]:
                        await handle_incoming_message(message, db)
                
                # Process message status updates
                if "statuses" in value:
                    for status in value["statuses"]:
                        await handle_message_status(status, db)
                        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")

async def handle_incoming_message(message: Dict, db: AsyncSession):
    """Handle incoming WhatsApp message"""
    try:
        from_number = message.get("from")
        message_id = message.get("id")
        message_type = message.get("type")
        
        if message_type == "text":
            text_content = message["text"]["body"]
            await process_text_message(from_number, text_content, message_id, db)
        elif message_type == "interactive":
            await process_interactive_message(from_number, message["interactive"], message_id, db)
            
    except Exception as e:
        logger.error(f"Message handling error: {e}")

async def process_text_message(from_number: str, text: str, message_id: str, db: AsyncSession):
    """Process incoming text message"""
    try:
        # Find or create borrower and session
        borrower = await find_borrower_by_phone(from_number, db)
        if not borrower:
            # Send error message
            await whatsapp_service.send_message(
                from_number,
                "Sorry, we couldn't find your account. Please contact customer service."
            )
            return
        
        # Get or create chat session
        session = await get_or_create_whatsapp_session(borrower.id, from_number, db)
        
        # Get debt account info
        debt_result = await db.execute(
            select(DebtAccount).where(DebtAccount.borrower_id == borrower.id)
        )
        debt_account = debt_result.scalar_one_or_none()
        
        if not debt_account:
            await whatsapp_service.send_message(
                from_number,
                "No debt account found. Please contact customer service."
            )
            return
        
        # Detect language
        detected_language = await language_service.detect_language(text)
        
        # Save user message
        user_message = ConversationMessage(
            session_id=session.id,
            sender_type="user",
            content=text,
            original_language=detected_language,
            metadata={"whatsapp_message_id": message_id}
        )
        db.add(user_message)
        
        # Get conversation history
        history_result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session.id)
            .order_by(ConversationMessage.sent_at.desc())
            .limit(10)
        )
        conversation_history = [
            {
                "sender_type": msg.sender_type,
                "content": msg.content,
                "sent_at": msg.sent_at.isoformat()
            }
            for msg in history_result.scalars().all()
        ]
        
        # Generate AI response
        borrower_info = {
            "name": borrower.name,
            "phone": borrower.phone,
            "preferred_language": borrower.preferred_language
        }
        
        debt_info = {
            "account_number": debt_account.account_number,
            "outstanding_amount": float(debt_account.outstanding_amount),
            "due_date": debt_account.due_date.isoformat(),
            "status": debt_account.status
        }
        
        ai_response = await ai_service.generate_response(
            message=text,
            borrower_info=borrower_info,
            debt_info=debt_info,
            conversation_history=conversation_history,
            detected_language=detected_language
        )
        
        # Send AI response via WhatsApp
        send_result = await whatsapp_service.send_message(
            from_number,
            ai_response['content']
        )
        
        # Save bot response
        bot_message = ConversationMessage(
            session_id=session.id,
            sender_type="bot",
            content=ai_response['content'],
            original_language=detected_language,
            metadata={
                "intent": ai_response.get('intent'),
                "entities": ai_response.get('entities'),
                "whatsapp_message_id": send_result.get('message_id')
            }
        )
        db.add(bot_message)
        
        # Send interactive buttons if appropriate
        if ai_response.get('suggested_actions'):
            await send_interactive_buttons(from_number, ai_response['suggested_actions'])
        
        await db.commit()
        
    except Exception as e:
        logger.error(f"Text message processing error: {e}")
        await db.rollback()

async def find_borrower_by_phone(phone: str, db: AsyncSession) -> Borrower:
    """Find borrower by phone number"""
    # Format phone number
    formatted_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
    if formatted_phone.startswith('91') and len(formatted_phone) == 12:
        formatted_phone = formatted_phone[2:]  # Remove country code
    
    result = await db.execute(
        select(Borrower).where(Borrower.phone.like(f"%{formatted_phone}"))
    )
    return result.scalar_one_or_none()

async def get_or_create_whatsapp_session(borrower_id: str, phone: str, db: AsyncSession) -> ChatSession:
    """Get or create WhatsApp chat session"""
    # Check for existing active session
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.borrower_id == borrower_id,
            ChatSession.platform == "whatsapp",
            ChatSession.status == "active"
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        # Create new session
        session = ChatSession(
            borrower_id=borrower_id,
            session_token=f"whatsapp_{phone}_{int(datetime.now().timestamp())}",
            platform="whatsapp",
            language="hi",  # Default to Hindi
            metadata={"phone": phone}
        )
        db.add(session)
        await db.flush()  # Get the ID
    
    return session

async def send_interactive_buttons(phone: str, suggested_actions: list):
    """Send interactive buttons for suggested actions"""
    try:
        action_buttons = []
        
        action_map = {
            'show_payment_options': {'id': 'payment_options', 'title': 'Payment Options'},
            'offer_emi_plan': {'id': 'emi_plan', 'title': 'EMI Plan'},
            'discuss_settlement': {'id': 'settlement', 'title': 'Settlement'},
            'escalate_to_agent': {'id': 'agent', 'title': 'Talk to Agent'}
        }
        
        for action in suggested_actions[:3]:  # Max 3 buttons
            if action in action_map:
                action_buttons.append({
                    "type": "reply",
                    "reply": action_map[action]
                })
        
        if action_buttons:
            await whatsapp_service.send_interactive_message(
                phone,
                "How would you like to proceed?",
                action_buttons
            )
            
    except Exception as e:
        logger.error(f"Interactive buttons error: {e}")

async def process_interactive_message(from_number: str, interactive: Dict, message_id: str, db: AsyncSession):
    """Process interactive button response"""
    try:
        if interactive.get("type") == "button_reply":
            button_id = interactive["button_reply"]["id"]
            button_title = interactive["button_reply"]["title"]
            
            # Process button response
            response_text = await handle_button_response(button_id, from_number, db)
            
            if response_text:
                await whatsapp_service.send_message(from_number, response_text)
                
    except Exception as e:
        logger.error(f"Interactive message processing error: {e}")

async def handle_button_response(button_id: str, phone: str, db: AsyncSession) -> str:
    """Handle button response and return appropriate message"""
    responses = {
        'payment_options': "Here are your payment options:\n1. Online Payment\n2. Bank Transfer\n3. UPI Payment\n\nReply with the option number you prefer.",
        'emi_plan': "We can offer you an EMI plan:\n- 6 months: ₹4,500/month\n- 12 months: ₹2,300/month\n- 18 months: ₹1,600/month\n\nWhich plan interests you?",
        'settlement': "We can discuss a one-time settlement offer. Our agent will call you within 24 hours to discuss the details.",
        'agent': "Connecting you to our customer service agent. Please wait while we transfer your call."
    }
    
    return responses.get(button_id, "Thank you for your response. Our team will get back to you soon.")

async def handle_message_status(status: Dict, db: AsyncSession):
    """Handle message delivery status updates"""
    try:
        message_id = status.get("id")
        status_type = status.get("status")  # sent, delivered, read, failed
        
        # Update message status in database
        result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.metadata['whatsapp_message_id'].astext == message_id)
        )
        message = result.scalar_one_or_none()
        
        if message:
            if status_type == "delivered":
                message.delivered_at = datetime.utcnow()
            elif status_type == "read":
                message.read_at = datetime.utcnow()
            
            await db.commit()
            
    except Exception as e:
        logger.error(f"Status update error: {e}")

@router.post("/send")
async def send_whatsapp_message(
    request: WhatsAppMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send WhatsApp message manually"""
    try:
        result = await whatsapp_service.send_message(
            request.to,
            request.message,
            request.message_type
        )
        
        return {"success": result["success"], "message_id": result.get("message_id")}
        
    except Exception as e:
        logger.error(f"Manual WhatsApp send error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")
