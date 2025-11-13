#!/usr/bin/env python3
"""
Test script to verify custom Google and Groq adapters work correctly
"""
import os
import asyncio
import csv
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
import sys
sys.path.append('backend')

from adapters.registry import AdapterRegistry
from models import Message

# Load environment variables
load_dotenv()

async def test_adapters():
    """Test both Google and Groq adapters"""
    print("🚀 TESTING CUSTOM ADAPTERS")
    print("=" * 50)
    
    # Initialize registry
    registry = AdapterRegistry()
    
    # Prepare output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_filename = f"adapter_test_results_{timestamp}.txt"
    csv_filename = f"adapter_test_results_{timestamp}.csv"
    
    results = []
    
    # Test getting models
    print("\n📋 Getting available models...")
    try:
        all_models = await registry.discover_models()
        
        total_models = sum(len(models) for models in all_models.values())
        print(f"✅ Found {total_models} models across {len(all_models)} providers:")
        
        for provider, models in all_models.items():
            print(f"\n   🔹 {provider.upper()} ({len(models)} models):")
            for model in models[:3]:  # Show first 3 models
                print(f"      • {model.id} - {model.name}")
            if len(models) > 3:
                print(f"      ... and {len(models) - 3} more")
                
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return
    
    if not all_models:
        print("❌ No models available - check your API keys")
        return
    
    # Open text file for writing
    with open(txt_filename, 'w', encoding='utf-8') as txt_file:
        txt_file.write(f"Custom Adapter Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        txt_file.write("=" * 80 + "\n\n")
        
        # Test streaming with first available model from each provider
        for provider, models in all_models.items():
            if not models:
                continue
                
            test_model = models[0]
            print(f"\n🧪 Testing streaming with {provider} - {test_model.id}...")
            txt_file.write(f"Testing {provider.upper()} - {test_model.id}\n")
            txt_file.write("-" * 50 + "\n")
            
            # Get the adapter
            adapter = registry.get_adapter(provider)
            if not adapter:
                error_msg = f"❌ Could not get adapter for {provider}"
                print(error_msg)
                txt_file.write(error_msg + "\n\n")
                results.append({
                    'provider': provider,
                    'model_id': test_model.id,
                    'model_name': test_model.name,
                    'status': 'FAILED',
                    'error': 'Could not get adapter',
                    'response': '',
                    'tokens': 0,
                    'cost': 0.0,
                    'latency': 0
                })
                continue
            
            messages = [
                Message(
                    role="user",
                    content="Hello! Please respond with just 'Hello from [your model name]' to test the connection."
                )
            ]
            
            try:
                response_parts = []
                tokens_used = 0
                cost = 0.0
                latency = 0
                error_msg = ""
                status = "SUCCESS"
                
                async for event in adapter.stream(messages, test_model.id, "test-pane"):
                    if event.type == "token":
                        response_parts.append(event.data.token)
                        print(f"📝 Token: {event.data.token}", end="", flush=True)
                    elif event.type == "final":
                        print(f"\n✅ Final: {event.data.finish_reason}")
                        txt_file.write(f"Finish reason: {event.data.finish_reason}\n")
                    elif event.type == "meter":
                        tokens_used = event.data.tokens_used
                        cost = event.data.cost
                        latency = event.data.latency
                        print(f"📊 Tokens: {tokens_used}, Cost: ${cost:.4f}, Latency: {latency}ms")
                        txt_file.write(f"Metrics - Tokens: {tokens_used}, Cost: ${cost:.4f}, Latency: {latency}ms\n")
                    elif event.type == "error":
                        error_msg = event.data.message
                        status = "FAILED"
                        print(f"❌ Error: {error_msg}")
                        txt_file.write(f"Error: {error_msg}\n")
                        break
                
                full_response = ''.join(response_parts)
                if full_response:
                    print(f"🎉 Full response: {full_response}")
                    txt_file.write(f"Response: {full_response}\n")
                
                # Add to results
                results.append({
                    'provider': provider,
                    'model_id': test_model.id,
                    'model_name': test_model.name,
                    'status': status,
                    'error': error_msg,
                    'response': full_response,
                    'tokens': tokens_used,
                    'cost': cost,
                    'latency': latency
                })
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error streaming from {provider}: {error_msg}")
                txt_file.write(f"Exception: {error_msg}\n")
                
                results.append({
                    'provider': provider,
                    'model_id': test_model.id,
                    'model_name': test_model.name,
                    'status': 'FAILED',
                    'error': error_msg,
                    'response': '',
                    'tokens': 0,
                    'cost': 0.0,
                    'latency': 0
                })
            
            txt_file.write("\n" + "=" * 50 + "\n\n")
            print("-" * 30)
    
    # Write CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['provider', 'model_id', 'model_name', 'status', 'error', 'response', 'tokens', 'cost', 'latency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n📄 Results saved to:")
    print(f"   • Text file: {txt_filename}")
    print(f"   • CSV file: {csv_filename}")
    
    # Print summary
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Successful: {len(successful)}")
    print(f"   ❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n🎉 Working models:")
        for result in successful:
            print(f"   • {result['provider']} - {result['model_id']}: \"{result['response'][:50]}...\"")
    
    return results

async def test_health_check():
    """Test health check functionality"""
    print("\n🏥 HEALTH CHECK")
    print("=" * 30)
    
    registry = AdapterRegistry()
    health_status = await registry.health_check()
    
    for provider, is_healthy in health_status.items():
        status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"{provider}: {status}")

if __name__ == "__main__":
    print("Testing custom Google and Groq adapters...")
    print("Make sure you have GOOGLE_API_KEY and GROQ_API_KEY in your .env file")
    print()
    
    asyncio.run(test_adapters())
    asyncio.run(test_health_check())