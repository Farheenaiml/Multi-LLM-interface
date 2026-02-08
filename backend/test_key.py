
import os
import asyncio
import httpx

async def main():
    print("🔍 DEBUG: Listing Google Models...")
    
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("❌ FAIL: GOOGLE_API_KEY is not set.")
        return
        
    masked_key = key[:10] + "..." + key[-4:]
    print(f"🔑 Key: {masked_key}")
    
    # List models
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                print("\n✅ AVAILABLE MODELS:")
                data = response.json()
                models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                for m in models:
                    print(f"  - {m}")
                    
                # Try a test generation with the first flash model found
                flash_models = [m for m in models if 'flash' in m]
                target_model = flash_models[0] if flash_models else (models[0] if models else None)
                
                if target_model:
                    # Strip 'models/' prefix for the generation call if present in list but needed in URL? 
                    # Actually usually the name includes 'models/' prefix like 'models/gemini-pro'
                    # But the generation URL needs 'models/MODEL_ID:generateContent'
                    # Let's try to use the name exactly as returned.
                    
                    print(f"\n🧪 Testing generation with: {target_model}")
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={key}"
                    
                    resp = await client.post(gen_url, json={"contents": [{"parts": [{"text": "hi"}]}]})
                    print(f"  Status: {resp.status_code}")
                    if resp.status_code == 200:
                         print(f"  Response: {resp.json()['candidates'][0]['content']['parts'][0]['text']}")
                    else:
                         print(f"  Error: {resp.text}")
            else:
                print(f"❌ FAIL: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
