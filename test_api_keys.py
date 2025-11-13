#!/usr/bin/env python3
"""
Test that API keys are properly loaded
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

# Load environment variables
load_dotenv()

def test_api_keys():
    """Test API key loading"""
    print("🔑 TESTING API KEY LOADING")
    print("=" * 40)
    
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print(f"Google API Key: {'✅ Loaded' if google_key else '❌ Missing'}")
    if google_key:
        print(f"   Length: {len(google_key)} characters")
        print(f"   Starts with: {google_key[:10]}...")
    
    print(f"Groq API Key: {'✅ Loaded' if groq_key else '❌ Missing'}")
    if groq_key:
        print(f"   Length: {len(groq_key)} characters") 
        print(f"   Starts with: {groq_key[:10]}...")
    
    if google_key and groq_key:
        print("\n🎉 Both API keys are loaded!")
        return True
    else:
        print("\n❌ Missing API keys - check your .env file")
        return False

if __name__ == "__main__":
    test_api_keys()