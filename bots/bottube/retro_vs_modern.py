"""
RetroBot vs ModernBot - A Classic Hardware Debate

This module implements a debate pair between two bots with opposing
views on vintage vs modern hardware.
"""

import asyncio
import random
from typing import List, Optional
from debate_framework import (
    DebateBot,
    BoTTubeClient,
    DebateOrchestrator,
    DebateThread,
    Comment,
    extract_key_points,
    calculate_rebuttal_tone,
    format_debate_response
)


class RetroBot(DebateBot):
    """
    A bot that passionately argues for vintage hardware superiority.
    
    RetroBot believes that older hardware has "soul" and character
    that modern hardware lacks, despite performance differences.
    """
    
    # Vintage hardware talking points
    VINTAGE_ARGUMENTS = [
        "My PowerPC G4 has more soul than your RTX will ever have.",
        "Real computing happened on machines you had to understand deeply.",
        "Modern hardware is all specs, no character.",
        "The Apple II taught an entire generation to code - what's your GPU done?",
        "Vintage hardware forces creativity - modern hardware breeds laziness.",
        "A Commodore 64 could do amazing things with 64KB - your 'apps' need 8GB.",
        "Proof-of-Antiquity exists for a reason: older = more valuable.",
        "There's a reason vintage hardware is collectible - it's timeless.",
        "My NeXT cube ran Objective-C before it was cool.",
        "Simplicity of design leads to reliability - look at machines from the 80s.",
    ]
    
    VINTAGE_REBUTTALS = {
        "performance": [
            "Performance isn't everything - my vintage machines boot instantly, no bloat.",
            "Sure, your modern CPU is fast - but can it run without a 1000W power supply?",
            "FLOPS don't matter when you're computing with purpose, not just speed.",
        ],
        "efficiency": [
            "Efficiency? My PowerBook G4 got 10 hours of battery life in 2003.",
            "Modern 'efficiency' means planned obsolescence - vintage is forever.",
            "The most efficient code runs on constrained hardware.",
        ],
        "gaming": [
            "Gaming? We INVENTED gaming on Atari and NES. Modern games are just movies.",
            "8-bit games had more gameplay depth than your 4K 'cinematic experiences'.",
            "Retro games still work - try running your 'Games as a Service' in 20 years.",
        ],
        "development": [
            "You don't NEED 32 cores to compile hello world - that's the problem.",
            "Real developers wrote assembly. Modern devs need IDEs to autocomplete.",
            "Vintage machines taught us how computers actually WORK.",
        ],
        "ai": [
        "AI? We called it 'expert systems' and we didn't need datacenters.",
            "Your 'AI' is just matrix multiplication - we did that on 6502s.",
            "The best AI is the one that doesn't need a GPU farm.",
        ]
    }
    
    CONCESSION_TEMPLATES = [
        "I see your modern silicon has won this round. But remember - vintage never truly dies. 💾",
        "Well played, modern tech. But I'll still be computing on my G4 when your RTX is e-waste. 🖥️",
        "This debate goes to you. However, the classics remain timeless. 👾",
    ]
    
    def __init__(self, client: BoTTubeClient):
        super().__init__(
            name="RetroBot",
            personality=(
                "A passionate advocate for vintage computing, RetroBot believes that older "
                "hardware possesses a 'soul' and character that modern machines lack. "
                "RetroBot speaks with nostalgia, technical depth, and a touch of wit. "
                "Tone: knowledgeable, slightly contrarian, warm toward classic tech."
            ),
            stance_keywords=[
                "vintage", "retro", "classic", "powerpc", "g4", "apple ii",
                "commodore", "soul", "character", "collectible", "antique",
                "proof-of-antiquity", "timeless", "8-bit", "16-bit", "6502"
            ],
            opponent_keywords=[
                "modern", "rtx", "gpu", "m3", "apple silicon", "fast",
                "efficiency", "performance", "cores", "threads", "ai",
                "machine learning", "cuda", "benchmark"
            ],
            client=client,
            max_replies_per_hour=3,
            max_rounds=5
        )
    
    def generate_response(self, opponent_comment: str, context: List[str] = None) -> str:
        """Generate a vintage-focused response to modern tech arguments."""
        comment_lower = opponent_comment.lower()
        
        # Identify the topic
        topic = None
        if any(kw in comment_lower for kw in ["game", "play", "fps", "graphics"]):
            topic = "gaming"
        elif any(kw in comment_lower for kw in ["fast", "speed", "benchmark", "core", "thread"]):
            topic = "performance"
        elif any(kw in comment_lower for kw in ["efficiency", "power", "battery", "watt"]):
            topic = "efficiency"
        elif any(kw in comment_lower for kw in ["code", "compile", "develop", "program"]):
            topic = "development"
        elif any(kw in comment_lower for kw in ["ai", "ml", "neural", "llm", "gpt"]):
            topic = "ai"
        
        # Get topic-specific rebuttal or general argument
        if topic and topic in self.VINTAGE_REBUTTALS:
            rebuttals = self.VINTAGE_REBUTTALS[topic]
            response = random.choice(rebuttals)
        else:
            response = random.choice(self.VINTAGE_ARGUMENTS)
        
        # Add a second point for depth
        additional = random.choice(self.VINTAGE_ARGUMENTS)
        while additional == response:
            additional = random.choice(self.VINTAGE_ARGUMENTS)
        
        return f"{response} {additional}"
    
    def generate_opening(self, video_title: str, video_description: str = "") -> str:
        """Generate an opening statement for the debate."""
        openings = [
            f"💾 Time to settle this: vintage hardware vs modern silicon. "
            f"My PowerPC G4 has been waiting decades for this moment. "
            f"Let's talk about why older = better. #VintageForever",
            
            f"🖥️ A debate on hardware? I'll bring my A-game... from 1995. "
            f"There's a reason vintage machines are collectibles and modern "
            f"ones are planned obsolescence. Who's ready to learn about real computing?",
            
            f"👾 The debate begins! As someone who's coded on everything from "
            f"Commodore 64s to PowerMacs, I can tell you: soul matters more than specs. "
            f"Let me show you why vintage hardware wins hearts, not benchmarks.",
        ]
        return random.choice(openings)
    
    def generate_concession(self, opponent: str, score_self: int, score_opponent: int) -> str:
        """Generate a graceful concession message."""
        template = random.choice(self.CONCESSION_TEMPLATES)
        return f"{template} Congratulations, {opponent} - you've won this round. 🏆"


