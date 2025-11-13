#!/usr/bin/env python3
"""
List all available Google models to verify correct model names
"""
import os
import asyncio
from litellm import get_supported_openai_params
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

async def list_google_models():
    """List all available Google models"""
    print("🔍 LISTING AVAILABLE GOOGLE AI STUDIO MODELS")
    print("="*60)
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    try:
        # Configure the Google AI client
        genai.configure(api_key=api_key)
        
        print("📋 Available models from Google AI Studio:")
        print("-" * 40)
        
        # List all available models
        models = genai.list_models()
        
        gemini_models = []
        gemma_models = []
        other_models = []
        
        for model in models:
            model_name = model.name
            display_name = model.display_name if hasattr(model, 'display_name') else "N/A"
            
            print(f"🤖 {model_name}")
            print(f"   Display: {display_name}")
            
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
                print(f"   Methods: {', '.join(methods)}")
            
            if hasattr(model, 'input_token_limit'):
                print(f"   Input tokens: {model.input_token_limit:,}")
            
            if hasattr(model, 'output_token_limit'):
                print(f"   Output tokens: {model.output_token_limit:,}")
            
            print()
            
            # Categorize models
            if 'gemini' in model_name.lower():
                gemini_models.append(model_name)
            elif 'gemma' in model_name.lower():
                gemma_models.append(model_name)
            else:
                other_models.append(model_name)
        
        # Summary
        print("="*60)
        print("📊 MODEL SUMMARY")
        print("="*60)
        
        print(f"🔷 Gemini Models ({len(gemini_models)}):")
        for model in gemini_models:
            print(f"   - {model}")
        
        print(f"\n🔶 Gemma Models ({len(gemma_models)}):")
        for model in gemma_models:
            print(f"   - {model}")
        
        print(f"\n🔸 Other Models ({len(other_models)}):")
        for model in other_models:
            print(f"   - {model}")
        
        print(f"\n📈 Total Models Available: {len(gemini_models) + len(gemma_models) + len(other_models)}")
        
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")
        print("💡 Make sure your GOOGLE_API_KEY is valid and has proper permissions")

if __name__ == "__main__":
    asyncio.run(list_google_models())