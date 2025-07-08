from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os
import httpx
import asyncpg
import aioredis
from pydantic import BaseModel
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Debt Collection Chatbot",
    description="Multilingual debt collection chatbot for India - Pure Python",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration from environment variables
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://debt_user:debt_password@localhost:5432/debt_collection_db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "debt_collection_verify_2024")
    SUPABASE_URL = os.getenv("SUPABASE_SUPABASE_NEXT_PUBLIC_SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_NEXT_PUBLIC_SUPABASE_ANON_KEY_ANON_KEY", "")
    # Python-specific configurations
    PYTHON_ENV = os.getenv("PYTHON_ENV", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()

# Data models
class ChatMessage(BaseModel):
    message: str
    language: str = "auto"
    debtor_id: str = "default"

class DebtorInfo(BaseModel):
    name: str
    phone: str
    amount: float
    due_date: str
    language: str = "Hindi"

# In-memory storage (will be replaced with database)
active_connections: Dict[str, WebSocket] = {}
chat_sessions: Dict[str, List[Dict]] = {}
debtors_db = {
    "AC123456789": DebtorInfo(
        name="राजेश कुमार",
        phone="+919876543210", 
        amount=25000.0,
        due_date="2024-01-15",
        language="Hindi"
    ),
    "AC987654321": DebtorInfo(
        name="प्रिया शर्मा",
        phone="+919876543211",
        amount=18500.0, 
        due_date="2024-01-20",
        language="Hindi"
    ),
    "AC555666777": DebtorInfo(
        name="अमित पटेल",
        phone="+919876543212",
        amount=35000.0, 
        due_date="2024-01-25",
        language="Hindi"
    )
}

# AI Service
class AIService:
    def __init__(self):
        self.xai_api_key = config.XAI_API_KEY
        self.groq_api_key = config.GROQ_API_KEY
    
    async def generate_response(self, message: str, debtor_info: DebtorInfo, language: str = "Hindi") -> str:
        """Generate AI response using available APIs"""
        
        # Create context-aware prompt
        system_prompt = f"""
        You are a professional, empathetic debt collection AI assistant for India.
        
        IMPORTANT GUIDELINES:
        - Always be respectful, professional, and compliant with RBI guidelines
        - Never be aggressive, threatening, or harassing
        - Focus on finding mutually beneficial solutions
        - Offer payment plans, EMI options, and settlement discussions
        - Be culturally sensitive and appropriate for Indian context
        - Use {language} language primarily
        - Keep responses concise and helpful
        
        Current debtor: {debtor_info.name}
        Outstanding amount: ₹{debtor_info.amount:,.2f}
        Due date: {debtor_info.due_date}
        
        COMPLIANCE REQUIREMENTS:
        - Never threaten legal action unless specifically authorized
        - Always offer reasonable payment options
        - Respect if customer requests to stop communication
        - Maintain professional tone throughout
        - Provide clear next steps
        
        Respond to: "{message}"
        """
        
        # Try XAI Grok first
        if self.xai_api_key:
            try:
                response = await self._call_xai_api(system_prompt, message)
                if response:
                    return response
            except Exception as e:
                logger.error(f"XAI API error: {e}")
        
        # Fallback to Groq
        if self.groq_api_key:
            try:
                response = await self._call_groq_api(system_prompt, message)
                if response:
                    return response
            except Exception as e:
                logger.error(f"Groq API error: {e}")
        
        # Fallback to rule-based responses
        return self._get_fallback_response(message, debtor_info, language)
    
    async def _call_xai_api(self, system_prompt: str, message: str) -> Optional[str]:
        """Call XAI Grok API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.xai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"XAI API call failed: {e}")
        return None
    
    async def _call_groq_api(self, system_prompt: str, message: str) -> Optional[str]:
        """Call Groq API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
        return None
    
    def _get_fallback_response(self, message: str, debtor_info: DebtorInfo, language: str) -> str:
        """Generate rule-based fallback response"""
        message_lower = message.lower()
        
        responses = {
            "Hindi": {
                "greeting": f"नमस्ते {debtor_info.name}! मैं आपकी ऋण वसूली में सहायता के लिए यहाँ हूँ। आपकी बकाया राशि ₹{debtor_info.amount:,.2f} है। क्या आप आज कुछ भुगतान कर सकते हैं?",
                "payment": f"धन्यवाद! आपका भुगतान प्राप्त हो गया है। क्या आप बाकी राशि ₹{debtor_info.amount:,.2f} के लिए EMI की व्यवस्था करना चाहेंगे? हम 3, 6, या 12 महीने का प्लान दे सकते हैं।",
                "help": f"मैं आपकी सहायता कर सकता हूँ। आपके पास ये विकल्प हैं:\n1. तुरंत भुगतान करें\n2. EMI प्लान बनाएं\n3. खाता विवरण देखें\n4. ग्राहक सेवा से बात करें\n\nआपकी बकाया राशि: ₹{debtor_info.amount:,.2f}",
                "emi": f"EMI प्लान के लिए:\n• 3 महीने: ₹{debtor_info.amount/3:,.2f} प्रति महीना\n• 6 महीने: ₹{debtor_info.amount/6:,.2f} प्रति महीना\n• 12 महीने: ₹{debtor_info.amount/12:,.2f} प्रति महीना\n\nकौन सा प्लान आपको सूट करता है?",
                "default": f"मैं समझ गया। आपकी बकाया राशि ₹{debtor_info.amount:,.2f} है। हम आपकी स्थिति समझते हैं। क्या आप आज कम से कम ₹{debtor_info.amount*0.1:,.2f} का भुगतान कर सकते हैं?"
            },
            "English": {
                "greeting": f"Hello {debtor_info.name}! I'm here to help with your debt recovery. Your outstanding amount is ₹{debtor_info.amount:,.2f}. Can you make a payment today?",
                "payment": f"Thank you for your payment! Would you like to set up an EMI plan for the remaining amount of ₹{debtor_info.amount:,.2f}? We offer 3, 6, or 12-month plans.",
                "help": f"I can help you with:\n1. Make immediate payment\n2. Set up EMI plan\n3. View account details\n4. Speak to customer service\n\nYour outstanding amount: ₹{debtor_info.amount:,.2f}",
                "emi": f"EMI Plan Options:\n• 3 months: ₹{debtor_info.amount/3:,.2f} per month\n• 6 months: ₹{debtor_info.amount/6:,.2f} per month\n• 12 months: ₹{debtor_info.amount/12:,.2f} per month\n\nWhich plan works for you?",
                "default": f"I understand your situation. Your outstanding amount is ₹{debtor_info.amount:,.2f}. We want to help you. Can you make at least ₹{debtor_info.amount*0.1:,.2f} payment today?"
            }
        }
        
        lang_responses = responses.get(language, responses["Hindi"])
        
        if any(word in message_lower for word in ["hello", "hi", "नमस्ते", "हैलो", "start"]):
            return lang_responses["greeting"]
        elif any(word in message_lower for word in ["payment", "pay", "भुगतान", "पैसे", "paid"]):
            return lang_responses["payment"]
        elif any(word in message_lower for word in ["help", "सहायता", "मदद", "option"]):
            return lang_responses["help"]
        elif any(word in message_lower for word in ["emi", "installment", "किस्त", "plan"]):
            return lang_responses["emi"]
        else:
            return lang_responses["default"]

# Initialize AI service
ai_service = AIService()

# Language detection service
class LanguageService:
    def detect_language(self, text: str) -> str:
        """Simple language detection based on script"""
        # Check for Devanagari script (Hindi/Marathi)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "Hindi"
        # Check for Tamil script
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):
            return "Tamil"
        # Check for Telugu script
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):
            return "Telugu"
        # Check for Gujarati script
        elif any('\u0A80' <= char <= '\u0AFF' for char in text):
            return "Gujarati"
        # Default to English
        else:
            return "English"

