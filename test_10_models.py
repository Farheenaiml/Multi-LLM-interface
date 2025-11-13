#!/usr/bin/env python3
"""
Test script to confirm we have exactly 10 models: 3 Google + 7 Groq
"""
import os
import asyncio
from dotenv import load_dotenv

# Add backend to path
import sys
sys.path.append('backend')

from adapters.registry import AdapterRegistry

# Load environment variables
load_dotenv()

async def test_model_count():
    """Test that we have exactly 10 models total"""
    print("🔢 CONFIRMING MODEL COUNT")
    print("=" * 40)
    
    registry = AdapterRegistry()
    
    # Test Google models
    print("\n🔍 Google Models:")
    google_adapter = registry.get_adapter("google")
    google_models = await google_adapter.get_models()
    
    print(f"   Found {len(google_models)} Google models:")
    for i, model in enumerate(google_models, 1):
        print(f"   {i}. {model.id} - {model.name}")
    
    # Test Groq models  
    print("\n🔍 Groq Models:")
    groq_adapter = registry.get_adapter("groq")
    groq_models = await groq_adapter.get_models()
    
    print(f"   Found {len(groq_models)} Groq models:")
    for i, model in enumerate(groq_models, 1):
        print(f"   {i}. {model.id} - {model.name}")
    
    # Summary
    total_models = len(google_models) + len(groq_models)
    print(f"\n📊 SUMMARY:")
    print(f"   Google: {len(google_models)} models")
    print(f"   Groq: {len(groq_models)} models")
    print(f"   Total: {total_models} models")
    
    if total_models == 10 and len(google_models) == 3 and len(groq_models) == 7:
        print("   ✅ Perfect! We have exactly 3 Google + 7 Groq = 10 models")
    else:
        print("   ❌ Model count doesn't match expected (3 Google + 7 Groq = 10)")
    
    # Verify specific models
    print(f"\n🎯 VERIFYING SPECIFIC MODELS:")
    
    expected_google = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]
    expected_groq = [
        "llama-3.1-8b-instant", "qwen/qwen3-32b", "openai/gpt-oss-120b", 
        "openai/gpt-oss-20b", "openai/gpt-oss-safeguard-20b",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct"
    ]
    
    google_ids = [m.id for m in google_models]
    groq_ids = [m.id for m in groq_models]
    
    print("   Google models:")
    for model_id in expected_google:
        status = "✅" if model_id in google_ids else "❌"
        print(f"     {status} {model_id}")
    
    print("   Groq models:")
    for model_id in expected_groq:
        status = "✅" if model_id in groq_ids else "❌"
        print(f"     {status} {model_id}")

if __name__ == "__main__":
    print("Confirming we have exactly 10 models (3 Google + 7 Groq)...")
    print()
    
    asyncio.run(test_model_count())