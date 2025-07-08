#!/usr/bin/env python3
"""
System test script for AI Debt Collection Chatbot
Tests all components without external dependencies
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_health_endpoint():
    """Test health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Framework: {data.get('framework', 'FastAPI')}")
                print(f"   Python: {data.get('python_version', '3.11+')}")
                print(f"   Debtors loaded: {data.get('debtors_loaded', 0)}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_chat_api():
    """Test chat API endpoint"""
    print("🤖 Testing chat API...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": "Hello, I need help with my payment",
                    "language": "English",
                    "debtor_id": "AC123456789"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat API working: {data['success']}")
                print(f"   Response: {data['response'][:50]}...")
                print(f"   Language: {data['language']}")
                return True
            else:
                print(f"❌ Chat API failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return False

async def test_debtors_api():
    """Test debtors API endpoint"""
    print("👥 Testing debtors API...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/debtors")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Debtors API working: {data['count']} debtors found")
                for debtor in data['debtors'][:2]:  # Show first 2
                    print(f"   - {debtor['name']}: ₹{debtor['amount']:,.2f}")
                return True
            else:
                print(f"❌ Debtors API failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Debtors API error: {e}")
        return False

async def test_whatsapp_webhook():
    """Test WhatsApp webhook verification"""
    print("📱 Testing WhatsApp webhook...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/whatsapp/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "debt_collection_verify_2024",
                    "hub.challenge": "12345"
                }
            )
            
            if response.status_code == 200:
                print("✅ WhatsApp webhook verification working")
                return True
            else:
                print(f"❌ WhatsApp webhook failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {e}")
        return False

async def test_multilingual_support():
    """Test multilingual support"""
    print("🌐 Testing multilingual support...")
    
    test_messages = [
        {"message": "नमस्ते, मुझे सहायता चाहिए", "language": "Hindi"},
        {"message": "Hello, I need help", "language": "English"},
        {"message": "Payment karna hai", "language": "auto"}
    ]
    
    success_count = 0
    
    for test_msg in test_messages:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/api/chat",
                    json={
                        "message": test_msg["message"],
                        "language": test_msg["language"],
                        "debtor_id": "AC123456789"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {test_msg['language']}: Response generated")
                    success_count += 1
                else:
                    print(f"❌ {test_msg['language']}: Failed")
        except Exception as e:
            print(f"❌ {test_msg['language']}: Error - {e}")
    
    return success_count == len(test_messages)

async def test_analytics():
    """Test analytics endpoint"""
    print("📊 Testing analytics...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/analytics")
            
            if response.status_code == 200:
                data = response.json()
                analytics = data['analytics']
                print(f"✅ Analytics working")
                print(f"   Total debtors: {analytics['total_debtors']}")
                print(f"   Active sessions: {analytics['active_sessions']}")
                print(f"   AI services: XAI={analytics['ai_services']['xai_configured']}, Groq={analytics['ai_services']['groq_configured']}")
                return True
            else:
                print(f"❌ Analytics failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def print_test_results(results):
    """Print test results summary"""
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("-" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("✅ PURE PYTHON SOLUTION - NO EXPRESS.JS OR NODE.JS!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check the logs above.")
    
    print("=" * 50)

async def main():
    """Main test function"""
    print("🧪 AI DEBT COLLECTION CHATBOT - SYSTEM TESTS")
    print("🐍 Pure Python FastAPI Implementation")
    print("❌ NO Express.js | NO Node.js | NO JavaScript Frameworks")
    print("=" * 50)
    print("🔄 Starting comprehensive system tests...")
    print()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    await asyncio.sleep(2)
    
    # Run all tests
    test_results = {
        "Health Check": await test_health_endpoint(),
        "Chat API": await test_chat_api(),
        "Debtors API": await test_debtors_api(),
        "WhatsApp Webhook": await test_whatsapp_webhook(),
        "Multilingual Support": await test_multilingual_support(),
        "Analytics": await test_analytics()
    }
    
    # Print results
    print_test_results(test_results)

if __name__ == "__main__":
    asyncio.run(main())
