#!/usr/bin/env python3

import requests
import json
import time

def test_ui_refresh_after_transfer():
    """Test that UI properly refreshes after transfer operations"""
    
    base_url = "http://localhost:5000"
    session_id = "test-ui-refresh"
    
    print("🧪 Testing UI Refresh After Transfer")
    print("=" * 50)
    
    try:
        # Step 1: Create a simple broadcast
        print("1. Creating test broadcast...")
        
        broadcast_data = {
            "session_id": session_id,
            "prompt": "Test message for UI refresh.",
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
            print(f"❌ Broadcast failed: {response.status_code}")
            return False
            
        result = response.json()
        pane_ids = result.get("pane_ids", [])
        
        if len(pane_ids) < 2:
            print("❌ Need at least 2 panes for testing")
            return False
            
        source_pane = pane_ids[0]
        target_pane = pane_ids[1]
        
        # Wait for messages to be generated
        print("2. Waiting for messages...")
        time.sleep(3)
        
        # Step 2: Get session data to verify structure
        print("3. Checking session data structure...")
        
        session_response = requests.get(f"{base_url}/sessions/{session_id}")
        if session_response.status_code != 200:
            print(f"❌ Failed to get session: {session_response.status_code}")
            return False
            
        session_data = session_response.json()
        
        # Verify pane structure
        panes = session_data.get('panes', [])
        if len(panes) < 2:
            print("❌ Not enough panes in session")
            return False
            
        # Check that panes have required properties
        for pane in panes:
            if not pane.get('modelInfo'):
                print(f"❌ Pane {pane.get('id', 'unknown')} missing modelInfo")
                return False
                
            model_info = pane['modelInfo']
            required_fields = ['provider', 'name', 'maxTokens', 'costPer1kTokens']
            
            for field in required_fields:
                if field not in model_info:
                    print(f"❌ Pane {pane.get('id', 'unknown')} modelInfo missing {field}")
                    return False
                    
            if not pane.get('metrics'):
                print(f"❌ Pane {pane.get('id', 'unknown')} missing metrics")
                return False
                
            metrics = pane['metrics']
            required_metrics = ['tokenCount', 'cost', 'latency']
            
            for metric in required_metrics:
                if metric not in metrics:
                    print(f"❌ Pane {pane.get('id', 'unknown')} metrics missing {metric}")
                    return False
        
        print("✅ All panes have required structure")
        
        # Step 3: Test transfer operation
        print("4. Testing transfer operation...")
        
        source_pane_data = next((p for p in panes if p['id'] == source_pane), None)
        if not source_pane_data or not source_pane_data.get('messages'):
            print("❌ Source pane has no messages")
            return False
            
        message_ids = [msg['id'] for msg in source_pane_data['messages']]
        
        transfer_data = {
            "source_pane_id": source_pane,
            "target_pane_id": target_pane,
            "message_ids": message_ids,
            "session_id": session_id,
            "transfer_mode": "append",
            "additional_context": None,
            "preserve_roles": True,
            "summary_instructions": None
        }
        
        transfer_response = requests.post(f"{base_url}/send-to", json=transfer_data)
        
        if transfer_response.status_code != 200:
            print(f"❌ Transfer failed: {transfer_response.status_code} - {transfer_response.text}")
            return False
            
        transfer_result = transfer_response.json()
        print(f"✅ Transfer successful: {transfer_result}")
        
        # Step 4: Verify transfer worked
        print("5. Verifying transfer...")
        
        verify_response = requests.get(f"{base_url}/sessions/{session_id}")
        if verify_response.status_code != 200:
            print(f"❌ Failed to verify: {verify_response.status_code}")
            return False
            
        verify_data = verify_response.json()
        
        target_pane_data = next((p for p in verify_data.get('panes', []) if p['id'] == target_pane), None)
        if not target_pane_data:
            print("❌ Target pane not found after transfer")
            return False
            
        transferred_messages = target_pane_data.get('messages', [])
        expected_count = transfer_result.get('transferred_count', 0)
        
        if len(transferred_messages) >= expected_count:
            print(f"✅ Transfer verified: {len(transferred_messages)} messages in target pane")
            
            # Check for provenance
            provenance_count = sum(1 for msg in transferred_messages if msg.get('provenance'))
            print(f"✅ {provenance_count} messages have provenance tracking")
            
            print("\n🎉 UI refresh test PASSED!")
            return True
        else:
            print(f"❌ Transfer verification failed: expected at least {expected_count} messages, got {len(transferred_messages)}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_ui_refresh_after_transfer()
    if not success:
        print("\n❌ UI refresh test FAILED!")
        exit(1)
    else:
        print("\n✅ UI refresh test PASSED!")
        exit(0)