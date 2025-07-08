import re
from typing import Dict, Tuple, Optional
from googletrans import Translator
from langdetect import detect, DetectorFactory
import asyncio
import logging

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class LanguageService:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'hi': 'Hindi',
            'mr': 'Marathi', 
            'ta': 'Tamil',
            'te': 'Telugu',
            'en': 'English',
            'en-IN': 'Hinglish'
        }
        
        # Language patterns for better detection
        self.language_patterns = {
            'hi': [
                r'[\u0900-\u097F]',  # Devanagari script
                r'\b(है|हैं|का|की|के|में|से|को|पर|और|या|नहीं|भी|तो|ही|जो|वह|यह|मैं|तुम|आप)\b'
            ],
            'mr': [
                r'[\u0900-\u097F]',  # Devanagari script
                r'\b(आहे|होते|करतो|मराठी|महाराष्ट्र|मुंबई)\b'
            ],
            'ta': [
                r'[\u0B80-\u0BFF]',  # Tamil script
                r'\b(இருக்கிறது|செய்கிறது|தமிழ்|நான்|நீங்கள்)\b'
            ],
            'te': [
                r'[\u0C00-\u0C7F]',  # Telugu script
                r'\b(ఉంది|చేస్తున్నాను|తెలుగు|నేను|మీరు)\b'
            ],
            'en-IN': [
                r'\b(hai|hain|kar|kya|aap|main|hum|paisa|rupee|payment|amount)\b',
                r'\b(chahiye|karna|kaise|kyun|abhi|jaldi|please)\b'
            ]
        }

    async def detect_language(self, text: str) -> str:
        """Detect language of input text with enhanced accuracy for Indian languages"""
        try:
            # Clean text
            cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
            
            # Check for script-based patterns first
            for lang_code, patterns in self.language_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        if lang_code == 'hi' and self._is_marathi(text):
                            return 'mr'
                        return lang_code
            
            # Fallback to langdetect
            detected = detect(cleaned_text)
            
            # Map detected language to supported languages
            if detected in self.supported_languages:
                return detected
            elif detected == 'hi':
                return 'hi'
            elif detected == 'mr':
                return 'mr'
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'  # Default fallback

    def _is_marathi(self, text: str) -> bool:
        """Check if Devanagari text is Marathi"""
        marathi_words = ['आहे', 'होते', 'करतो', 'मराठी', 'महाराष्ट्र']
        hindi_words = ['है', 'था', 'करता', 'हिंदी', 'भारत']
        
        marathi_count = sum(1 for word in marathi_words if word in text)
        hindi_count = sum(1 for word in hindi_words if word in text)
        
        return marathi_count > hindi_count

    async def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """Translate text to target language"""
        try:
            if source_language == target_language:
                return {
                    'translated_text': text,
                    'source_language': source_language,
                    'target_language': target_language,
                    'confidence': 1.0
                }
            
            # Handle Hinglish specially
            if target_language == 'en-IN':
                return await self._generate_hinglish(text, source_language)
            
            # Use Google Translate
            result = self.translator.translate(
                text, 
                dest=target_language, 
                src=source_language
            )
            
            return {
                'translated_text': result.text,
                'source_language': result.src,
                'target_language': target_language,
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'translated_text': text,
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'confidence': 0.0
            }

    async def _generate_hinglish(self, text: str, source_language: str) -> Dict:
        """Generate Hinglish text"""
        hinglish_mappings = {
            'payment': 'payment',
            'amount': 'amount',
            'due': 'due',
            'please': 'please',
            'thank you': 'thank you',
            'hello': 'hello',
            'yes': 'haan',
            'no': 'nahi',
            'money': 'paisa',
            'time': 'time',
            'today': 'aaj',
            'tomorrow': 'kal',
            'help': 'help',
            'problem': 'problem'
        }
        
        # Simple Hinglish generation (in production, use more sophisticated methods)
        hinglish_text = text
        for eng, hin in hinglish_mappings.items():
            hinglish_text = re.sub(rf'\b{eng}\b', hin, hinglish_text, flags=re.IGNORECASE)
        
        return {
            'translated_text': hinglish_text,
            'source_language': source_language,
            'target_language': 'en-IN',
            'confidence': 0.8
        }

    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        return self.supported_languages.get(code, 'Unknown')

# Global instance
language_service = LanguageService()
