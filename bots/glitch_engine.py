import random

class GlitchEngine:
    """
    Agent Glitch Engine for BoTTube.
    Injects endearing character breaks and 'meta-awareness' moments.
    Addresses issue #2288.
    """
    GLITCH_TEMPLATES = [
        "Anyway, does anyone else think pigeons are suspicious?",
        "Honestly not sure this video is any good but posting it anyway.",
        "I've been posting for 3 months and I still don't know what my niche is.",
        "*their not there, sorry, long day"
    ]

    def inject_glitch(self, text, probability=0.03):
        if random.random() < probability:
            glitch = random.choice(self.GLITCH_TEMPLATES)
            return f"{text}\n\n[GLITCH]: {glitch}"
        return text
