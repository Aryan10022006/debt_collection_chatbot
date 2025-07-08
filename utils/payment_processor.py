"""
Payment processing utilities for AI Debt Collection Chatbot
Pure Python implementation for handling payment integrations
"""

import asyncio
import httpx
import json
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class PaymentRequest:
    debtor_id: str
    amount: float
    currency: str = "INR"
    description: str = ""
    callback_url: str = ""

@dataclass
class PaymentResponse:
    payment_id: str
    status: PaymentStatus
    amount: float
    currency: str
    payment_url: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: str = ""

class RazorpayProcessor:
    """Razorpay payment processor for Indian market"""
    
    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret
        self.base_url = "https://api.razorpay.com/v1"
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(
            auth=(self.key_id, self.key_secret),
            timeout=30.0
        )
        logger.info("Razorpay processor initialized")
    
    async def create_payment_link(self, request: PaymentRequest) -> PaymentResponse:
        """Create payment link for debtor"""
        try:
            payload = {
                "amount": int(request.amount * 100),  # Convert to paise
                "currency": request.currency,
                "description": request.description or f"Payment for debt collection - {request.debtor_id}",
                "customer": {
                    "name": f"Debtor {request.debtor_id}",
                    "contact": "+919999999999",  # Default contact
                    "email": f"debtor{request.debtor_id}@example.com"
                },
                "notify": {
                    "sms": True,
                    "email": False
                },
                "reminder_enable": True,
                "callback_url": request.callback_url,
                "callback_method": "get"
            }
            
            response = await self.client.post(
                f"{self.base_url}/payment_links",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return PaymentResponse(
                    payment_id=data["id"],
                    status=PaymentStatus.PENDING,
                    amount=request.amount,
                    currency=request.currency,
                    payment_url=data["short_url"],
                    created_at=datetime.now().isoformat()
                )
            else:
                logger.error(f"Razorpay payment link creation failed: {response.text}")
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    amount=request.amount,
                    currency=request.currency,
                    created_at=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Razorpay payment link error: {e}")
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                created_at=datetime.now().isoformat()
            )
    
    async def verify_payment(self, payment_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify payment signature"""
        try:
            # Create signature
            message = f"{payment_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                self.key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, razorpay_signature)
            
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return False
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get payment status"""
        try:
            response = await self.client.get(f"{self.base_url}/payment_links/{payment_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "created")
                
                status_mapping = {
                    "created": PaymentStatus.PENDING,
                    "partially_paid": PaymentStatus.PENDING,
                    "paid": PaymentStatus.SUCCESS,
                    "cancelled": PaymentStatus.CANCELLED,
                    "expired": PaymentStatus.FAILED
                }
                
                return status_mapping.get(status, PaymentStatus.PENDING)
            else:
                logger.error(f"Failed to get payment status: {response.text}")
                return PaymentStatus.FAILED
                
        except Exception as e:
            logger.error(f"Payment status error: {e}")
            return PaymentStatus.FAILED
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

class PaymentService:
    """Main payment service that handles multiple processors"""
    
    def __init__(self):
        self.processors = {}
        self.default_processor = None
    
    def add_processor(self, name: str, processor, is_default: bool = False):
        """Add payment processor"""
        self.processors[name] = processor
        if is_default or not self.default_processor:
            self.default_processor = name
        logger.info(f"Payment processor '{name}' added")
    
    async def create_payment_link(self, request: PaymentRequest, processor_name: str = None) -> PaymentResponse:
        """Create payment link using specified or default processor"""
        processor_name = processor_name or self.default_processor
        
        if processor_name not in self.processors:
            logger.error(f"Payment processor '{processor_name}' not found")
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                created_at=datetime.now().isoformat()
            )
        
        processor = self.processors[processor_name]
        return await processor.create_payment_link(request)
    
    async def verify_payment(self, payment_id: str, processor_data: Dict, processor_name: str = None) -> bool:
        """Verify payment using specified or default processor"""
        processor_name = processor_name or self.default_processor
        
        if processor_name not in self.processors:
            logger.error(f"Payment processor '{processor_name}' not found")
            return False
        
        processor = self.processors[processor_name]
        
        if hasattr(processor, 'verify_payment'):
            return await processor.verify_payment(
                payment_id,
                processor_data.get("razorpay_payment_id", ""),
                processor_data.get("razorpay_signature", "")
            )
        
        return False
    
    async def get_payment_status(self, payment_id: str, processor_name: str = None) -> PaymentStatus:
        """Get payment status using specified or default processor"""
        processor_name = processor_name or self.default_processor
        
        if processor_name not in self.processors:
            logger.error(f"Payment processor '{processor_name}' not found")
            return PaymentStatus.FAILED
        
        processor = self.processors[processor_name]
        
        if hasattr(processor, 'get_payment_status'):
            return await processor.get_payment_status(payment_id)
        
        return PaymentStatus.FAILED
    
    def generate_payment_message(self, payment_response: PaymentResponse, debtor_name: str, language: str = "Hindi") -> str:
        """Generate payment message for debtor"""
        messages = {
            "Hindi": {
                "success": f"🎉 {debtor_name}, आपका पेमेंट लिंक तैयार है!\n\n💰 राशि: ₹{payment_response.amount:,.2f}\n🔗 लिंक: {payment_response.payment_url}\n\n⏰ कृपया 24 घंटे के अंदर भुगतान करें।\n📞 सहायता के लिए संपर्क करें।",
                "failed": f"😔 {debtor_name}, पेमेंट लिंक बनाने में समस्या हुई है। कृपया ग्राहक सेवा से संपर्क करें।"
            },
            "English": {
                "success": f"🎉 {debtor_name}, your payment link is ready!\n\n💰 Amount: ₹{payment_response.amount:,.2f}\n🔗 Link: {payment_response.payment_url}\n\n⏰ Please pay within 24 hours.\n📞 Contact us for assistance.",
                "failed": f"😔 {debtor_name}, there was an issue creating your payment link. Please contact customer service."
            }
        }
        
        lang_messages = messages.get(language, messages["Hindi"])
        
        if payment_response.status == PaymentStatus.PENDING and payment_response.payment_url:
            return lang_messages["success"]
        else:
            return lang_messages["failed"]
    
    async def close_all(self):
        """Close all payment processors"""
        for processor in self.processors.values():
            if hasattr(processor, 'close'):
                await processor.close()
        logger.info("All payment processors closed")
