#!/usr/bin/env python3
"""
WhatsApp integration test script
"""
import asyncio
import httpx
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_whatsapp_integration():
    """Test WhatsApp Business API integration"""
    
    logger.info("🧪 Testing WhatsApp Business API integration...")
    
    # Test 1: Verify business account
    logger.info("1. Testing business account verification...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_BUSINESS_ACCOUNT_ID}",
                headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
                params={"fields": "id,name,timezone_offset_min"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Business account verified: {data.get('name')}")
            else:
                logger.error(f"❌ Business account verification failed: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Business account test failed: {e}")
        return False
    
    # Test 2: Send test message (optional - uncomment to test)
    # logger.info("2. Testing message sending...")
    # try:
    #     test_message = {
    #         "messaging_product": "whatsapp",
    #         "to": "917439330282",  # Your WhatsApp number
    #         "type": "text",
    #         "text": {"body": "🤖 DebtBot AI integration test successful!"}
    #     }
    #     
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
    #             headers={
    #                 "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
    #                 "Content-Type": "application/json"
    #             },
    #             json=test_message
    #         )
    #         
    #         if response.status_code == 200:
    #             logger.info("✅ Test message sent successfully")
    #         else:
    #             logger.error(f"❌ Test message failed: {response.text}")
    #             
    # except Exception as e:
    #     logger.error(f"❌ Message test failed: {e}")
    
    logger.info("🎉 WhatsApp integration tests completed!")
    return True

async def main():
    """Main test function"""
    success = await test_whatsapp_integration()
    
    if success:
        logger.info("✅ All tests passed! WhatsApp integration is ready.")
        logger.info("Next steps:")
        logger.info("1. Configure webhook URL in Meta Developer Console")
        logger.info("2. Submit message templates for approval")
        logger.info("3. Start the application and test end-to-end")
    else:
        logger.error("❌ Tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main())
