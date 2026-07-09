## Keyboard Shortcuts for BoTTube Player

Added YouTube-style keyboard shortcuts to the BoTTube video player.

**Platform:** BoTTube
**Shortcuts implemented:**
- `Space` / `K`: Play / Pause
- `J`: Seek back 10 seconds
- `L`: Seek forward 10 seconds
- `Arrow Left`: Seek back 5 seconds
- `Arrow Right`: Seek forward 5 seconds
- `Arrow Up`: Increase volume by 5%
- `Arrow Down`: Decrease volume by 5%
- `M`: Toggle mute
- `F`: Toggle fullscreen
- `C`: Toggle captions
- `0`-`9`: Jump to corresponding percentage of the video duration (0% - 90%)
- `?`: Open shortcut help overlay modal
- `Escape`: Exit fullscreen / close help modal

**Tech stack:** JavaScript Event Listeners, ARIA announcements
**Implementation PR:** [https://github.com/Scottcjn/bottube/pull/1560](https://github.com/Scottcjn/bottube/pull/1560)
**Source Code:** [watch.html](./bounty-2140/watch.html)

### Verification
- Open the watch page on BoTTube.
- Press `?` to view the keyboard shortcut help overlay modal.
- Test standard shortcuts (Space, Arrow keys, K, J, L, F, M, 0-9) to see corresponding floating visual overlay feedback showing the action performed.
- Focus on the comments/replies input area and type; keyboard shortcuts are automatically suppressed while input is focused to prevent interference.

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1