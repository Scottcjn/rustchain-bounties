import pytest
from unittest.mock import MagicMock, patch
from clawrtc import ClawRTC, ClawRTCConfig
from clawrtc.session import Session
from clawrtc.message import Message


class TestClawRTCUnit:
    """Unit tests for the ClawRTC package"""
    
    def test_config_creation(self):
        """Test ClawRTCConfig creation"""
        config = ClawRTCConfig(
            server_url="ws://localhost:8080",
            api_key="test-key",
            max_retries=5,
            timeout=60
        )
        
        assert config.server_url == "ws://localhost:8080"
        assert config.api_key == "test-key"
        assert config.max_retries == 5
        assert config.timeout == 60
        
    def test_clawrtc_initialization(self):
        """Test ClawRTC initialization"""
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        assert clawrtc.config == config
        assert clawrtc._websocket is None
        assert clawrtc._is_connected is False
        assert clawrtc._message_queue == []
        
    def test_message_creation(self):
        """Test Message creation"""
        message = Message(
            type="test",
            data={"content": "Hello"},
            recipient="user1"
        )
        
        assert message.type == "test"
        assert message.data == {"content": "Hello"}
        assert message.recipient == "user1"
        assert message.sender is None
        
    def test_session_creation(self):
        """Test Session creation"""
        session = Session(
            id="test-session",
            participants=["user1", "user2"],
            session_type="video"
        )
        
        assert session.id == "test-session"
        assert session.participants == ["user1", "user2"]
        assert session.session_type == "video"
        
    @patch('clawrtc.ClawRTC._create_websocket')
    def test_websocket_creation(self, mock_create_websocket):
        """Test websocket creation"""
        mock_ws = MagicMock()
        mock_create_websocket.return_value = mock_ws
        
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        websocket = clawrtc._create_websocket()
        
        mock_create_websocket.assert_called_once()
        assert websocket == mock_ws
        
    def test_message_queue_operations(self):
        """Test message queue operations"""
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        # Test queue is empty initially
        assert len(clawrtc._message_queue) == 0
        
        # Add messages to queue
        message1 = Message(type="msg1", data={})
        message2 = Message(type="msg2", data={})
        
        clawrtc._queue_message(message1)
        clawrtc._queue_message(message2)
        
        assert len(clawrtc._message_queue) == 2
        assert clawrtc._message_queue[0] == message1
        assert clawrtc._message_queue[1] == message2
        
        # Test dequeue
        dequeued = clawrtc._dequeue_message()
        assert dequeued == message1
        assert len(clawrtc._message_queue) == 1
        
    def test_event_handler_registration(self):
        """Test event handler registration"""
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        # Mock handler
        handler = MagicMock()
        
        # Register handler
        clawrtc.on("message", handler)
        
        # Verify handler was registered
        assert "message" in clawrtc._event_handlers
        assert handler in clawrtc._event_handlers["message"]
        
    def test_event_handler_removal(self):
        """Test event handler removal"""
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        # Mock handler
        handler = MagicMock()
        
        # Register and remove handler
        clawrtc.on("message", handler)
        clawrtc.off("message", handler)
        
        # Verify handler was removed
        assert "message" in clawrtc._event_handlers
        assert handler not in clawrtc._event_handlers["message"]
        
    def test_connection_state_tracking(self):
        """Test connection state tracking"""
        config = ClawRTCConfig(server_url="ws://test.com")
        clawrtc = ClawRTC(config)
        
        # Initial state
        assert clawrtc._is_connected is False
        
        # Set connected state
        clawrtc._set_connected(True)
        assert clawrtc._is_connected is True
        
        # Set disconnected state
        clawrtc._set_connected(False)
        assert clawrtc._is_connected is False
        
    def test_retry_configuration(self):
        """Test retry configuration"""
        config = ClawRTCConfig(
            server_url="ws://test.com",
            max_retries=3,
            timeout=10
        )
        
        assert config.max_retries == 3
        assert config.timeout == 10
        
    def test_invalid_config(self):
        """Test invalid configuration handling"""
        with pytest.raises(ValueError):
            ClawRTCConfig(server_url="")
            
        with pytest.raises(ValueError):
            ClawRTCConfig(server_url="invalid-url")
            
        with pytest.raises(ValueError):
            ClawRTCConfig(server_url="ws://test.com", max_retries=-1)
