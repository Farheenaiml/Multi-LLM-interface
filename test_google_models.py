#!/usr/bin/env python3
"""
Test script to verify Google AI Studio models work with LiteLLM
"""
import os
import asyncio
from litellm import completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_google_model(model_name, display_name):
    """Test a single Google model"""
    print(f"\n🧪 Testing {display_name} ({model_name})...")
    
    try:
        # Test prompt asking model to identify itself
        response = completion(
            model=model_name,
            messages=[
                {"role": "user", "content": "Please tell me your exact model name and version. What model are you? Be specific about which Gemini or Gemma model you are."}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        print(f"✅ {display_name}: {content}")
        return True
        
    except Exception as e:
        print(f"❌ {display_name} failed: {str(e)}")
        return False

async def main():
    """Test all Google models"""
    print("🚀 Testing Google AI Studio Models...")
    print(f"📋 Using API Key: {os.getenv('GOOGLE_API_KEY', 'NOT SET')[:20]}...")
    
    # Models to test (using the exact model names from litellm_config.yaml)
    models_to_test = [
        ("gemini/gemini-2.5-pro", "Gemini 2.5 Pro"),
        ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("gemini/gemini-flash-lite-latest", "Gemini Flash Latest"),
        ("gemini/gemma-3-4b-it", "Gemma 3 4B"),
        ("gemini/gemma-3-12b-it", "Gemma 3 12B"),
        ("gemini/gemma-3-27b-it", "Gemma 3 27B"),
    ]
    
    results = []
    for model_name, display_name in models_to_test:
        success = await test_google_model(model_name, display_name)
        results.append((display_name, success))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    working_models = []
    failed_models = []
    
    for display_name, success in results:
        if success:
            print(f"✅ {display_name}")
            working_models.append(display_name)
        else:
            print(f"❌ {display_name}")
            failed_models.append(display_name)
    
    print(f"\n🎉 Working models: {len(working_models)}/{len(results)}")
    if failed_models:
        print(f"⚠️  Failed models: {', '.join(failed_models)}")
    else:
        print("🎊 All Google models are working perfectly!")

if __name__ == "__main__":
    asyncio.run(main())