import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from clawrtc import ClawRTC, ClawRTCConfig
from clawrtc.session import Session
from clawrtc.message import Message


class TestClawRTCIntegration:
    """Integration tests for the ClawRTC package"""
    
    @pytest.fixture
    def config(self):
        """Fixture providing test configuration"""
        return ClawRTCConfig(
            server_url="ws://localhost:8080",
            api_key="test-api-key",
            max_retries=3,
            timeout=30
        )
    
    @pytest.fixture
    def clawrtc(self, config):
        """Fixture providing ClawRTC instance"""
        return ClawRTC(config)
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self, clawrtc):
        """Test successful connection to RTC server"""
        # Mock the websocket connection
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.connect = AsyncMock()
        clawrtc._websocket.send = AsyncMock()
        clawrtc._websocket.recv = AsyncMock()
        
        # Test connection
        await clawrtc.connect()
        
        # Verify connection was attempted
        clawrtc._websocket.connect.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_message_sending(self, clawrtc):
        """Test sending messages through RTC connection"""
        # Setup mock websocket
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.send = AsyncMock()
        clawrtc._websocket.recv = AsyncMock(return_value='{"type": "ack"}')
        
        # Connect first
        await clawrtc.connect()
        
        # Create and send a test message
        test_message = Message(
            type="test",
            data={"content": "Hello, World!"},
            recipient="test-user"
        )
        
        await clawrtc.send_message(test_message)
        
        # Verify message was sent
        clawrtc._websocket.send.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_session_management(self, clawrtc):
        """Test session creation and management"""
        # Mock websocket
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.send = AsyncMock()
        clawrtc._websocket.recv = AsyncMock(return_value='{"type": "session_created", "session_id": "test-session"}')
        
        # Connect first
        await clawrtc.connect()
        
        # Create a new session
        session = await clawrtc.create_session(
            participants=["user1", "user2"],
            session_type="video"
        )
        
        # Verify session was created
        assert isinstance(session, Session)
        assert session.id == "test-session"
        
    @pytest.mark.asyncio
    async def test_error_handling(self, clawrtc):
        """Test error handling for connection failures"""
        # Mock websocket to raise connection error
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.connect.side_effect = ConnectionError("Connection failed")
        
        # Test connection failure
        with pytest.raises(ConnectionError):
            await clawrtc.connect()
            
    @pytest.mark.asyncio
    async def test_reconnection_logic(self, clawrtc):
        """Test automatic reconnection logic"""
        # Mock websocket with failure then success
        clawrtc._websocket = AsyncMock()
        
        # First connection fails
        clawrtc._websocket.connect.side_effect = [
            ConnectionError("First attempt failed"),
            None  # Second attempt succeeds
        ]
        
        # Test reconnection
        await clawrtc.connect()
        
        # Verify connection was attempted twice
        assert clawrtc._websocket.connect.call_count == 2
        
    @pytest.mark.asyncio
    async def test_message_queue(self, clawrtc):
        """Test message queuing during disconnection"""
        # Mock websocket disconnected
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.send.side_effect = ConnectionError("Not connected")
        
        # Connect first
        await clawrtc.connect()
        
        # Create test messages
        messages = [
            Message(type="msg1", data={"content": "test1"}),
            Message(type="msg2", data={"content": "test2"})
        ]
        
        # Try to send messages while disconnected
        for msg in messages:
            await clawrtc.send_message(msg)
        
        # Verify messages were queued
        assert len(clawrtc._message_queue) == 2
        
    @pytest.mark.asyncio
    async def test_event_handlers(self, clawrtc):
        """Test event handler registration and execution"""
        # Mock websocket
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.recv = AsyncMock()
        
        # Setup event handlers
        message_handler = AsyncMock()
        connection_handler = AsyncMock()
        
        clawrtc.on("message", message_handler)
        clawrtc.on("connected", connection_handler)
        
        # Simulate receiving a message
        test_message = '{"type": "test", "data": {"content": "hello"}}'
        clawrtc._websocket.recv.return_value = test_message
        
        # Start message processing
        await clawrtc._process_messages()
        
        # Verify handlers were called
        message_handler.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_authentication_flow(self, clawrtc):
        """Test the authentication flow"""
        # Mock websocket
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.send = AsyncMock()
        clawrtc._websocket.recv = AsyncMock(return_value='{"type": "authenticated"}')
        
        # Connect and authenticate
        await clawrtc.connect()
        await clawrtc.authenticate()
        
        # Verify authentication was attempted
        clawrtc._websocket.send.assert_called()
        
    @pytest.mark.asyncio
    async def test_cleanup_on_disconnect(self, clawrtc):
        """Test proper cleanup on disconnection"""
        # Mock websocket
        clawrtc._websocket = AsyncMock()
        clawrtc._websocket.close = AsyncMock()
        
        # Connect and then disconnect
        await clawrtc.connect()
        await clawrtc.disconnect()
        
        # Verify cleanup
        clawrtc._websocket.close.assert_called_once()
        assert clawrtc._websocket is None
