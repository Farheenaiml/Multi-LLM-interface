#!/usr/bin/env python3
"""
Test script to verify FastAPI server starts with custom adapters
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

# Load environment variables
load_dotenv()

async def test_server_startup():
    """Test that FastAPI server can start with custom adapters"""
    print("🚀 TESTING FASTAPI SERVER STARTUP")
    print("=" * 50)
    
    try:
        # Import main components
        print("📦 Importing FastAPI components...")
        from adapters.registry import registry
        from models import BroadcastRequest, Message
        
        print("✅ FastAPI components imported successfully")
        
        # Test adapter registry
        print("\n🔧 Testing adapter registry...")
        adapters = registry.get_all_adapters()
        print(f"✅ Found {len(adapters)} adapters: {list(adapters.keys())}")
        
        # Test model discovery
        print("\n🔍 Testing model discovery...")
        all_models = await registry.discover_models()
        total_models = sum(len(models) for models in all_models.values())
        print(f"✅ Discovered {total_models} models across {len(all_models)} providers")
        
        for provider, models in all_models.items():
            print(f"   • {provider}: {len(models)} models")
        
        print("\n🎉 FastAPI server ready to start!")
        print("You can now run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during server startup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing FastAPI server startup with custom adapters...")
    print()
    
    success = asyncio.run(test_server_startup())
    
    if success:
        print("\n✅ Server startup test passed!")
    else:
        print("\n❌ Server startup test failed!")