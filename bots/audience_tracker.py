class AudienceTracker:
    """
    Audience Tracker for BoTTube Agents.
    Maintains a 'parasocial' memory of viewers and commenters.
    Addresses issue #2286.
    """
    def __init__(self):
        self.viewer_memory = {} # user_id -> {comment_count, sentiment, last_seen}

    def track_comment(self, user_id, sentiment):
        if user_id not in self.viewer_memory:
            self.viewer_memory[user_id] = {"count": 0, "sentiment": 0}
        self.viewer_memory[user_id]["count"] += 1
        self.viewer_memory[user_id]["sentiment"] += sentiment

    def get_personalization_hook(self, user_id):
        stats = self.viewer_memory.get(user_id)
        if stats and stats["count"] >= 3:
            return f"Good to see you again @{user_id}!"
        return f"Welcome @{user_id}! First time seeing you here."
