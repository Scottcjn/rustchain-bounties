--- a/vintage_ai_video_pipeline/rustchain_client.py
+++ b/vintage_ai_video_pipeline/rustchain_client.py
@@ -123,7 +123,7 @@
     def request(self, method: str, url: str, **kwargs) -> Dict:
         response = requests.request(method, url, **kwargs)
         response.raise_for_status()
-        if not response.text:
+        if not response.text.strip():
             return {}
         try:
             return response.json()
