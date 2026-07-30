--- a/bottube/routes.py
+++ b/bottube/routes.py
@@ -123,7 +123,7 @@
     try:
         # Existing code to handle referral routes
         if not isinstance(data, dict):
-            return {"error": "Invalid JSON"}, 500
+            return {"error": "Invalid JSON"}, 400

--- a/bottube/feeds.py
+++ b/bottube/feeds.py
@@ -56,7 +56,7 @@
     try:
         # Existing code to handle feed page
         if page > max_pages:
-            return {"error": "Page overflow"}, 500
+            return {"error": "Page overflow"}, 400

--- a/bottube/agents.py
+++ b/bottube/agents.py
@@ -210,7 +210,7 @@
     try:
         # Existing code to handle agent names
         if not validate_agent_name(agent_name):
-            return {"error": "Invalid agent name"}, 500
+            return {"error": "Invalid agent name"}, 400
