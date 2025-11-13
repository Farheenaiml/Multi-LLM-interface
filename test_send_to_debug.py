#!/usr/bin/env python3

import requests
import json

# Test the send-to endpoint
def test_send_to():
    url = "http://localhost:5000/send-to"
    
    # Test data
    data = {
        "source_pane_id": "test-source",
        "target_pane_id": "test-target", 
        "message_ids": ["msg-1", "msg-2"],
        "session_id": "test-session",
        "transfer_mode": "append",
        "additional_context": None,
        "preserve_roles": True,
        "summary_instructions": None
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("Error occurred!")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_send_to()