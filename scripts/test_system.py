#!/usr/bin/env python3
"""
Complete system test for DebtBot AI
"""
import asyncio
import httpx
import json
import sys
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []

    async def test_health_endpoint(self):
        """Test health check endpoint"""
        logger.info("🏥 Testing health endpoint...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Health check passed: {data.get('status')}")
                    self.test_results.append(("Health Check", True, "OK"))
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status_code}")
                    self.test_results.append(("Health Check", False, f"Status: {response.status_code}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            self.test_results.append(("Health Check", False, str(e)))
            return False

    async def test_chat_session_creation(self):
        """Test chat session creation"""
        logger.info("💬 Testing chat session creation...")
        try:
            session_data = {
                "phone": "917439330282",
                "account_number": "AC123456789",
                "platform": "web",
                "language": "hi"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat/session",
                    json=session_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("session_token"):
                        logger.info(f"✅ Chat session created: {data['session_token'][:16]}...")
                        self.test_results.append(("Chat Session", True, "Created successfully"))
                        return data["session_token"]
                    else:
                        logger.error(f"❌ Chat session creation failed: {data}")
                        self.test_results.append(("Chat Session", False, "Invalid response"))
                        return None
                else:
                    logger.error(f"❌ Chat session failed: {response.status_code}")
                    self.test_results.append(("Chat Session", False, f"Status: {response.status_code}"))
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Chat session error: {e}")
            self.test_results.append(("Chat Session", False, str(e)))
            return None

    async def test_chat_message(self, session_token):
        """Test sending a chat message"""
        if not session_token:
            return False
            
        logger.info("📝 Testing chat message...")
        try:
            message_data = {
                "session_token": session_token,
                "message": "मुझे अपना बकाया राशि जानना है",
                "language": "hi"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat/message",
                    json=message_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("response"):
                        logger.info(f"✅ AI response received: {data['response'][:50]}...")
                        logger.info(f"   Language: {data.get('language')}")
                        logger.info(f"   Intent: {data.get('intent')}")
                        self.test_results.append(("Chat Message", True, "AI response generated"))
                        return True
                    else:
                        logger.error(f"❌ Chat message failed: {data}")
                        self.test_results.append(("Chat Message", False, "No AI response"))
                        return False
                else:
                    logger.error(f"❌ Chat message failed: {response.status_code}")
                    self.test_results.append(("Chat Message", False, f"Status: {response.status_code}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Chat message error: {e}")
            self.test_results.append(("Chat Message", False, str(e)))
            return False

    async def test_whatsapp_webhook_verification(self):
        """Test WhatsApp webhook verification"""
        logger.info("📱 Testing WhatsApp webhook verification...")
        try:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
                "hub.challenge": "test_challenge_123"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/whatsapp/webhook",
                    params=params
                )
                
                if response.status_code == 200 and response.text == "test_challenge_123":
                    logger.info("✅ WhatsApp webhook verification passed")
                    self.test_results.append(("WhatsApp Webhook", True, "Verification successful"))
                    return True
                else:
                    logger.error(f"❌ WhatsApp webhook verification failed: {response.status_code}")
                    self.test_results.append(("WhatsApp Webhook", False, f"Status: {response.status_code}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ WhatsApp webhook error: {e}")
            self.test_results.append(("WhatsApp Webhook", False, str(e)))
            return False

    async def test_language_detection(self):
        """Test language detection service"""
        logger.info("🌐 Testing language detection...")
        try:
            from app.services.language_service import language_service
            
            test_texts = [
                ("Hello, how are you?", "en"),
                ("नमस्ते, आप कैसे हैं?", "hi"),
                ("मराठी भाषा", "mr"),
                ("Hi, main acha hun", "en-IN")
            ]
            
            all_passed = True
            for text, expected_lang in test_texts:
                detected = await language_service.detect_language(text)
                if detected == expected_lang:
                    logger.info(f"✅ '{text}' -> {detected}")
                else:
                    logger.warning(f"⚠️ '{text}' -> {detected} (expected {expected_lang})")
                    all_passed = False
            
            if all_passed:
                self.test_results.append(("Language Detection", True, "All tests passed"))
            else:
                self.test_results.append(("Language Detection", False, "Some tests failed"))
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Language detection error: {e}")
            self.test_results.append(("Language Detection", False, str(e)))
            return False

    def print_test_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*50)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} {test_name}: {details}")
            if success:
                passed += 1
        
        logger.info("="*50)
        logger.info(f"📈 Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! System is ready for production.")
            return True
        else:
            logger.error(f"❌ {total - passed} tests failed. Please check the issues above.")
            return False

    async def run_all_tests(self):
        """Run all system tests"""
        logger.info("🧪 Starting comprehensive system tests...\n")
        
        # Test 1: Health check
        await self.test_health_endpoint()
        
        # Test 2: Language detection
        await self.test_language_detection()
        
        # Test 3: Chat session creation
        session_token = await self.test_chat_session_creation()
        
        # Test 4: Chat message (depends on session)
        await self.test_chat_message(session_token)
        
        # Test 5: WhatsApp webhook
        await self.test_whatsapp_webhook_verification()
        
        # Print summary
        return self.print_test_summary()

async def main():
    """Main test function"""
    tester = SystemTester()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:8000/health", timeout=5.0)
    except Exception:
        logger.error("❌ Server is not running!")
        logger.info("Please start the server first:")
        logger.info("   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # Run tests
    success = await tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
