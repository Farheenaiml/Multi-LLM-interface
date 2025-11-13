#!/usr/bin/env python3
"""
Test that we have the correct 5 working Groq models and 3 Google models
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

# Load environment variables
load_dotenv()

async def test_correct_models():
    """Test that we have exactly the right models"""
    print("✅ TESTING CORRECT MODEL CONFIGURATION")
    print("=" * 50)
    
    try:
        from adapters.registry import AdapterRegistry
        
        registry = AdapterRegistry()
        
        # Clear cache to get fresh results
        registry.clear_cache()
        
        # Get models
        all_models = await registry.discover_models()
        
        print(f"📊 Found {len(all_models)} providers")
        
        # Check Groq models
        if "groq" in all_models:
            groq_models = all_models["groq"]
            print(f"\n🤖 GROQ MODELS ({len(groq_models)}):")
            
            expected_groq = [
                "llama-3.1-8b-instant",
                "qwen/qwen3-32b", 
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "meta-llama/llama-4-maverick-17b-128e-instruct"
            ]
            
            for model in groq_models:
                status = "✅" if model.id in expected_groq else "❌"
                print(f"   {status} {model.id} - {model.name}")
            
            # Check for unwanted models
            unwanted = ["compound", "compound-mini"]
            for unwanted_model in unwanted:
                if any(m.id == unwanted_model for m in groq_models):
                    print(f"   ❌ UNWANTED: {unwanted_model} (should be removed)")
            
            print(f"   Expected: {len(expected_groq)}, Got: {len(groq_models)}")
            
        else:
            print("❌ No Groq models found")
        
        # Check Google models  
        if "google" in all_models:
            google_models = all_models["google"]
            print(f"\n🔍 GOOGLE MODELS ({len(google_models)}):")
            
            expected_google = [
                "gemini-2.5-pro",
                "gemini-2.5-flash", 
                "gemini-2.0-flash"
            ]
            
            for model in google_models:
                status = "✅" if model.id in expected_google else "❌"
                print(f"   {status} {model.id} - {model.name}")
            
            print(f"   Expected: {len(expected_google)}, Got: {len(google_models)}")
            
        else:
            print("❌ No Google models found")
        
        # Summary
        total_models = sum(len(models) for models in all_models.values())
        print(f"\n📈 SUMMARY:")
        print(f"   Total models: {total_models}")
        print(f"   Providers: {list(all_models.keys())}")
        
        if total_models == 8:  # 5 Groq + 3 Google
            print("   🎉 Perfect! We have exactly 8 models (5 Groq + 3 Google)")
        else:
            print(f"   ⚠️  Expected 8 models, got {total_models}")
        
        return total_models > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing correct model configuration...")
    print()
    
    success = asyncio.run(test_correct_models())
    
    if success:
        print("\n✅ Model configuration test passed!")
    else:
        print("\n❌ Model configuration test failed!")