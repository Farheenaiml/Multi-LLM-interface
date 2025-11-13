#!/usr/bin/env python3
"""
Hello World test for the 6 working models
"""
import os
import asyncio
from dotenv import load_dotenv

# Add backend to path
import sys
sys.path.append('backend')

from adapters.registry import AdapterRegistry
from models import Message

# Load environment variables
load_dotenv()

async def test_hello_world():
    """Test hello world with the 6 working models"""
    print("👋 HELLO WORLD TEST - 6 WORKING MODELS")
    print("=" * 50)
    
    # Initialize registry
    registry = AdapterRegistry()
    
    # Test specific working models
    working_models = [
        ("google", "gemini-2.5-pro", "Gemini 2.5 Pro"),
        ("google", "gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("google", "gemini-2.0-flash", "Gemini 2.0 Flash"),
        ("groq", "llama-3.1-8b-instant", "Llama 3.1 8B Instant"),
        ("groq", "qwen/qwen3-32b", "Qwen 3 32B"),
        ("groq", "openai/gpt-oss-120b", "GPT OSS 120B"),
        ("groq", "openai/gpt-oss-20b", "GPT OSS 20B"),
        ("groq", "meta-llama/llama-4-maverick-17b-128e-instruct", "Llama 4 Maverick 17B")
    ]
    
    successful_tests = 0
    
    for provider, model_id, model_name in working_models:
        print(f"\n🧪 Testing {provider.upper()} - {model_name}")
        print("-" * 40)
        
        # Get the adapter
        adapter = registry.get_adapter(provider)
        if not adapter:
            print(f"❌ Could not get adapter for {provider}")
            continue
        
        messages = [
            Message(
                role="user",
                content="Say exactly: 'Hello World! I am working correctly.'"
            )
        ]
        
        try:
            response_parts = []
            success = False
            
            async for event in adapter.stream(messages, model_id, f"test-{provider}-{model_id.replace('/', '-')}"):
                if event.type == "status":
                    print(f"📡 {event.data.message}")
                elif event.type == "token":
                    response_parts.append(event.data.token)
                elif event.type == "final":
                    full_response = ''.join(response_parts)
                    print(f"✅ Response: {full_response}")
                    print(f"📊 Finish reason: {event.data.finish_reason}")
                    success = True
                elif event.type == "meter":
                    print(f"📈 Tokens: {event.data.tokens_used}, Cost: ${event.data.cost:.4f}, Latency: {event.data.latency}ms")
                elif event.type == "error":
                    print(f"❌ Error: {event.data.message}")
                    break
            
            if success:
                successful_tests += 1
                print("🎉 SUCCESS!")
            
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    print(f"📊 FINAL RESULTS:")
    print(f"   Successful: {successful_tests}/{len(working_models)} models")
    print(f"   Success rate: {(successful_tests/len(working_models)*100):.1f}%")
    
    if successful_tests >= 4:  # At least 4 out of 8 working
        print("🎉 READY FOR BROADCAST IMPLEMENTATION!")
    else:
        print("⚠️  Need to fix more models before proceeding")

if __name__ == "__main__":
    print("Testing Hello World with working models...")
    print()
    
    asyncio.run(test_hello_world())