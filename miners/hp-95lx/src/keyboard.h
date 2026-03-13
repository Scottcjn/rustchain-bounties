/*
 * keyboard.h - HP 95LX keyboard input handling
 * 
 * HP 95LX keyboard layout:
 * - Standard QWERTY keys
 * - Function keys F1-F12 (F1-F10 visible on screen)
 * - Special keys: ESC, ENTER, CTRL, ALT, SHIFT
 * - Arrow keys (cursor movement)
 */

#ifndef KEYBOARD_H
#define KEYBOARD_H

/* Key codes for HP 95LX */
#define KEY_NONE        0
#define KEY_ESC         0x1B
#define KEY_ENTER       0x0D
#define KEY_BACKSPACE   0x08
#define KEY_TAB         0x09
#define KEY_SPACE       0x20

/* Function keys (extended scan codes) */
#define KEY_F1          0x3B
#define KEY_F2          0x3C
#define KEY_F3          0x3D
#define KEY_F4          0x3E
#define KEY_F5          0x3F
#define KEY_F6          0x40
#define KEY_F7          0x41
#define KEY_F8          0x42
#define KEY_F9          0x43
#define KEY_F10         0x44

/* Arrow keys */
#define KEY_UP          0x48
#define KEY_DOWN        0x50
#define KEY_LEFT        0x4B
#define KEY_RIGHT       0x4D

/* Keyboard state */
struct keyboard_state {
    int last_key;
    int shift_pressed;
    int ctrl_pressed;
    int alt_pressed;
    unsigned long key_count;
};

/* Initialize keyboard */
int keyboard_init(void);

/* Close keyboard */
void keyboard_close(void);

/* Check if key is available (non-blocking) */
int keyboard_kbhit(void);

/* Read key (blocking if no key available) */
int keyboard_getch(void);

/* Read key with timeout (returns KEY_NONE if timeout) */
int keyboard_getch_timeout(unsigned long timeout_ms);

/* Get keyboard state */
void keyboard_get_state(struct keyboard_state *state);

/* Clear keyboard buffer */
void keyboard_clear_buffer(void);

/* Check for specific key */
int keyboard_wait_key(int key_code, unsigned long timeout_ms);

#endif /* KEYBOARD_H */
