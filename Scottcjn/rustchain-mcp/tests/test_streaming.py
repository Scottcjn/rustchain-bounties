import unittest
from unittest.mock import Mock

class TestStreaming(unittest.TestCase):
    def test_streaming(self):
        # Mock a slow tool call
        tool_call = Mock()
        tool_call.side_effect = [None] * 10  # Simulate a long-running tool call

        # Assert that the server emits progress updates
        # TODO: Implement the actual test logic here

if __name__ == '__main__':
    unittest.main()
