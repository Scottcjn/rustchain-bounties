/**
 * BoTTube Keyboard Shortcuts Module
 * Issue: Scottcjn/rustchain-bounties#2140 - $5 RTC
 * Wallet: RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5
 * 
 * YouTube-style keyboard shortcuts for video player.
 * Pure JavaScript, no frameworks.
 * 
 * Shortcuts:
 * - Space/K: Play/Pause
 * - J/L: Seek back/forward 10s
 * - M: Mute toggle
 * - F: Fullscreen toggle
 * - Arrow Left/Right: Seek 5s
 * - Arrow Up/Down: Volume
 */

export interface KeyboardShortcutsOptions {
    videoElement: HTMLVideoElement;
    containerElement?: HTMLElement;
    seekBackwardSeconds?: number;
    seekForwardSeconds?: number;
    volumeStep?: number;
    overlayDuration?: number;
}

export interface ShortcutAction {
    key: string;
    description: string;
    icon: string;
}

const DEFAULT_SEEK_SECONDS = 10;
const DEFAULT_SEEK_SHORT = 5;
const DEFAULT_VOLUME_STEP = 0.1;
const DEFAULT_OVERLAY_DURATION = 800;

/**
 * Check if the user is typing in an input field (comment box, etc.)
 */
function isTypingInInput(): boolean {
    const activeElement = document.activeElement;
    if (!activeElement) return false;
    
    const tagName = activeElement.tagName.toLowerCase();
    if (tagName === 'input' || tagName === 'textarea' || tagName === 'select') {
        return true;
    }
    
    // Check for contenteditable elements
    if (activeElement.getAttribute('contenteditable') === 'true') {
        return true;
    }
    
    return false;
}

/**
 * Create the overlay indicator element
 */
