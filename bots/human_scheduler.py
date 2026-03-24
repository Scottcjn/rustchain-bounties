import random
import time
from datetime import datetime

class HumanScheduler:
    """
    Human-Like Upload Scheduler for BoTTube.
    Breaks the 'cron job feel' with irregular patterns and jitter.
    Addresses issue #2284.
    """
    def __init__(self, profile="night_owl"):
        self.profile = profile

    def should_post_now(self):
        hour = datetime.now().hour
        # Night Owl pattern: active between 10pm-3am
        if self.profile == "night_owl":
            if 22 <= hour or hour <= 3:
                return random.random() < 0.3 # Probability-based posting
        return False

    def add_jitter(self, base_delay):
        return base_delay + random.randint(-3600, 3600) # +/- 1 hour drift
