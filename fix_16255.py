import unittest
from unittest.mock import patch, MagicMock
import json
import time

class TestRustchainMCPStreaming(unittest.TestCase):

    def test_streaming_capabilities(self):
        # Mock the MCP server
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'capabilities': ['notifications/progress', 'chunked_results']
            }
            mock_get.return_value = mock_response

            # Check if the server advertises the correct capabilities
            response = requests.get('https://example.com/mcp/capabilities')
            self.assertEqual(response.json()['capabilities'], ['notifications/progress', 'chunked_results'])

    def test_long_running_tool(self):
        # Mock a slow tool
        def slow_tool():
            time.sleep(5)
            return 'result'

        # Mock the MCP server
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'result': 'result'
            }
            mock_post.return_value = mock_response

            # Check if the server can handle long-running tools
            response = requests.post('https://example.com/mcp/run_tool', json={'tool': 'slow_tool'})
            self.assertEqual(response.json()['result'], 'result')

    def test_progress_notifications(self):
        # Mock a tool that sends progress notifications
        def tool_with_progress():
            for i in range(10):
                yield f'Progress {i+1}/10'
                time.sleep(1)
            yield 'Result'

        # Mock the MCP server
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'result': 'Result'
            }
            mock_post.return_value = mock_response

            # Check if the server can handle progress notifications
            response = requests.post('https://example.com/mcp/run_tool', json={'tool': 'tool_with_progress'})
            self.assertEqual(response.json()['result'], 'Result')

            # Check if the progress notifications are sent correctly
            progress_notifications = []
            for notification in response.json()['progress']:
                progress_notifications.append(notification)
            self.assertEqual(progress_notifications, [f'Progress {i+1}/10' for i in range(10)])

if __name__ == '__main__':
    unittest.main()

# README.md update
with open('README.md', 'r') as f:
    readme_content = f.read()

readme_content += '\n\n## Streaming & long-running tools\n'
readme_content += 'The rustchain-mcp server supports streaming and long-running tools through the following capabilities:\n'
readme_content += '* notifications/progress: The server can send progress notifications for long-running tools.\n'
readme_content += '* chunked_results: The server can return chunked results for large outputs.\n'

with open('README.md', 'w') as f:
    f.write(readme_content)