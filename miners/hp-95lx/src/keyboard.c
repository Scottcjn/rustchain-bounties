/*
 * keyboard.c - HP 95LX keyboard input handling
 * 
 * Uses BIOS keyboard services (INT 0x16) for reliable input
 * across HP 95LX hardware and emulators.
 */

#include <stdio.h>
#include <dos.h>
#include <i86.h>
#include <conio.h>

#include "keyboard.h"

/* Keyboard state */
static struct keyboard_state g_kb_state;
static int g_keyboard_initialized = 0;

/*
 * Initialize keyboard
 * 
 * Returns: 0 on success, -1 on failure
 */
int keyboard_init(void)
{
    g_kb_state.last_key = KEY_NONE;
    g_kb_state.shift_pressed = 0;
    g_kb_state.ctrl_pressed = 0;
    g_kb_state.alt_pressed = 0;
    g_kb_state.key_count = 0;
    g_keyboard_initialized = 1;
    
    /* Clear any pending keystrokes */
    keyboard_clear_buffer();
    
    return 0;
}

/*
 * Close keyboard
 */
void keyboard_close(void)
{
    keyboard_clear_buffer();
    g_keyboard_initialized = 0;
}

/*
 * Check if key is available (non-blocking)
 * 
 * Returns: 1 if key available, 0 otherwise
 */
int keyboard_kbhit(void)
{
    if (!g_keyboard_initialized) return 0;
    
    return kbhit();
}

/*
 * Read key (blocking if no key available)
 * 
 * Returns: ASCII code or scan code for extended keys
 */
int keyboard_getch(void)
{
    int key;
    
    if (!g_keyboard_initialized) return KEY_NONE;
    
    key = getch();
    
    /* Track extended keys (function keys, arrows) */
    if (key == 0 || key == 0xE0) {
        /* Extended key prefix - read scan code */
        int scan = getch();
        g_kb_state.last_key = scan;
        
        /* Update modifier state */
        if (scan >= 0x3B && scan <= 0x44) {
            /* F1-F10 */
        } else if (scan == 0x48) {
            /* Up arrow */
        } else if (scan == 0x50) {
            /* Down arrow */
        } else if (scan == 0x4B) {
            /* Left arrow */
        } else if (scan == 0x4D) {
            /* Right arrow */
        }
    } else {
        g_kb_state.last_key = key;
        
        /* Check for modifier keys */
        if (key == KEY_ESC || key == KEY_ENTER) {
            /* Common navigation keys */
        }
    }
    
    g_kb_state.key_count++;
    
    return key;
}

/*
 * Read key with timeout (returns KEY_NONE if timeout)
 * 
 * timeout_ms: Timeout in milliseconds
 * Returns: Key code or KEY_NONE if timeout
 */
int keyboard_getch_timeout(unsigned long timeout_ms)
{
    unsigned long start_ticks;
    unsigned long current_ticks;
    unsigned long timeout_ticks;
    
    if (!g_keyboard_initialized) return KEY_NONE;
    
    /* Get current timer ticks */
    start_ticks = get_timer_ticks();
    timeout_ticks = (timeout_ms * 18) / 1000;  /* Convert to timer ticks (~18.2 Hz) */
    
    while (1) {
        if (keyboard_kbhit()) {
            return keyboard_getch();
        }
        
        current_ticks = get_timer_ticks();
        
        /* Handle timer wraparound */
        if (current_ticks < start_ticks) {
            current_ticks += 0x100000000UL;
        }
        
        if ((current_ticks - start_ticks) >= timeout_ticks) {
            return KEY_NONE;  /* Timeout */
        }
        
        /* Small delay to prevent CPU hogging */
        delay(10);
    }
}

/*
 * Get keyboard state
 */
void keyboard_get_state(struct keyboard_state *state)
{
    if (!state || !g_keyboard_initialized) return;
    
    *state = g_kb_state;
}

/*
 * Clear keyboard buffer
 */
void keyboard_clear_buffer(void)
{
    union REGS regs;
    
    /* Clear keyboard buffer using BIOS */
    while (kbhit()) {
        getch();
    }
}

/*
 * Check for specific key
 * 
 * key_code: Key code to wait for
 * timeout_ms: Timeout in milliseconds (0 = no timeout)
 * Returns: 1 if key pressed, 0 if timeout
 */
int keyboard_wait_key(int key_code, unsigned long timeout_ms)
{
    int key;
    unsigned long start_ticks = 0;
    unsigned long timeout_ticks = 0;
    
    if (timeout_ms > 0) {
        start_ticks = get_timer_ticks();
        timeout_ticks = (timeout_ms * 18) / 1000;
    }
    
    while (1) {
        if (keyboard_kbhit()) {
            key = keyboard_getch();
            if (key == key_code) {
                return 1;
            }
        }
        
        /* Check timeout */
        if (timeout_ms > 0) {
            unsigned long current_ticks = get_timer_ticks();
            if (current_ticks < start_ticks) {
                current_ticks += 0x100000000UL;
            }
            if ((current_ticks - start_ticks) >= timeout_ticks) {
                return 0;  /* Timeout */
            }
        }
        
        delay(10);
    }
}
