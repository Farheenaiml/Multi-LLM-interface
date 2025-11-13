#!/usr/bin/env python3
"""
Test script to ask models to identify themselves and show detailed error info
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

async def test_model_identity():
    """Test models by asking them to identify themselves"""
    print("🆔 MODEL IDENTITY TEST")
    print("=" * 50)
    
    registry = AdapterRegistry()
    
    # Get all models
    print("\n📋 Getting available models...")
    all_models = await registry.discover_models()
    
    total_models = sum(len(models) for models in all_models.values())
    print(f"Found {total_models} models across {len(all_models)} providers")
    
    # Test each model
    successful = 0
    failed = 0
    
    for provider, models in all_models.items():
        print(f"\n🔹 Testing {provider.upper()} models:")
        
        adapter = registry.get_adapter(provider)
        if not adapter:
            print(f"❌ Could not get adapter for {provider}")
            continue
        
        for model in models:
            print(f"\n🧪 Testing {model.name} ({model.id})")
            print("-" * 40)
            
            # Ask model to identify itself
            messages = [
                Message(
                    role="user",
                    content="Hello! Please respond with: 'Hello World! I am [your exact model name]' - replace [your exact model name] with your actual model name."
                )
            ]
            
            try:
                response_parts = []
                error_occurred = False
                
                async for event in adapter.stream(messages, model.id, f"test-{provider}-{model.id}"):
                    if event.type == "status":
                        print(f"📡 {event.data.message}")
                    elif event.type == "token":
                        response_parts.append(event.data.token)
                        # Show first few tokens
                        if len(response_parts) <= 3:
                            print(f"📝 Token: '{event.data.token}'")
                        elif len(response_parts) == 4:
                            print("📝 ... (continuing)")
                    elif event.type == "final":
                        full_response = ''.join(response_parts)
                        print(f"✅ Complete Response: {full_response}")
                        print(f"📊 Finish: {event.data.finish_reason}")
                        successful += 1
                    elif event.type == "meter":
                        print(f"📈 Tokens: {event.data.tokens_used}, Cost: ${event.data.cost:.4f}, Latency: {event.data.latency}ms")
                    elif event.type == "error":
                        print(f"❌ ERROR: {event.data.message}")
                        print(f"❌ Error Code: {event.data.code}")
                        print(f"❌ Retryable: {event.data.retryable}")
                        error_occurred = True
                        failed += 1
                        break
                
                if not error_occurred and not response_parts:
                    print("❌ No response received (timeout or silent failure)")
                    failed += 1
                
            except Exception as e:
                print(f"❌ Exception: {e}")
                failed += 1
            
            print()
    
    # Summary
    print(f"\n📊 FINAL RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {successful/(successful+failed)*100:.1f}%")
    
    if successful > 0:
        print(f"\n🎉 Ready for broadcast with {successful} working models!")
    else:
        print(f"\n⚠️  No working models - need to debug API connections")

if __name__ == "__main__":
    print("Testing model identity and error handling...")
    print("This will show detailed error codes and ask models to identify themselves")
    print()
    
    asyncio.run(test_model_identity())