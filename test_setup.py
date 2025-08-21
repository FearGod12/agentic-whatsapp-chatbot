#!/usr/bin/env python3
"""
Test script to verify the WhatsApp chatbot setup.
Run this script to check if all dependencies and configurations are working.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime

def test_environment():
    """Test if environment variables are properly loaded."""
    print("🔍 Testing environment variables...")

    # Load environment variables
    load_dotenv()

    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER',
        'OPENAI_API_KEY',
        'SECRET_KEY'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_imports():
    """Test if all required packages can be imported."""
    print("\n📦 Testing package imports...")

    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import twilio
        print("✅ Twilio imported successfully")
    except ImportError as e:
        print(f"❌ Twilio import failed: {e}")
        return False

    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False

    return True

def test_config():
    """Test if configuration can be loaded."""
    print("\n⚙️ Testing configuration...")

    try:
        from config import settings
        print("✅ Configuration loaded successfully")
        print(f"   - OpenAI Model: {settings.openai_model}")
        print(f"   - Host: {settings.host}")
        print(f"   - Port: {settings.port}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_services():
    """Test if services can be initialized."""
    print("\n🔧 Testing service initialization...")

    try:
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()
        print("✅ OpenAI service initialized successfully")
    except Exception as e:
        print(f"❌ OpenAI service initialization failed: {e}")
        return False

    try:
        from services.twilio_service import TwilioService
        twilio_service = TwilioService()
        print("✅ Twilio service initialized successfully")
    except Exception as e:
        print(f"❌ Twilio service initialization failed: {e}")
        return False

    try:
        from services.chat_service import ChatService
        chat_service = ChatService()
        print("✅ Chat service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Chat service initialization failed: {e}")
        return False

async def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI API connection...")

    try:
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()

        # Test with a simple message
        test_message = openai_service.create_user_message("Hello, this is a test message.")
        system_message = openai_service.create_system_message()

        response = await openai_service.generate_response(
            messages=[system_message, test_message],
            max_tokens=50
        )

        if response:
            print("✅ OpenAI API connection successful")
            print(f"   - Response: {response[:100]}...")
            return True
        else:
            print("❌ OpenAI API returned no response")
            return False

    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection if configured."""
    print("\n🔴 Testing Redis connection...")

    try:
        from services.session_storage import SessionStorage
        session_storage = SessionStorage()

        if session_storage.use_redis:
            print("✅ Redis connection successful")
            print(f"   - Storage type: {session_storage.get_storage_status()['storage_type']}")
            return True
        else:
            print("⚠️ Redis not available, using in-memory fallback")
            print("   - This is fine for development, but consider Redis for production")
            return True

    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        print("   - Will use in-memory storage as fallback")
        return True  # Not critical for basic functionality


def test_session_storage():
    """Test session storage functionality."""
    print("\n💾 Testing session storage...")

    try:
        from services.session_storage import SessionStorage
        session_storage = SessionStorage()

        # Test basic operations
        test_phone = "+1234567890"
        test_data = {
            'user_phone': test_phone,
            'messages': [],
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }

        # Test save
        save_success = session_storage.save_session(test_phone, test_data)
        if save_success:
            print("✅ Session save successful")
        else:
            print("❌ Session save failed")
            return False

        # Test retrieve
        retrieved_data = session_storage.get_session(test_phone)
        if retrieved_data and retrieved_data['user_phone'] == test_phone:
            print("✅ Session retrieve successful")
        else:
            print("❌ Session retrieve failed")
            return False

        # Test delete
        delete_success = session_storage.delete_session(test_phone)
        if delete_success:
            print("✅ Session delete successful")
        else:
            print("❌ Session delete failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Session storage test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 WhatsApp Chatbot Setup Test")
    print("=" * 40)

    tests = [
        ("Environment Variables", test_environment),
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Service Initialization", test_services),
        ("Redis Connection", test_redis_connection),
        ("Session Storage", test_session_storage),
    ]

    results = []

    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Run async test
    try:
        result = asyncio.run(test_openai_connection())
        results.append(("OpenAI API Connection", result))
    except Exception as e:
        print(f"❌ OpenAI API Connection test failed with exception: {e}")
        results.append(("OpenAI API Connection", False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready to go.")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Or use Docker: docker-compose up")
        print("3. Visit http://localhost:8000 to see the status page")
        print("4. Check storage status at http://localhost:8000/storage/status")
        print("5. Configure your Twilio webhook to point to your server")
        print("6. Test with WhatsApp!")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above and fix them.")
        sys.exit(1)

if __name__ == "__main__":
    main()
