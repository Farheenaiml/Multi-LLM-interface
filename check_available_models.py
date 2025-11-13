#!/usr/bin/env python3
"""
Check which Google models are actually available through LiteLLM and Google AI Studio
"""
import os
import asyncio
import google.generativeai as genai
from litellm import get_supported_openai_params
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_google_ai_studio_models():
    """Check available models directly from Google AI Studio"""
    print("🔍 CHECKING GOOGLE AI STUDIO AVAILABLE MODELS")
    print("=" * 60)
    
    try:
        # Configure Google AI Studio
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return []
            
        genai.configure(api_key=api_key)
        
        # List available models
        print("📋 Available models from Google AI Studio:")
        available_models = []
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                print(f"✅ {model_name}")
                available_models.append(model_name)
        
        return available_models
        
    except Exception as e:
        print(f"❌ Error checking Google AI Studio models: {e}")
        return []

def check_litellm_google_support():
    """Check LiteLLM's Google model support"""
    print("\n🔍 CHECKING LITELLM GOOGLE MODEL SUPPORT")
    print("=" * 60)
    
    # Common Google model patterns that LiteLLM supports
    litellm_patterns = [
        "gemini/gemini-pro",
        "gemini/gemini-pro-latest", 
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-2.0-flash",
        "gemini/gemini-2.5-pro",
        "gemini/gemini-2.5-flash",
        "gemini/gemini-flash-lite-latest",
        "gemini/gemma-2b-it",
        "gemini/gemma-7b-it",
        "gemini/gemma-2-2b-it",
        "gemini/gemma-2-9b-it", 
        "gemini/gemma-2-27b-it",
        "gemini/gemma-3-4b-it",
        "gemini/gemma-3-12b-it",
        "gemini/gemma-3-27b-it"
    ]
    
    print("📋 LiteLLM Google model patterns:")
    for pattern in litellm_patterns:
        print(f"📝 {pattern}")
    
    return litellm_patterns

def create_recommended_config(google_models, litellm_patterns):
    """Create recommended configuration based on available models"""
    print("\n🎯 RECOMMENDED CONFIGURATION")
    print("=" * 60)
    
    # Map Google AI Studio models to LiteLLM patterns
    recommended = []
    
    for google_model in google_models:
        # Try to find matching LiteLLM pattern
        for pattern in litellm_patterns:
            pattern_model = pattern.replace('gemini/', '')
            if google_model == pattern_model or google_model.replace('-', '.') in pattern_model:
                recommended.append({
                    'google_model': google_model,
                    'litellm_pattern': pattern,
                    'status': '✅ MATCH'
                })
                break
        else:
            # No direct match found
            recommended.append({
                'google_model': google_model,
                'litellm_pattern': f'gemini/{google_model}',
                'status': '⚠️  TRY'
            })
    
    print("📊 Model Mapping:")
    for rec in recommended:
        print(f"{rec['status']} {rec['google_model']} → {rec['litellm_pattern']}")
    
    return recommended

async def main():
    """Main function to check all models"""
    print("🚀 GOOGLE AI STUDIO & LITELLM MODEL COMPATIBILITY CHECK")
    print("=" * 70)
    
    # Check Google AI Studio models
    google_models = check_google_ai_studio_models()
    
    # Check LiteLLM patterns
    litellm_patterns = check_litellm_google_support()
    
    # Create recommendations
    if google_models:
        recommendations = create_recommended_config(google_models, litellm_patterns)
        
        print(f"\n🎉 Found {len(google_models)} available Google models")
        print(f"📝 {len([r for r in recommendations if r['status'] == '✅ MATCH'])} direct matches with LiteLLM")
        print(f"⚠️  {len([r for r in recommendations if r['status'] == '⚠️  TRY'])} models to test")
        
        # Generate YAML config
        print("\n📄 SUGGESTED LITELLM CONFIG:")
        print("-" * 40)
        for rec in recommendations[:10]:  # Show first 10
            model_name = rec['google_model'].replace('gemini-', '').replace('gemma-', 'gemma-')
            print(f"""  - model_name: {model_name}
    litellm_params:
      model: {rec['litellm_pattern']}
      api_key: os.environ/GOOGLE_API_KEY""")
            print()
    else:
        print("❌ No Google models found. Check your API key.")

if __name__ == "__main__":
    asyncio.run(main())