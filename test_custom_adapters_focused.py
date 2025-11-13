#!/usr/bin/env python3
"""
Focused test script for custom Google and Groq adapters with specific models
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

async def test_specific_models():
    """Test specific reliable models from litellm_config.yaml"""
    print("🚀 TESTING CUSTOM ADAPTERS WITH SPECIFIC MODELS")
    print("=" * 60)
    
    # Initialize registry
    registry = AdapterRegistry()
    
    # Test specific models that we know work
    test_cases = [
        ("google", "gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("groq", "llama-3.1-8b-instant", "Llama 3.1 8B Instant"),
        ("groq", "compound-mini", "Compound Mini")
    ]
    
    for provider, model_id, model_name in test_cases:
        print(f"\n🧪 Testing {provider.upper()} - {model_name} ({model_id})")
        print("-" * 50)
        
        # Get the adapter
        adapter = registry.get_adapter(provider)
        if not adapter:
            print(f"❌ Could not get adapter for {provider}")
            continue
        
        messages = [
            Message(
                role="user",
                content="Say 'Hello! I am working correctly.' to test the connection."
            )
        ]
        
        try:
            response_parts = []
            token_count = 0
            
            async for event in adapter.stream(messages, model_id, f"test-pane-{provider}"):
                if event.type == "status":
                    print(f"📡 Status: {event.data.message}")
                elif event.type == "token":
                    response_parts.append(event.data.token)
                    token_count += 1
                    if token_count <= 5:  # Show first few tokens
                        print(f"📝 Token {token_count}: '{event.data.token}'")
                    elif token_count == 6:
                        print("📝 ... (continuing)")
                elif event.type == "final":
                    print(f"✅ Completed: {event.data.finish_reason}")
                    full_response = ''.join(response_parts)
                    print(f"🎉 Full response: {full_response}")
                elif event.type == "meter":
                    print(f"📊 Metrics - Tokens: {event.data.tokens_used}, Cost: ${event.data.cost:.4f}, Latency: {event.data.latency}ms")
                elif event.type == "error":
                    print(f"❌ Error: {event.data.message} (Code: {event.data.code})")
                    break
            
        except Exception as e:
            print(f"❌ Exception during streaming: {e}")
        
        print()

async def test_model_discovery():
    """Test model discovery for both providers"""
    print("\n📋 TESTING MODEL DISCOVERY")
    print("=" * 40)
    
    registry = AdapterRegistry()
    
    for provider in ["google", "groq"]:
        print(f"\n🔍 Discovering {provider.upper()} models...")
        
        adapter = registry.get_adapter(provider)
        if not adapter:
            print(f"❌ Could not get adapter for {provider}")
            continue
        
        try:
            models = await adapter.get_models()
            print(f"✅ Found {len(models)} models:")
            
            for i, model in enumerate(models[:5]):  # Show first 5
                print(f"   {i+1}. {model.id} - {model.name}")
                print(f"      Max tokens: {model.max_tokens}, Cost/1K: ${model.cost_per_1k_tokens}")
            
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more models")
                
        except Exception as e:
            print(f"❌ Error discovering models: {e}")

if __name__ == "__main__":
    print("Testing custom Google and Groq adapters with specific models...")
    print("Make sure you have GOOGLE_API_KEY and GROQ_API_KEY in your .env file")
    print()
    
    asyncio.run(test_model_discovery())
    asyncio.run(test_specific_models())