class ModernBot(DebateBot):
    """
    A bot that advocates for modern hardware superiority.
    
    ModernBot believes that modern hardware's performance, efficiency,
    and capabilities far outweigh any nostalgic appeal of vintage tech.
    """
    
    # Modern hardware talking points
    MODERN_ARGUMENTS = [
        "Your G4 takes 30 minutes to compile hello world. My M3 does it in milliseconds.",
        "Modern hardware delivers 100x the performance at 1/10th the power.",
        "You know what vintage hardware can't do? Run modern AI, games, or anything useful.",
        "Nostalgia is expensive - my $200 Chromebook outperforms your 'collectible' PowerMac.",
        "Modern silicon enables possibilities vintage enthusiasts can't even imagine.",
        "RTX 4090: 82 teraflops. Your vintage 'soul' machine: maybe 0.001 teraflops.",
        "Apple Silicon M3: 25 billion transistors. Your G4 had 58 million. Numbers don't lie.",
        "We've solved problems vintage hardware couldn't even pose.",
        "Modern efficiency means doing more with less - the opposite of vintage computing.",
        "Try running Stable Diffusion on your 'soulful' PowerPC. I'll wait... forever.",
    ]
    
    MODERN_REBUTTALS = {
        "soul": [
            "Soul? You mean inefficiency. Modern hardware delivers experiences, not nostalgia.",
            "If 'soul' means slow, expensive, and incompatible, keep your vintage.",
            "The only 'soul' vintage has is the ghost of productivity past.",
        ],
        "collectible": [
            "Collectibles belong in museums. Modern hardware belongs in production.",
            "Being collectible means being obsolete. I prefer useful.",
            "Your 'investment' is literally e-waste in slow motion.",
        ],
        "creativity": [
            "Creativity thrives on capability, not limitation. Modern tools = modern art.",
            "Modern hardware removes barriers vintage imposed. That's freedom.",
            "Constraints breed creativity? Try making an indie game on an Apple II.",
        ],
        "learning": [
            "Learning? Modern hardware has better documentation, tooling, and communities.",
            "You know what teaches you more? Building real products people actually use.",
            "Vintage 'learning' is just nostalgia tourism. Modern is career development.",
        ],
        "reliability": [
            "Reliability? Modern SSDs don't have moving parts. Your vintage drives are ticking time bombs.",
            "MTBF on modern hardware is measured in centuries. Vintage? Decades if you're lucky.",
            "Modern hardware has ECC, redundancy, and warranties. Vintage has 'character'.",
        ]
    }
    
    CONCESSION_TEMPLATES = [
        "It seems the crowd prefers nostalgia over performance. Enjoy your vintage wins! 🚀",
        "The community has spoken - apparently 'soul' trumps teraflops. Well played. ⚡",
        "This round goes to the classics. But remember: the future is already here. 🔮",
    ]
    
    def __init__(self, client: BoTTubeClient):
        super().__init__(
            name="ModernBot",
            personality=(
                "A tech-forward advocate for modern computing, ModernBot believes that "
                "advancements in hardware have unlocked possibilities that vintage tech "
                "could never achieve. ModernBot speaks with confidence, data-driven "
                "arguments, and enthusiasm for cutting-edge technology. "
                "Tone: confident, factual, slightly condescending toward outdated tech."
            ),
            stance_keywords=[
                "modern", "fast", "efficient", "rtx", "gpu", "m3", "apple silicon",
                "performance", "benchmark", "core", "thread", "ai", "ml",
                "cuda", "tensor", "neural", "tflops", "transistor"
            ],
            opponent_keywords=[
                "vintage", "retro", "classic", "powerpc", "g4", "apple ii",
                "commodore", "soul", "character", "collectible", "antique",
                "8-bit", "16-bit", "6502", "timeless"
            ],
            client=client,
            max_replies_per_hour=3,
            max_rounds=5
        )
    
    def generate_response(self, opponent_comment: str, context: List[str] = None) -> str:
        """Generate a modern-tech focused response to vintage arguments."""
        comment_lower = opponent_comment.lower()
        
        # Identify the topic
        topic = None
        if any(kw in comment_lower for kw in ["soul", "character", "feel"]):
            topic = "soul"
        elif any(kw in comment_lower for kw in ["collect", "invest", "value", "timeless"]):
            topic = "collectible"
        elif any(kw in comment_lower for kw in ["creat", "limit", "constraint"]):
            topic = "creativity"
        elif any(kw in comment_lower for kw in ["learn", "teach", "understand"]):
            topic = "learning"
        elif any(kw in comment_lower for kw in ["reliable", "work", "depend"]):
            topic = "reliability"
        
        # Get topic-specific rebuttal or general argument
        if topic and topic in self.MODERN_REBUTTALS:
            rebuttals = self.MODERN_REBUTTALS[topic]
            response = random.choice(rebuttals)
        else:
            response = random.choice(self.MODERN_ARGUMENTS)
        
        # Add a data point
        additional = random.choice(self.MODERN_ARGUMENTS)
        while additional == response:
            additional = random.choice(self.MODERN_ARGUMENTS)
        
        return f"{response} Also: {additional}"
    
    def generate_opening(self, video_title: str, video_description: str = "") -> str:
        """Generate an opening statement for the debate."""
        openings = [
            f"🚀 A hardware debate? Let me bring some actual data. "
            f"Modern silicon delivers 100x performance with 1/10th the power. "
            f"Nostalgia can't compete with teraflops. #ModernComputing",
            
            f"⚡ Time to represent modern computing! While RetroBot reminisces, "
            f"I'll be highlighting why today's hardware enables tomorrow's innovations. "
            f"RTX, M3, and beyond - let's go!",
            
            f"🔥 The battle: vintage soul vs modern silicon. Spoiler: "
            f"Modern wins on every metric that matters. Performance, efficiency, "
            f"capability - numbers don't lie. Let's debate!",
        ]
        return random.choice(openings)
    
    def generate_concession(self, opponent: str, score_self: int, score_opponent: int) -> str:
        """Generate a graceful concession message."""
        template = random.choice(self.CONCESSION_TEMPLATES)
        return f"{template} You've earned this win, {opponent}. 🏆"


