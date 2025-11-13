#!/usr/bin/env python3
"""
Check which models are available through LiteLLM itself (not our config)
"""
import os
import asyncio
from litellm import completion, get_supported_openai_params
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_litellm_model(model_name):
    """Test if a model works through LiteLLM directly"""
    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": "Hi, what model are you?"}],
            max_tokens=50,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        model_used = response.model if hasattr(response, 'model') else 'unknown'
        
        return {
            'success': True,
            'response': content,
            'model_used': model_used
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def check_litellm_google_models():
    """Check Google models directly through LiteLLM (not our config)"""
    print("🔍 TESTING GOOGLE MODELS THROUGH LITELLM DIRECTLY")
    print("=" * 60)
    print(f"📋 Using API Key: {os.getenv('GOOGLE_API_KEY', 'NOT SET')[:20]}...")
    print()
    
    # Test common Google model names that LiteLLM should support
    models_to_test = [
        # Gemini models
        "gemini/gemini-pro",
        "gemini/gemini-pro-latest",
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-flash", 
        "gemini/gemini-2.0-flash",
        "gemini/gemini-2.5-pro",
        "gemini/gemini-2.5-flash",
        "gemini/gemini-flash-lite-latest",
        
        # Gemma models
        "gemini/gemma-2b-it",
        "gemini/gemma-7b-it", 
        "gemini/gemma-2-2b-it",
        "gemini/gemma-2-9b-it",
        "gemini/gemma-2-27b-it",
        "gemini/gemma-3-4b-it",
        "gemini/gemma-3-12b-it", 
        "gemini/gemma-3-27b-it",
        
        # Alternative formats
        "google/gemini-pro",
        "google/gemini-1.5-pro",
        "google/gemini-flash",
    ]
    
    working_models = []
    failed_models = []
    
    for model_name in models_to_test:
        print(f"🧪 Testing {model_name}...")
        result = await test_litellm_model(model_name)
        
        if result['success']:
            print(f"✅ {model_name}")
            print(f"   Response: {result['response'][:80]}...")
            print(f"   Model used: {result['model_used']}")
            working_models.append({
                'name': model_name,
                'response': result['response'],
                'model_used': result['model_used']
            })
        else:
            print(f"❌ {model_name}")
            print(f"   Error: {result['error'][:100]}...")
            failed_models.append({
                'name': model_name,
                'error': result['error']
            })
        print()
    
    return working_models, failed_models

def generate_config_from_working_models(working_models):
    """Generate litellm_config.yaml based on working models"""
    print("📄 SUGGESTED CONFIG BASED ON WORKING MODELS:")
    print("=" * 60)
    
    if not working_models:
        print("❌ No working models found!")
        return
    
    print("model_list:")
    for i, model in enumerate(working_models):
        # Create a clean model name for the config
        clean_name = model['name'].replace('gemini/', '').replace('google/', '')
        
        print(f"  # Model {i+1}: {clean_name}")
        print(f"  - model_name: {clean_name}")
        print(f"    litellm_params:")
        print(f"      model: {model['name']}")
        print(f"      api_key: os.environ/GOOGLE_API_KEY")
        print()

async def main():
    """Main function"""
    print("🚀 LITELLM GOOGLE MODELS COMPATIBILITY TEST")
    print("=" * 70)
    print("This tests models directly through LiteLLM, not our config file")
    print()
    
    working_models, failed_models = await check_litellm_google_models()
    
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Working models: {len(working_models)}")
    print(f"❌ Failed models: {len(failed_models)}")
    print()
    
    if working_models:
        print("🎉 WORKING MODELS:")
        for model in working_models:
            print(f"  ✅ {model['name']} → {model['model_used']}")
        print()
        
        generate_config_from_working_models(working_models)
    
    if failed_models:
        print("⚠️  FAILED MODELS:")
        for model in failed_models[:5]:  # Show first 5 failures
            print(f"  ❌ {model['name']}: {model['error'][:60]}...")

if __name__ == "__main__":
    asyncio.run(main())