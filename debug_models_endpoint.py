#!/usr/bin/env python3
"""
Debug the models endpoint to see why no models are returned
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

# Load environment variables
load_dotenv()

async def debug_models():
    """Debug model discovery"""
    print("🔍 DEBUGGING MODELS ENDPOINT")
    print("=" * 50)
    
    try:
        # Test adapter registry directly
        from adapters.registry import AdapterRegistry
        
        registry = AdapterRegistry()
        print("✅ Registry created")
        
        # Test each adapter individually
        for provider in ["google", "groq"]:
            print(f"\n🧪 Testing {provider} adapter...")
            
            adapter = registry.get_adapter(provider)
            if not adapter:
                print(f"❌ No adapter for {provider}")
                continue
                
            print(f"✅ Got {provider} adapter")
            
            try:
                models = await adapter.get_models()
                print(f"✅ {provider} returned {len(models)} models:")
                for model in models[:3]:  # Show first 3
                    print(f"   • {model.id} - {model.name}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more")
            except Exception as e:
                print(f"❌ {provider} error: {e}")
                import traceback
                traceback.print_exc()
        
        # Test registry discover_models
        print(f"\n🔍 Testing registry discover_models...")
        all_models = await registry.discover_models()
        
        total = sum(len(models) for models in all_models.values())
        print(f"✅ Registry returned {total} models from {len(all_models)} providers")
        
        for provider, models in all_models.items():
            print(f"   • {provider}: {len(models)} models")
        
        # Test the actual endpoint logic
        print(f"\n🌐 Testing endpoint logic...")
        all_models_list = []
        for provider, models in all_models.items():
            for model in models:
                all_models_list.append({
                    "id": f"{provider}:{model.id}",
                    "name": model.name,
                    "provider": provider,
                    "max_tokens": model.max_tokens,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "supports_streaming": model.supports_streaming
                })
        
        print(f"✅ Endpoint would return {len(all_models_list)} models")
        
        # Show sample models
        if all_models_list:
            print("\n📋 Sample models:")
            for model in all_models_list[:5]:
                print(f"   • {model['id']} - {model['name']}")
        
        return len(all_models_list) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Debugging models endpoint...")
    print()
    
    success = asyncio.run(debug_models())
    
    if success:
        print("\n✅ Models endpoint should work!")
    else:
        print("\n❌ Models endpoint has issues!")