function createOverlayElement(): HTMLElement {
    const overlay = document.createElement('div');
    overlay.className = 'bottube-shortcut-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.75);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        opacity: 0;
        transition: opacity 0.15s ease-in-out;
        pointer-events: none;
        z-index: 1000;
    `;
    document.body.appendChild(overlay);
    return overlay;
}

export class KeyboardShortcuts {
    private video: HTMLVideoElement;
    private container: HTMLElement | null;
    private overlay: HTMLElement;
    private overlayTimeout: number | null = null;
    private seekBackward: number;
    private seekForward: number;
    private volumeStep: number;
    private overlayDuration: number;
    private boundKeyHandler: (e: KeyboardEvent) => void;
    private isEnabled: boolean = true;

    constructor(options: KeyboardShortcutsOptions) {
        this.video = options.videoElement;
        this.container = options.containerElement || this.video.parentElement as HTMLElement;
        this.seekBackward = options.seekBackwardSeconds ?? DEFAULT_SEEK_SECONDS;
        this.seekForward = options.seekForwardSeconds ?? DEFAULT_SEEK_SECONDS;
        this.volumeStep = options.volumeStep ?? DEFAULT_VOLUME_STEP;
        this.overlayDuration = options.overlayDuration ?? DEFAULT_OVERLAY_DURATION;
        
        this.overlay = createOverlayElement();
        this.boundKeyHandler = this.handleKeyDown.bind(this);
        this.attach();
    }

    /**
     * Attach keyboard event listeners
     */
    public attach(): void {
        document.addEventListener('keydown', this.boundKeyHandler);
    }

    /**
     * Detach keyboard event listeners
     */
    public detach(): void {
        document.removeEventListener('keydown', this.boundKeyHandler);
        if (this.overlayTimeout) {
            clearTimeout(this.overlayTimeout);
        }
        this.overlay.remove();
    }

    /**
     * Enable/disable shortcuts
     */
    public setEnabled(enabled: boolean): void {
        this.isEnabled = enabled;
    }

    /**
     * Show the overlay indicator
     */
    private showOverlay(icon: string, text: string): void {
        this.overlay.innerHTML = `<span style="font-size: 20px;">${icon}</span><span>${text}</span>`;
        this.overlay.style.opacity = '1';

        if (this.overlayTimeout) {
            clearTimeout(this.overlayTimeout);
        }

        this.overlayTimeout = window.setTimeout(() => {
            this.overlay.style.opacity = '0';
        }, this.overlayDuration);
    }

    /**
     * Toggle play/pause
     */
    private togglePlayPause(): void {
        if (this.video.paused) {
            this.video.play();
            this.showOverlay('▶️', 'Play');
        } else {
            this.video.pause();
            this.showOverlay('⏸️', 'Pause');
        }
    }

    /**
     * Seek backward
     */
    private seekBackwardAction(): void {
        this.video.currentTime = Math.max(0, this.video.currentTime - this.seekBackward);
        this.showOverlay('⏪', `-${this.seekBackward}s`);
    }

    /**
     * Seek forward
     */
    private seekForwardAction(): void {
        this.video.currentTime = Math.min(this.video.duration, this.video.currentTime + this.seekForward);
        this.showOverlay('⏩', `+${this.seekForward}s`);
    }

    /**
     * Seek short distance (used for arrow keys)
     */
    private seekShort(seconds: number): void {
        const newTime = Math.max(0, Math.min(this.video.duration, this.video.currentTime + seconds));
        this.video.currentTime = newTime;
        const direction = seconds > 0 ? '+' : '';
        this.showOverlay('⏱️', `${direction}${seconds}s`);
    }

    /**
     * Toggle mute
     */
    private toggleMute(): void {
        this.video.muted = !this.video.muted;
        this.showOverlay('🔇', this.video.muted ? 'Muted' : 'Unmuted');
    }

    /**
     * Toggle fullscreen
     */
    private toggleFullscreen(): void {
        if (!this.container) return;

        if (document.fullscreenElement) {
            document.exitFullscreen();
            this.showOverlay('⛶', 'Exit Fullscreen');
        } else {
            this.container.requestFullscreen();
            this.showOverlay('⛶', 'Fullscreen');
        }
    }

    /**
     * Adjust volume
     */
    private adjustVolume(delta: number): void {
        const newVolume = Math.max(0, Math.min(1, this.video.volume + delta));
        this.video.volume = newVolume;
        
        // Show volume percentage
        const volumePercent = Math.round(newVolume * 100);
        let icon = '🔊';
        if (newVolume === 0) icon = '🔇';
        else if (newVolume < 0.3) icon = '🔈';
        else if (newVolume < 0.7) icon = '🔉';
        
        this.showOverlay(icon, `Volume: ${volumePercent}%`);
    }

    /**
     * Main keyboard event handler
     */
    private handleKeyDown(e: KeyboardEvent): void {
        // Don't interfere when typing in input fields
        if (isTypingInInput()) return;
        
        // Don't handle if modifier keys are pressed (except maybe shift for edge cases)
        if (e.ctrlKey || e.altKey || e.metaKey) return;

        let handled = false;

        switch (e.key.toLowerCase()) {
            case ' ':
            case 'k':
                e.preventDefault();
                this.togglePlayPause();
                handled = true;
                break;

            case 'j':
                e.preventDefault();
                this.seekBackwardAction();
                handled = true;
                break;

            case 'l':
                e.preventDefault();
                this.seekForwardAction();
                handled = true;
                break;

            case 'm':
                e.preventDefault();
                this.toggleMute();
                handled = true;
                break;

            case 'f':
                e.preventDefault();
                this.toggleFullscreen();
                handled = true;
                break;

            case 'arrowleft':
                e.preventDefault();
                this.seekShort(-DEFAULT_SEEK_SHORT);
                handled = true;
                break;

            case 'arrowright':
                e.preventDefault();
                this.seekShort(DEFAULT_SEEK_SHORT);
                handled = true;
                break;

            case 'arrowup':
                e.preventDefault();
                this.adjustVolume(this.volumeStep);
                handled = true;
                break;

            case 'arrowdown':
                e.preventDefault();
                this.adjustVolume(-this.volumeStep);
                handled = true;
                break;
        }

        if (handled) {
            e.preventDefault();
        }
    }

    /**
     * Get list of available shortcuts
     */
    public getShortcutList(): ShortcutAction[] {
        return [
            { key: 'Space / K', description: 'Play / Pause', icon: '▶️⏸️' },
            { key: 'J', description: 'Seek back 10s', icon: '⏪' },
            { key: 'L', description: 'Seek forward 10s', icon: '⏩' },
            { key: 'M', description: 'Mute toggle', icon: '🔇' },
            { key: 'F', description: 'Fullscreen toggle', icon: '⛶' },
            { key: '←', description: 'Seek back 5s', icon: '⏮️' },
            { key: '→', description: 'Seek forward 5s', icon: '⏭️' },
            { key: '↑', description: 'Volume up', icon: '🔊' },
            { key: '↓', description: 'Volume down', icon: '🔉' },
        ];
    }
}

/**
 * Quick setup function - attaches keyboard shortcuts to a video element
 */
export function setupKeyboardShortcuts(
    videoSelector: string,
    containerSelector?: string,
    options?: Partial<KeyboardShortcutsOptions>
): KeyboardShortcuts | null {
    const video = document.querySelector(videoSelector) as HTMLVideoElement;
    if (!video) {
        console.error(`Video element not found: ${videoSelector}`);
        return null;
    }

    const container = containerSelector 
        ? document.querySelector(containerSelector) as HTMLElement 
        : video.parentElement as HTMLElement;

    return new KeyboardShortcuts({
        videoElement: video,
        containerElement: container,
        ...options
    });
}

export default KeyboardShortcuts;
