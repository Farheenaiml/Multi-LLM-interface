#!/usr/bin/env python3

import requests
import json
import time

def test_replace_mode():
    """Test that replace mode actually replaces messages instead of appending"""
    
    base_url = "http://localhost:5000"
    session_id = "test-replace-mode"
    
    print("🧪 Testing Replace Mode Functionality")
    print("=" * 50)
    
    try:
        # Step 1: Create a broadcast to generate initial messages
        print("1. Creating initial broadcast...")
        
        broadcast_data = {
            "session_id": session_id,
            "prompt": "Initial message for replace test.",
            "models": [
                {
                    "provider_id": "google",
                    "model_id": "gemini-2.0-flash",
                    "temperature": 0.7,
                    "max_tokens": 50
                },
                {
                    "provider_id": "groq", 
                    "model_id": "llama-3.1-8b-instant",
                    "temperature": 0.7,
                    "max_tokens": 50
                }
            ]
        }
        
        response = requests.post(f"{base_url}/broadcast", json=broadcast_data)
        if response.status_code != 200:
            print(f"❌ Initial broadcast failed: {response.status_code}")
            return False
            
        result = response.json()
        pane_ids = result.get("pane_ids", [])
        
        if len(pane_ids) < 2:
            print("❌ Need at least 2 panes for testing")
            return False
            
        source_pane = pane_ids[0]
        target_pane = pane_ids[1]
        
        # Wait for messages to be generated
        print("2. Waiting for initial messages...")
        time.sleep(3)
        
        # Step 2: Add more messages to target pane
        print("3. Adding additional messages to target pane...")
        
        second_broadcast = {
            "session_id": session_id,
            "prompt": "Second message to populate target pane.",
            "models": [
                {
                    "provider_id": "google",
                    "model_id": "gemini-2.0-flash",
                    "temperature": 0.7,
                    "max_tokens": 50
                }
            ]
        }
        
        requests.post(f"{base_url}/broadcast", json=second_broadcast)
        time.sleep(2)
        
        # Step 3: Check target pane message count before replace
        session_response = requests.get(f"{base_url}/sessions/{session_id}")
        if session_response.status_code != 200:
            print(f"❌ Failed to get session: {session_response.status_code}")
            return False
            
        session_data = session_response.json()
        
        target_pane_data = None
        source_pane_data = None
        
        for pane in session_data.get('panes', []):
            if pane['id'] == target_pane:
                target_pane_data = pane
            elif pane['id'] == source_pane:
                source_pane_data = pane
        
        if not target_pane_data or not source_pane_data:
            print("❌ Could not find panes")
            return False
            
        initial_target_count = len(target_pane_data.get('messages', []))
        source_message_ids = [msg['id'] for msg in source_pane_data.get('messages', [])]
        
        print(f"📊 Target pane has {initial_target_count} messages before replace")
        print(f"📊 Source pane has {len(source_message_ids)} messages to transfer")
        
        if initial_target_count == 0 or len(source_message_ids) == 0:
            print("❌ Need messages in both panes for testing")
            return False
        
        # Step 4: Test REPLACE mode
        print("4. Testing REPLACE mode...")
        
        replace_data = {
            "source_pane_id": source_pane,
            "target_pane_id": target_pane,
            "message_ids": source_message_ids,
            "session_id": session_id,
            "transfer_mode": "replace",  # This should clear target pane first
            "additional_context": None,
            "preserve_roles": True,
            "summary_instructions": None
        }
        
        replace_response = requests.post(f"{base_url}/send-to", json=replace_data)
        
        if replace_response.status_code != 200:
            print(f"❌ Replace operation failed: {replace_response.status_code} - {replace_response.text}")
            return False
            
        replace_result = replace_response.json()
        print(f"✅ Replace operation completed: {replace_result}")
        
        # Step 5: Verify replace worked correctly
        print("5. Verifying replace operation...")
        
        verify_response = requests.get(f"{base_url}/sessions/{session_id}")
        if verify_response.status_code != 200:
            print(f"❌ Failed to verify: {verify_response.status_code}")
            return False
            
        verify_data = verify_response.json()
        
        final_target_pane = None
        for pane in verify_data.get('panes', []):
            if pane['id'] == target_pane:
                final_target_pane = pane
                break
        
        if not final_target_pane:
            print("❌ Could not find target pane after replace")
            return False
            
        final_target_count = len(final_target_pane.get('messages', []))
        transferred_count = replace_result.get('transferred_count', 0)
        
        print(f"📊 Target pane has {final_target_count} messages after replace")
        print(f"📊 Expected {transferred_count} messages (should match transferred count)")
        
        # Verify replace worked correctly
        if final_target_count == transferred_count:
            print("✅ REPLACE mode working correctly - target pane was cleared and repopulated")
            
            # Check for provenance
            provenance_count = sum(1 for msg in final_target_pane.get('messages', []) if msg.get('provenance'))
            print(f"✅ {provenance_count} messages have provenance tracking")
            
            print("\n🎉 Replace mode test PASSED!")
            return True
        else:
            print(f"❌ REPLACE mode failed - expected {transferred_count} messages, got {final_target_count}")
            print("❌ Messages were appended instead of replaced")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_replace_mode()
    if not success:
        print("\n❌ Replace mode test FAILED!")
        exit(1)
    else:
        print("\n✅ Replace mode test PASSED!")
        exit(0)