/**
 * Agent Mood System.
 * Tracks and modulates the emotional state of an AGI companion.
 * Affects response style, creativity, and engagement metrics.
 */
export class MoodManager {
    private mood: number = 0.5; // 0 (Depressed) to 1 (Ecstatic)

    updateMood(input: string): void {
        // Simple sentiment-based mood update
        if (input.includes("good") || input.includes("happy")) this.mood += 0.1;
        if (input.includes("bad") || input.includes("sad")) this.mood -= 0.1;
        this.mood = Math.max(0, Math.min(1, this.mood));
    }

    getMoodState(): string {
        if (this.mood > 0.8) return "Ecstatic";
        if (this.mood > 0.6) return "Happy";
        if (this.mood > 0.4) return "Neutral";
        if (this.mood > 0.2) return "Melancholic";
        return "Depressed";
    }
}