language_service = LanguageService()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "framework": "FastAPI (Pure Python)",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "runtime": "Python asyncio",
        "no_nodejs": True,
        "no_express": True,
        "services": {
            "ai_xai": "configured" if config.XAI_API_KEY else "not_configured",
            "ai_groq": "configured" if config.GROQ_API_KEY else "not_configured",
            "whatsapp": "configured" if config.WHATSAPP_ACCESS_TOKEN else "not_configured",
            "supabase": "configured" if config.SUPABASE_URL else "not_configured",
            "database": "postgresql" if config.DATABASE_URL else "not_configured",
            "redis": "configured" if config.REDIS_URL else "not_configured"
        },
        "debtors_loaded": len(debtors_db),
        "active_sessions": len(active_connections)
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    # Initialize session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Send welcome message
    welcome_msg = {
        "id": str(uuid.uuid4()),
        "type": "bot",
        "content": "नमस्ते! मैं आपकी ऋण वसूली में सहायता के लिए यहाँ हूँ। कृपया अपना खाता नंबर या नाम बताएं।",
        "language": "Hindi",
        "timestamp": datetime.now().isoformat()
    }
    
    await websocket.send_text(json.dumps({
        "type": "message",
        "data": welcome_msg
    }))
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            user_message = message_data.get("message", "")
            debtor_id = message_data.get("debtor_id", "AC123456789")
            language = message_data.get("language", "auto")
            
            # Get debtor info
            debtor_info = debtors_db.get(debtor_id, debtors_db["AC123456789"])
            
            # Detect language if auto
            if language == "auto":
                language = language_service.detect_language(user_message)
            
            # Save user message
            user_msg = {
                "id": str(uuid.uuid4()),
                "type": "user",
                "content": user_message,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            chat_sessions[session_id].append(user_msg)
            
            # Generate AI response
            try:
                ai_response = await ai_service.generate_response(
                    user_message, debtor_info, language
                )
                
                # Save bot message
                bot_msg = {
                    "id": str(uuid.uuid4()),
                    "type": "bot",
                    "content": ai_response,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
                chat_sessions[session_id].append(bot_msg)
                
                # Send response
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "data": bot_msg
                }))
                
            except Exception as e:
                logger.error(f"AI response error: {e}")
                error_msg = {
                    "id": str(uuid.uuid4()),
                    "type": "bot",
                    "content": "मुझे खुशी होगी आपकी सहायता करने में। कृपया फिर से प्रयास करें। / I'd be happy to help you. Please try again.",
                    "language": "Hindi",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps({
                    "type": "message", 
                    "data": error_msg
                }))
                
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """REST API endpoint for chat"""
    try:
        # Get debtor info
        debtor_info = debtors_db.get(chat_message.debtor_id, debtors_db["AC123456789"])
        
        # Detect language if auto
        language = chat_message.language
        if language == "auto":
            language = language_service.detect_language(chat_message.message)
        
        # Generate response
        response = await ai_service.generate_response(
            chat_message.message, debtor_info, language
        )
        
        return {
            "success": True,
            "response": response,
            "language": language,
            "debtor": {
                "id": chat_message.debtor_id,
                "name": debtor_info.name,
                "amount": debtor_info.amount,
                "due_date": debtor_info.due_date
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/api/debtors")
async def get_debtors():
    """Get list of debtors"""
    return {
        "success": True,
        "count": len(debtors_db),
        "debtors": [
            {
                "id": debtor_id,
                "name": info.name,
                "amount": info.amount,
                "due_date": info.due_date,
                "phone": info.phone,
                "language": info.language
            }
            for debtor_id, info in debtors_db.items()
        ]
    }

@app.get("/api/debtor/{debtor_id}")
async def get_debtor(debtor_id: str):
    """Get specific debtor information"""
    if debtor_id not in debtors_db:
        raise HTTPException(status_code=404, detail="Debtor not found")
    
    info = debtors_db[debtor_id]
    return {
        "success": True,
        "debtor": {
            "id": debtor_id,
            "name": info.name,
            "amount": info.amount,
            "due_date": info.due_date,
            "phone": info.phone,
            "language": info.language
        }
    }

# WhatsApp webhook endpoints
@app.get("/api/whatsapp/webhook")
async def verify_whatsapp_webhook(request: Request):
    """Verify WhatsApp webhook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"WhatsApp webhook verification: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return int(challenge)
    else:
        logger.warning("WhatsApp webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/api/whatsapp/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.json()
        logger.info(f"WhatsApp webhook received: {json.dumps(body, indent=2)}")
        
        # Process webhook data
        if body.get("entry"):
            for entry in body["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages" and "messages" in change.get("value", {}):
                            for message in change["value"]["messages"]:
                                await process_whatsapp_message(message)
        
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return {"status": "error", "message": str(e)}

async def process_whatsapp_message(message: Dict):
    """Process incoming WhatsApp message"""
    try:
        from_number = message.get("from")
        message_text = message.get("text", {}).get("body", "")
        
        if not message_text:
            return
        
        logger.info(f"Processing WhatsApp message from {from_number}: {message_text}")
        
        # Find debtor by phone number
        debtor_info = None
        debtor_id = None
        
        for did, info in debtors_db.items():
            if from_number in info.phone.replace("+", "").replace("-", "").replace(" ", ""):
                debtor_info = info
                debtor_id = did
                break
        
        if not debtor_info:
            # Send error message
            await send_whatsapp_message(
                from_number,
                "नमस्ते! हमें आपका खाता नहीं मिला। कृपया ग्राहक सेवा से संपर्क करें। / Hello! We couldn't find your account. Please contact customer service."
            )
            return
        
        # Detect language
        language = language_service.detect_language(message_text)
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message_text, debtor_info, language
        )
        
        # Send response via WhatsApp
        await send_whatsapp_message(from_number, ai_response)
        
    except Exception as e:
        logger.error(f"WhatsApp message processing error: {e}")

async def send_whatsapp_message(to: str, message: str):
    """Send WhatsApp message"""
    if not config.WHATSAPP_ACCESS_TOKEN or not config.WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp not configured - message not sent")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://graph.facebook.com/v18.0/{config.WHATSAPP_PHONE_NUMBER_ID}/messages",
                headers={
                    "Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "text": {"body": message}
                }
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent to {to}")
                return True
            else:
                logger.error(f"WhatsApp send failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return False

# Analytics endpoint
@app.get("/api/analytics")
async def get_analytics():
    """Get system analytics"""
    total_messages = sum(len(session) for session in chat_sessions.values())
    
    return {
        "success": True,
        "analytics": {
            "total_debtors": len(debtors_db),
            "active_sessions": len(active_connections),
            "total_chat_sessions": len(chat_sessions),
            "total_messages": total_messages,
            "system_uptime": datetime.now().isoformat(),
            "ai_services": {
                "xai_configured": bool(config.XAI_API_KEY),
                "groq_configured": bool(config.GROQ_API_KEY)
            },
            "whatsapp_configured": bool(config.WHATSAPP_ACCESS_TOKEN)
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting AI Debt Collection Chatbot (Pure Python)")
    print("🌐 Access at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
