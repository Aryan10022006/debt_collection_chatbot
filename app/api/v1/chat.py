from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
import json
import uuid
from datetime import datetime

from app.database.database import get_db
from app.database.models import ChatSession, ConversationMessage, Borrower, DebtAccount
from app.services.ai_service import ai_service
from app.services.language_service import language_service
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSessionCreate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_token}")
async def websocket_endpoint(websocket: WebSocket, session_token: str, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_token)
    
    try:
        # Get session info
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            await websocket.send_text(json.dumps({"error": "Invalid session token"}))
            return
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            response = await process_chat_message(
                session_token=session_token,
                message=message_data.get("message", ""),
                db=db
            )
            
            # Send response back to client
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        manager.disconnect(session_token)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"error": "Internal server error"}))

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send message to chatbot"""
    return await process_chat_message(
        session_token=request.session_token,
        message=request.message,
        db=db
    )

async def process_chat_message(session_token: str, message: str, db: AsyncSession) -> Dict:
    """Process chat message and generate AI response"""
    try:
        # Get chat session with borrower and debt info
        result = await db.execute(
            select(ChatSession, Borrower, DebtAccount)
            .join(Borrower, ChatSession.borrower_id == Borrower.id)
            .join(DebtAccount, Borrower.id == DebtAccount.borrower_id)
            .where(ChatSession.session_token == session_token)
        )
        session_data = result.first()
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        session, borrower, debt_account = session_data
        
        # Detect language
        detected_language = await language_service.detect_language(message)
        
        # Save user message
        user_message = ConversationMessage(
            session_id=session.id,
            sender_type="user",
            content=message,
            original_language=detected_language
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
            message=message,
            borrower_info=borrower_info,
            debt_info=debt_info,
            conversation_history=conversation_history,
            detected_language=detected_language
        )
        
        # Translate response if needed
        if detected_language != session.language:
            translation = await language_service.translate_text(
                ai_response['content'],
                target_language=detected_language,
                source_language='en'
            )
            ai_response['content'] = translation['translated_text']
        
        # Save bot response
        bot_message = ConversationMessage(
            session_id=session.id,
            sender_type="bot",
            content=ai_response['content'],
            original_language=detected_language,
            metadata={
                "intent": ai_response.get('intent'),
                "entities": ai_response.get('entities'),
                "confidence": ai_response.get('confidence')
            }
        )
        db.add(bot_message)
        
        await db.commit()
        
        return {
            "success": True,
            "response": ai_response['content'],
            "language": detected_language,
            "intent": ai_response.get('intent'),
            "suggested_actions": ai_response.get('suggested_actions', []),
            "session_token": session_token
        }
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.post("/session", response_model=Dict)
async def create_chat_session(
    request: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new chat session"""
    try:
        # Find borrower by phone or account number
        result = await db.execute(
            select(Borrower, DebtAccount)
            .join(DebtAccount, Borrower.id == DebtAccount.borrower_id)
            .where(
                (Borrower.phone == request.phone) | 
                (Borrower.account_number == request.account_number)
            )
        )
        borrower_data = result.first()
        
        if not borrower_data:
            raise HTTPException(status_code=404, detail="Borrower not found")
        
        borrower, debt_account = borrower_data
        
        # Create chat session
        session_token = f"session_{uuid.uuid4().hex[:16]}"
        
        chat_session = ChatSession(
            borrower_id=borrower.id,
            session_token=session_token,
            platform=request.platform,
            language=request.language or borrower.preferred_language,
            metadata={"debt_account_id": str(debt_account.id)}
        )
        
        db.add(chat_session)
        await db.commit()
        
        return {
            "success": True,
            "session_token": session_token,
            "borrower": {
                "name": borrower.name,
                "preferred_language": borrower.preferred_language
            },
            "debt_account": {
                "account_number": debt_account.account_number,
                "outstanding_amount": float(debt_account.outstanding_amount),
                "due_date": debt_account.due_date.isoformat(),
                "status": debt_account.status
            }
        }
        
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.get("/history/{session_token}")
async def get_chat_history(
    session_token: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    try:
        result = await db.execute(
            select(ConversationMessage)
            .join(ChatSession, ConversationMessage.session_id == ChatSession.id)
            .where(ChatSession.session_token == session_token)
            .order_by(ConversationMessage.sent_at.asc())
            .limit(limit)
        )
        
        messages = [
            {
                "id": str(msg.id),
                "sender_type": msg.sender_type,
                "content": msg.content,
                "language": msg.original_language,
                "sent_at": msg.sent_at.isoformat(),
                "metadata": msg.metadata
            }
            for msg in result.scalars().all()
        ]
        
        return {"success": True, "messages": messages}
        
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")
