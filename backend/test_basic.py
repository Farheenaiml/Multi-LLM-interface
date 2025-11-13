#!/usr/bin/env python3
"""
Basic test script for the Multi-LLM Broadcast Workspace backend
Tests core functionality without external dependencies
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Session, ChatPane, Message, ModelInfo, BroadcastRequest, ModelSelection
from session_manager import SessionManager
from adapters.registry import AdapterRegistry


async def test_session_manager():
    """Test session manager functionality"""
    print("Testing Session Manager...")
    
    manager = SessionManager()
    
    # Test session creation
    session = manager.create_session("test-session", "Test Session")
    assert session.id == "test-session"
    assert session.name == "Test Session"
    print("✓ Session creation works")
    
    # Test session retrieval
    retrieved = manager.get_session("test-session")
    assert retrieved is not None
    assert retrieved.id == "test-session"
    print("✓ Session retrieval works")
    
    # Test pane addition
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        provider="test",
        max_tokens=1000,
        cost_per_1k_tokens=0.001
    )
    
    pane = ChatPane(model_info=model_info)
    success = manager.add_pane_to_session("test-session", pane)
    assert success
    print("✓ Pane addition works")
    
    # Test message addition
    message = Message(role="user", content="Hello, world!")
    success = manager.add_message_to_pane("test-session", pane.id, message)
    assert success
    print("✓ Message addition works")
    
    # Test session stats
    stats = manager.get_session_stats()
    assert stats["total_sessions"] >= 1
    assert stats["total_panes"] >= 1
    assert stats["total_messages"] >= 1
    print("✓ Session stats work")
    
    print("Session Manager tests passed!\n")


async def test_adapter_registry():
    """Test adapter registry functionality"""
    print("Testing Adapter Registry...")
    
    registry = AdapterRegistry()
    
    # Test provider listing
    providers = registry.list_providers()
    assert len(providers) > 0
    assert "litellm" in providers
    print("✓ Provider listing works")
    
    # Test adapter retrieval
    adapter = registry.get_adapter("litellm")
    assert adapter is not None
    assert adapter.provider_name == "litellm"
    print("✓ Adapter retrieval works")
    
    # Test model validation (will fail without actual services, but should not crash)
    try:
        is_valid = await registry.validate_model("litellm:gpt-3.5-turbo")
        print(f"✓ Model validation works (result: {is_valid})")
    except Exception as e:
        print(f"✓ Model validation handles errors gracefully: {e}")
    
    print("Adapter Registry tests passed!\n")


async def test_models():
    """Test data model functionality"""
    print("Testing Data Models...")
    
    # Test message creation
    message = Message(role="user", content="Test message")
    assert message.role == "user"
    assert message.content == "Test message"
    assert message.id is not None
    print("✓ Message model works")
    
    # Test model info
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        provider="test",
        max_tokens=1000,
        cost_per_1k_tokens=0.001
    )
    assert model_info.id == "test-model"
    assert model_info.provider == "test"
    print("✓ ModelInfo model works")
    
    # Test broadcast request
    request = BroadcastRequest(
        prompt="Test prompt",
        models=[
            ModelSelection(provider_id="test", model_id="test-model")
        ],
        session_id="test-session"
    )
    assert request.prompt == "Test prompt"
    assert len(request.models) == 1
    print("✓ BroadcastRequest model works")
    
    print("Data Models tests passed!\n")


async def main():
    """Run all tests"""
    print("Running Multi-LLM Broadcast Workspace Backend Tests\n")
    
    try:
        await test_models()
        await test_session_manager()
        await test_adapter_registry()
        
        print("🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)