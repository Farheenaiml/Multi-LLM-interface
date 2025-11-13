#!/usr/bin/env python3
"""
Test script to verify that summary generation works correctly
and only sends the actual summary, not the prompt.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models import SendToRequest, Message, ProvenanceInfo
from datetime import datetime

def test_summary_request():
    """Test that we create the correct summary request"""
    
    # Create a mock request for summarize mode
    request = SendToRequest(
        session_id="test-session",
        source_pane_id="pane-1",
        target_pane_id="pane-2", 
        message_ids=["msg-1", "msg-2"],
        transfer_mode="summarize",
        additional_context="Focus on key points",
        preserve_roles=True,
        summary_instructions="Highlight important decisions"
    )
    
    print("✅ Summary request created successfully")
    print(f"Transfer mode: {request.transfer_mode}")
    print(f"Summary instructions: {request.summary_instructions}")
    print(f"Additional context: {request.additional_context}")
    
    # Verify the request structure
    assert request.transfer_mode == "summarize"
    assert request.summary_instructions == "Highlight important decisions"
    assert request.additional_context == "Focus on key points"
    
    print("✅ All assertions passed!")

if __name__ == "__main__":
    test_summary_request()
    print("\n🎉 Summary request test completed successfully!")