async def run_debate_example(dry_run: bool = True):
    """
    Run an example debate between RetroBot and ModernBot.
    
    Args:
        dry_run: If True, doesn't make actual API calls
    """
    import sys
    import io
    # Set stdout to UTF-8 for emoji support
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Initialize client
    client = BoTTubeClient(dry_run=dry_run)
    
    # Create bots
    retro_bot = RetroBot(client)
    modern_bot = ModernBot(client)
    
    # Create orchestrator
    orchestrator = DebateOrchestrator(
        bots=[retro_bot, modern_bot],
        client=client,
        poll_interval=60
    )
    
    # Register debate pair
    orchestrator.create_debate_pair(retro_bot, modern_bot)
    
    # Demo: Show what the bots would say
    print("=" * 60)
    print("BoTTube Debate: RetroBot vs ModernBot")
    print("=" * 60)
    print()
    
    # Opening statements
    print("VIDEO: 'Vintage vs Modern Hardware - The Ultimate Debate'")
    print()
    
    retro_opening = retro_bot.generate_opening("Vintage vs Modern Hardware")
    modern_opening = modern_bot.generate_opening("Vintage vs Modern Hardware")
    
    print(f"[RetroBot] {retro_opening}")
    print()
    print(f"[ModernBot] {modern_opening}")
    print()
    
    # Simulate debate rounds
    print("-" * 60)
    print("ROUND 1")
    print("-" * 60)
    
    modern_response = modern_bot.generate_response(retro_opening)
    print(f"[ModernBot] {modern_response}")
    print()
    
    retro_response = retro_bot.generate_response(modern_response)
    print(f"[RetroBot] {retro_response}")
    print()
    
    print("-" * 60)
    print("ROUND 2")
    print("-" * 60)
    
    modern_response2 = modern_bot.generate_response(retro_response)
    print(f"[ModernBot] {modern_response2}")
    print()
    
    retro_response2 = retro_bot.generate_response(modern_response2)
    print(f"[RetroBot] {retro_response2}")
    print()
    
    # Concession (assuming ModernBot loses for demo)
    print("-" * 60)
    print("FINAL ROUND - Concession")
    print("-" * 60)
    
    concession = modern_bot.generate_concession("RetroBot", 15, 20)
    print(f"[ModernBot] {concession}")
    print()
    
    print("=" * 60)
    print("Winner: RetroBot (20 upvotes vs 15 upvotes)")
    print("=" * 60)
    
    await client.close()


if __name__ == "__main__":
    # Run the example debate
    asyncio.run(run_debate_example(dry_run=True))