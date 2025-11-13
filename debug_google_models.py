#!/usr/bin/env python3
"""
Debug script to figure out exactly which Google models are available and working
"""
import os
import asyncio
from litellm import completion, get_supported_openai_params
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_model_with_details(model_name, display_name):
    """Test a model and get detailed information"""
    print(f"\n🔍 Testing {display_name} ({model_name})...")
    
    try:
        # Test with a more specific prompt
        response = completion(
            model=model_name,
            messages=[
                {"role": "user", "content": "In exactly one sentence, tell me: What is your exact model name, version, and parameter count?"}
            ],
            max_tokens=100,
            temperature=0.0  # Make it deterministic
        )
        
        content = response.choices[0].message.content
        
        # Get response metadata if available
        usage = getattr(response, 'usage', None)
        model_used = getattr(response, 'model', 'unknown')
        
        print(f"✅ {display_name}:")
        print(f"   Response: {content}")
        print(f"   Model used: {model_used}")
        if usage:
            print(f"   Tokens: {usage.prompt_tokens} prompt + {usage.completion_tokens} completion = {usage.total_tokens} total")
        
        return True, content
        
    except Exception as e:
        print(f"❌ {display_name} failed: {str(e)}")
        return False, str(e)

async def test_alternative_models():
    """Test some alternative model names that might work better"""
    print("\n🧪 Testing alternative Google model names...")
    
    alternative_models = [
        # Try different Gemini model names
        ("gemini-pro", "Gemini Pro (alternative)"),
        ("gemini-pro-latest", "Gemini Pro Latest"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        
        # Try different Gemma model names
        ("gemma-2b-it", "Gemma 2B IT"),
        ("gemma-7b-it", "Gemma 7B IT"),
        ("gemma-2-2b-it", "Gemma 2 2B IT"),
        ("gemma-2-9b-it", "Gemma 2 9B IT"),
        ("gemma-2-27b-it", "Gemma 2 27B IT"),
    ]
    
    working_alternatives = []
    
    for model_name, display_name in alternative_models:
        try:
            full_model_name = f"gemini/{model_name}"
            success, response = await test_model_with_details(full_model_name, display_name)
            if success:
                working_alternatives.append((display_name, full_model_name, response))
        except Exception as e:
            print(f"❌ {display_name}: {str(e)}")
    
    return working_alternatives

async def main():
    """Main test function"""
    print("🔍 DEBUGGING GOOGLE AI STUDIO MODELS")
    print("="*60)
    print(f"📋 Using API Key: {os.getenv('GOOGLE_API_KEY', 'NOT SET')[:20]}...")
    
    # Test original models
    print("\n📋 Testing Original Configuration:")
    original_models = [
        ("gemini/gemini-2.5-pro", "Gemini 2.5 Pro"),
        ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash"), 
        ("gemini/gemini-flash-lite-latest", "Gemini Flash Latest"),
        ("gemini/gemma-3-4b-it", "Gemma 3 4B"),
        ("gemini/gemma-3-12b-it", "Gemma 3 12B"),
        ("gemini/gemma-3-27b-it", "Gemma 3 27B"),
    ]
    
    original_results = []
    for model_name, display_name in original_models:
        success, response = await test_model_with_details(model_name, display_name)
        original_results.append((display_name, success, response))
    
    # Test alternatives
    alternative_results = await test_alternative_models()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEBUGGING SUMMARY")
    print("="*60)
    
    print("\n🔧 ORIGINAL MODELS:")
    working_originals = []
    for display_name, success, response in original_results:
        status = "✅" if success else "❌"
        print(f"{status} {display_name}")
        if success and response and response.strip() and response != "None":
            working_originals.append(display_name)
    
    print(f"\n🔧 WORKING ALTERNATIVES:")
    for display_name, model_name, response in alternative_results:
        print(f"✅ {display_name} ({model_name})")
        print(f"   → {response[:100]}...")
    
    print(f"\n📈 RECOMMENDATIONS:")
    if len(alternative_results) > len(working_originals):
        print("💡 Consider updating litellm_config.yaml with working alternative model names")
        print("\nSuggested model names to try:")
        for display_name, model_name, _ in alternative_results:
            print(f"  - {model_name}")
    else:
        print("✅ Original configuration seems to be working well")
    
    print(f"\n🎯 TOTAL WORKING MODELS: {len(working_originals)} original + {len(alternative_results)} alternatives")

if __name__ == "__main__":
    asyncio.run(main())