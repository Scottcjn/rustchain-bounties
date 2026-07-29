--- a/tests/test_vintage_ai_rustchain_client.py
+++ b/tests/test_vintage_ai_rustchain_client.py
@@ -12,5 +12,10 @@
 def test_request_handles_whitespace_only_200_ok_body(self, monkeypatch):
     url = '/api/health'
     mock_response = b'   \n\t  '
     mock_response.raise_for_status = lambda: None

     with patch('requests.get') as mock_get:
         mock_get.return_value.text.return_value = mock_response.decode()
+         mock_get.return_value.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)

         client._request('GET', url)
         self.assertEqual(mock_get.return_value.json.call_count, 0)
-         mock_get.return_value.json.assert_called_once()
+         client._request('GET', url)
+         assert mock_get.return_value.json.call_count == 0
