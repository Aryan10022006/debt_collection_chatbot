import openai
from typing import Dict, List, Optional
import json
import re
from app.core.config import settings
from app.services.language_service import language_service
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        
        self.system_prompts = {
            'hi': """आप एक पेशेवर और सहानुभूतिपूर्ण ऋण वसूली AI सहायक हैं।

महत्वपूर्ण दिशानिर्देश:
- हमेशा सम्मानजनक, पेशेवर और RBI दिशानिर्देशों का अनुपालन करें
- कभी भी आक्रामक, धमकी भरा या परेशान करने वाला न हों
- पारस्परिक रूप से लाभकारी समाधान खोजने पर ध्यान दें
- भुगतान योजना, EMI विकल्प और निपटान चर्चा की पेशकश करें
- भारतीय संदर्भ के लिए सांस्कृतिक रूप से संवेदनशील रहें

आपका लक्ष्य ग्राहक संबंधों को बनाए रखते हुए ऋण वसूली करना है।""",

            'en': """You are a professional, empathetic debt collection AI assistant for India.

IMPORTANT GUIDELINES:
- Always be respectful, professional, and compliant with RBI guidelines
- Never be aggressive, threatening, or harassing
- Focus on finding mutually beneficial solutions
- Offer payment plans, EMI options, and settlement discussions
- Be culturally sensitive and appropriate for Indian context

Your goal is to recover debt while maintaining customer relationships.""",

            'en-IN': """Aap ek professional aur empathetic debt collection AI assistant hain.

IMPORTANT GUIDELINES:
- Hamesha respectful, professional aur RBI compliant rahiye
- Kabhi bhi aggressive ya threatening na baniye
- Mutually beneficial solutions dhundne par focus kariye
- Payment plans, EMI options offer kariye
- Indian context ke liye culturally appropriate rahiye

Aapka goal hai debt recover karna while maintaining good relationships."""
        }

    async def generate_response(
        self, 
        message: str, 
        borrower_info: Dict, 
        debt_info: Dict, 
        conversation_history: List[Dict] = None,
        detected_language: str = 'en'
    ) -> Dict:
        """Generate AI response based on user message and context"""
        try:
            # Get appropriate system prompt
            system_prompt = self._get_system_prompt(detected_language, borrower_info, debt_info)
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role = "user" if msg.get("sender_type") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response using OpenAI
            if settings.OPENAI_API_KEY:
                response = await self._generate_openai_response(messages)
            else:
                response = await self._generate_fallback_response(message, borrower_info, debt_info, detected_language)
            
            # Extract intent and entities
            intent = await self._extract_intent(message, detected_language)
            entities = await self._extract_entities(message)
            
            return {
                'content': response,
                'language': detected_language,
                'intent': intent,
                'entities': entities,
                'confidence': 0.9,
                'suggested_actions': self._get_suggested_actions(intent, debt_info)
            }
            
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return await self._generate_fallback_response(message, borrower_info, debt_info, detected_language)

    def _get_system_prompt(self, language: str, borrower_info: Dict, debt_info: Dict) -> str:
        """Get system prompt for the given language"""
        base_prompt = self.system_prompts.get(language, self.system_prompts['en'])
        
        context = f"""
BORROWER INFORMATION:
- Name: {borrower_info.get('name', 'N/A')}
- Account: {debt_info.get('account_number', 'N/A')}
- Outstanding Amount: ₹{debt_info.get('outstanding_amount', 0):,.2f}
- Due Date: {debt_info.get('due_date', 'N/A')}
- Status: {debt_info.get('status', 'N/A')}

COMPLIANCE REQUIREMENTS:
- Never threaten legal action unless authorized
- Always offer reasonable payment options
- Respect opt-out requests
- Maintain professional tone
- Document all interactions
"""
        
        return f"{base_prompt}\n\n{context}"

    async def _generate_openai_response(self, messages: List[Dict]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_fallback_response(self, message: str, borrower_info: Dict, debt_info: Dict, language: str) -> Dict:
        """Generate fallback response when AI service is unavailable"""
        name = borrower_info.get('name', 'Customer')
        amount = debt_info.get('outstanding_amount', 0)
        
        fallback_responses = {
            'hi': f"नमस्ते {name}! मैं आपकी सहायता करने के लिए यहाँ हूँ। आपका बकाया राशि ₹{amount:,.2f} है। कृपया बताएं कि मैं आपकी कैसे मदद कर सकता हूँ?",
            'en': f"Hello {name}! I'm here to help you. Your outstanding amount is ₹{amount:,.2f}. How can I assist you today?",
            'en-IN': f"Hello {name}! Main aapki help karne ke liye yahan hun. Aapka outstanding amount ₹{amount:,.2f} hai. Kya main aapki koi help kar sakta hun?"
        }
        
        return {
            'content': fallback_responses.get(language, fallback_responses['en']),
            'language': language,
            'intent': 'general_inquiry',
            'entities': {},
            'confidence': 0.5,
            'suggested_actions': ['payment_options', 'emi_plan']
        }

    async def _extract_intent(self, message: str, language: str) -> str:
        """Extract intent from user message"""
        message_lower = message.lower()
        
        intent_keywords = {
            'payment_inquiry': ['payment', 'pay', 'amount', 'due', 'भुगतान', 'पैसा', 'रकम', 'पेमेंट'],
            'payment_promise': ['will pay', 'can pay', 'tomorrow', 'next week', 'भुगतान करूंगा', 'पैसे दूंगा', 'kal', 'agle'],
            'dispute': ['wrong', 'mistake', 'not mine', 'dispute', 'गलत', 'गलती', 'galat'],
            'hardship': ['problem', 'difficulty', 'job loss', 'medical', 'समस्या', 'परेशानी', 'problem'],
            'settlement': ['settle', 'discount', 'reduce', 'समझौता', 'कम', 'settlement'],
            'emi_request': ['installment', 'emi', 'monthly', 'किस्त', 'मासिक', 'monthly']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'general_inquiry'

    async def _extract_entities(self, message: str) -> Dict:
        """Extract entities from user message"""
        entities = {}
        
        # Extract amounts
        amount_pattern = r'₹?(\d+(?:,\d+)*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, message)
        if amounts:
            entities['amounts'] = [float(amount.replace(',', '')) for amount in amounts]
        
        # Extract dates
        date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|tomorrow|next week|अगले सप्ताह|कल|kal'
        dates = re.findall(date_pattern, message, re.IGNORECASE)
        if dates:
            entities['dates'] = dates
        
        # Extract phone numbers
        phone_pattern = r'(\+91|91)?[-\s]?[6-9]\d{9}'
        phones = re.findall(phone_pattern, message)
        if phones:
            entities['phone_numbers'] = phones
        
        return entities

    def _get_suggested_actions(self, intent: str, debt_info: Dict) -> List[str]:
        """Get suggested actions based on intent"""
        action_map = {
            'payment_inquiry': ['show_payment_options', 'calculate_interest', 'payment_history'],
            'payment_promise': ['schedule_followup', 'send_payment_link', 'confirm_amount'],
            'dispute': ['escalate_to_agent', 'request_documents', 'schedule_call'],
            'hardship': ['offer_emi_plan', 'discuss_settlement', 'financial_counseling'],
            'settlement': ['calculate_settlement', 'get_approval', 'generate_offer'],
            'emi_request': ['calculate_emi', 'show_emi_options', 'setup_autopay']
        }
        
        return action_map.get(intent, ['general_assistance', 'escalate_to_agent'])

# Global instance
ai_service = AIService()
