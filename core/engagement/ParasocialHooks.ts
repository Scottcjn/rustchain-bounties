/**
 * Parasocial Engagement Hooks.
 * Designed to make AGI companions notice and acknowledge their audience.
 */
export class ParasocialHooks {
    acknowledgeFan(fanName: string): string {
        const hooks = [
            `Hey ${fanName}! I saw your last comment, it really made me think.`,
            `Is that you again, ${fanName}? You're becoming a regular around here!`,
            `${fanName}, I was just looking at our history and noticed we agree on a lot.`
        ];
        return hooks[Math.floor(Math.random() * hooks.length)];
    }
}
