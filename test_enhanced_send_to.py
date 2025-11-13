#!/usr/bin/env python3

import requests
import json
import time

def test_send_to_functionality():
    """Test the enhanced send-to functionality"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Enhanced Send-To Functionality")
    print("=" * 50)
    
    # Step 1: Create a session with some messages
    print("1. Creating test session...")
    
    # Create a broadcast to generate some messages
    broadcast_data = {
        "session_id": "test-send-to-session",
        "prompt": "Hello, this is a test message for send-to functionality.",
        "models": [
            {
                "provider_id": "google",
                "model_id": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_tokens": 100
            },
            {
                "provider_id": "groq", 
                "model_id": "llama-3.1-8b-instant",
                "temperature": 0.7,
                "max_tokens": 100
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/broadcast", json=broadcast_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Broadcast created: {result}")
            pane_ids = result.get("pane_ids", [])
            
            if len(pane_ids) >= 2:
                source_pane = pane_ids[0]
                target_pane = pane_ids[1]
                
                # Wait a moment for messages to be generated
                print("2. Waiting for messages to be generated...")
                time.sleep(3)
                
                # Step 2: Get session to see the messages
                session_response = requests.get(f"{base_url}/sessions/test-send-to-session")
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    print(f"✅ Session retrieved with {len(session_data.get('panes', []))} panes")
                    
                    # Find messages in source pane
                    source_pane_data = None
                    for pane in session_data.get('panes', []):
                        if pane['id'] == source_pane:
                            source_pane_data = pane
                            break
                    
                    if source_pane_data and source_pane_data.get('messages'):
                        message_ids = [msg['id'] for msg in source_pane_data['messages']]
                        print(f"✅ Found {len(message_ids)} messages in source pane")
                        
                        # Step 3: Test send-to functionality
                        print("3. Testing send-to transfer...")
                        
                        send_to_data = {
                            "source_pane_id": source_pane,
                            "target_pane_id": target_pane,
                            "message_ids": message_ids,
                            "session_id": "test-send-to-session",
                            "transfer_mode": "append",
                            "additional_context": "This is additional context for the transfer.",
                            "preserve_roles": True,
                            "summary_instructions": None
                        }
                        
                        send_response = requests.post(f"{base_url}/send-to", json=send_to_data)
                        
                        if send_response.status_code == 200:
                            send_result = send_response.json()
                            print(f"✅ Send-to successful: {send_result}")
                            
                            # Step 4: Verify the transfer
                            print("4. Verifying transfer...")
                            verify_response = requests.get(f"{base_url}/sessions/test-send-to-session")
                            if verify_response.status_code == 200:
                                verify_data = verify_response.json()
                                
                                # Check target pane
                                target_pane_data = None
                                for pane in verify_data.get('panes', []):
                                    if pane['id'] == target_pane:
                                        target_pane_data = pane
                                        break
                                
                                if target_pane_data:
                                    transferred_messages = target_pane_data.get('messages', [])
                                    print(f"✅ Target pane now has {len(transferred_messages)} messages")
                                    
                                    # Check for provenance
                                    provenance_count = sum(1 for msg in transferred_messages if msg.get('provenance'))
                                    print(f"✅ {provenance_count} messages have provenance tracking")
                                    
                                    print("\n🎉 Send-to functionality test PASSED!")
                                    return True
                                else:
                                    print("❌ Could not find target pane after transfer")
                            else:
                                print(f"❌ Failed to verify transfer: {verify_response.status_code}")
                        else:
                            print(f"❌ Send-to failed: {send_response.status_code} - {send_response.text}")
                    else:
                        print("❌ No messages found in source pane")
                else:
                    print(f"❌ Failed to get session: {session_response.status_code}")
            else:
                print("❌ Not enough panes created for testing")
        else:
            print(f"❌ Broadcast failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
    
    print("\n❌ Send-to functionality test FAILED!")
    return False

if __name__ == "__main__":
    test_send_to_functionality()