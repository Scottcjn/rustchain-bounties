/*
 * display.c - HP 95LX LCD display routines
 * 
 * HP 95LX: 240×128 pixels, 40×16 characters, monochrome STN LCD
 * Uses standard BIOS video services (INT 0x10)
 */

#include <stdio.h>
#include <string.h>
#include <conio.h>
#include <i86.h>

#include "display.h"
/* Temporarily exclude miner.h and hw_95lx.h */

/* Display state */
static int g_display_initialized = 0;
static int g_cursor_x = 0;
static int g_cursor_y = 0;
static char g_screen_buffer[16][41];  /* 16 rows × 40 cols + null */

/*
 * Initialize display
 * 
 * Sets up 40×16 text mode for HP 95LX LCD
 * 
 * Returns: 0 on success, -1 on failure
 */
int display_init(void)
{
    union REGS regs;
    
    /* Set video mode to 40-column text mode */
    /* HP 95LX uses CGA-compatible modes */
    regs.h.ah = 0x00;  /* Set video mode */
    regs.h.al = 0x00;  /* 40×25 text mode (we'll use 40×16) */
    int86(0x10, &regs, &regs);
    
    /* Clear screen buffer */
    /* memset(g_screen_buffer, 0, sizeof(g_screen_buffer)); */
    
    /* Clear screen */
    display_clear();
    
    g_display_initialized = 1;
    g_cursor_x = 0;
    g_cursor_y = 0;
    
    return 0;
}

/*
 * Close display
 * 
 * Restores original video mode
 */
void display_close(void)
{
    if (!g_display_initialized) return;
    
    /* Restore text mode - stub for now */
    g_display_initialized = 0;
}

/*
 * Clear screen
 */
void display_clear(void)
{
    union REGS regs;
    
    /* Clear screen using BIOS */
    regs.h.ah = 0x06;  /* Scroll up (clear) */
    regs.h.al = 0x00;  /* Clear entire window */
    regs.h.bh = 0x07;  /* Attribute (white on black) */
    regs.h.ch = 0x00;  /* Upper row */
    regs.h.cl = 0x00;  /* Left column */
    regs.h.dh = 15;    /* Lower row (0-15 for 16 rows) */
    regs.h.dl = 39;    /* Right column (0-39 for 40 cols) */
    int86(0x10, &regs, &regs);
    
    /* Reset cursor */
    display_gotoxy(0, 0);
}

/*
 * Print text at specific line
 * 
 * line: Line number (0-15)
 * text: Text to print (truncated to fit)
 */
void display_print_line(int line, const char *text)
{
    if (line < 0 || line >= DISPLAY_ROWS) return;
    
    display_gotoxy(0, line);
    display_print(text);
}

/*
 * Print text at current cursor position
 */
void display_print(const char *text)
{
    union REGS regs;
    
    if (!text || !g_display_initialized) return;
    
    /* Use BIOS teletype output */
    while (*text && g_cursor_x < DISPLAY_COLS) {
        regs.h.ah = 0x0E;  /* Teletype output */
        regs.h.al = *text;
        regs.h.bh = 0x00;  /* Page 0 */
        int86(0x10, &regs, &regs);
        
        if (*text == '\n') {
            g_cursor_x = 0;
            g_cursor_y++;
        } else if (*text == '\r') {
            g_cursor_x = 0;
        } else {
            g_cursor_x++;
        }
        
        text++;
    }
}

/*
 * Set cursor position
 * 
 * x: Column (0-39)
 * y: Row (0-15)
 */
void display_gotoxy(int x, int y)
{
    union REGS regs;
    
    if (x < 0) x = 0;
    if (x >= DISPLAY_COLS) x = DISPLAY_COLS - 1;
    if (y < 0) y = 0;
    if (y >= DISPLAY_ROWS) y = DISPLAY_ROWS - 1;
    
    g_cursor_x = x;
    g_cursor_y = y;
    
    /* Set cursor position using BIOS */
    regs.h.ah = 0x02;  /* Set cursor position */
    regs.h.bh = 0x00;  /* Page 0 */
    regs.h.dh = y;     /* Row */
    regs.h.dl = x;     /* Column */
    int86(0x10, &regs, &regs);
}

/*
 * Update status line
 * 
 * status: Status text to display
 */
void display_status(const char *status)
{
    int i;
    
    /* Display status on last line (row 15) */
    display_gotoxy(0, 15);
    
    /* Clear the line first */
    for (i = 0; i < DISPLAY_COLS; i++) {
        display_print(" ");
    }
    
    /* Print status */
    display_gotoxy(0, 15);
    display_print(status);
}

/*
 * Display mining statistics
 * 
 * state: Pointer to miner state
 * iterations: Current iteration count
 * elapsed: Elapsed time in timer ticks
 */
void display_mining_stats(struct miner_state *state, unsigned long iterations, unsigned long elapsed)
{
    char buffer[41];
    unsigned long seconds, minutes, hours;
    double hash_rate;
    
    /* Calculate uptime */
    seconds = elapsed / 18;  /* BIOS timer runs at ~18.2 Hz */
    minutes = seconds / 60;
    hours = minutes / 60;
    seconds %= 60;
    minutes %= 60;
    
    /* Calculate hash rate (hashes per second) */
    if (elapsed > 0) {
        hash_rate = (double)iterations * 18.2 / elapsed;
    } else {
        hash_rate = 0.0;
    }
    
    /* Row 4: Status */
    if (state->is_emulator) {
        snprintf(buffer, sizeof(buffer), "| STATUS: EMULATOR [NO REWARDS]          |");
    } else if (state->serial_connected) {
        snprintf(buffer, sizeof(buffer), "| STATUS: MINING (ONLINE)                |");
    } else {
        snprintf(buffer, sizeof(buffer), "| STATUS: MINING (OFFLINE)               |");
    }
    display_print_line(4, buffer);
    
    /* Row 5: Total earned */
    snprintf(buffer, sizeof(buffer), "| EARNED: %.4f RTC (x%.1f)                  |", 
             state->total_earned, state->reward_multiplier);
    display_print_line(5, buffer);
    
    /* Row 6: Uptime */
    snprintf(buffer, sizeof(buffer), "| UPTIME: %02lu:%02lu:%02lu                       |",
             hours, minutes, seconds);
    display_print_line(6, buffer);
    
    /* Row 7: Hash rate */
    snprintf(buffer, sizeof(buffer), "| HASHES: %.0f H/s                           |", hash_rate);
    display_print_line(7, buffer);
    
    /* Row 9-11: Hardware info */
    snprintf(buffer, sizeof(buffer), "| CPU: %-34s |", hw_95lx_get_cpu_name());
    display_print_line(9, buffer);
    
    snprintf(buffer, sizeof(buffer), "| MEM: %d KB                             |", 
             hw_95lx_get_memory_kb());
    display_print_line(10, buffer);
    
    if (state->serial_connected) {
        snprintf(buffer, sizeof(buffer), "| NET: COM1 @ 9600 baud                  |");
    } else {
        snprintf(buffer, sizeof(buffer), "| NET: OFFLINE                           |");
    }
    display_print_line(11, buffer);
}

/*
 * Display main menu
 * 
 * selected: Currently selected menu item (0-3)
 */
void display_menu(int selected)
{
    int i;
    char buffer[41];
    
    display_clear();
    
    /* Header */
    display_print_line(0, "+----------------------------------------+");
    display_print_line(1, "|       RUSTCHAIN MINER MENU             |");
    display_print_line(2, "+----------------------------------------+");
    
    /* Menu items */
    for (i = 0; i < 4; i++) {
        char *label;
        switch (i) {
            case 0: label = "Start Mining"; break;
            case 1: label = "Mining Statistics"; break;
            case 2: label = "Network Settings"; break;
            case 3: label = "Exit"; break;
            default: label = "Unknown"; break;
        }
        
        if (i == selected) {
            snprintf(buffer, sizeof(buffer), "| > %-36s |", label);
        } else {
            snprintf(buffer, sizeof(buffer), "|   %-36s |", label);
        }
        display_print_line(5 + i, buffer);
    }
    
    /* Footer */
    display_print_line(12, "+----------------------------------------+");
    display_print_line(13, "| [UP/DOWN] Select  [ENTER] Choose       |");
    display_print_line(14, "| [ESC] Back                             |");
    display_print_line(15, "+----------------------------------------+");
}

/*
 * Display statistics screen
 */
void display_stats_screen(struct miner_state *state, unsigned long iterations)
{
    char buffer[41];
    unsigned long seconds, minutes, hours;
    
    /* Calculate uptime */
    seconds = get_timer_ticks() / 18;
    minutes = seconds / 60;
    hours = minutes / 60;
    seconds %= 60;
    minutes %= 60;
    
    display_clear();
    
    /* Header */
    display_print_line(0, "+----------------------------------------+");
    display_print_line(1, "|       MINING STATISTICS                |");
    display_print_line(2, "+----------------------------------------+");
    
    /* Statistics */
    snprintf(buffer, sizeof(buffer), "| Total Iterations: %-20lu |", state->total_iterations);
    display_print_line(5, buffer);
    
    snprintf(buffer, sizeof(buffer), "| Total Hashes:     %-20lu |", state->total_hashes);
    display_print_line(6, buffer);
    
    snprintf(buffer, sizeof(buffer), "| Total Earned:     %-17.4f RTC |", state->total_earned);
    display_print_line(7, buffer);
    
    snprintf(buffer, sizeof(buffer), "| Reward Mult:      %-20.1fx |", state->reward_multiplier);
    display_print_line(8, buffer);
    
    snprintf(buffer, sizeof(buffer), "| Uptime:           %02lu:%02lu:%02lu                   |", 
             hours, minutes, seconds);
    display_print_line(10, buffer);
    
    /* Hardware info */
    snprintf(buffer, sizeof(buffer), "| CPU: %-34s |", hw_95lx_get_cpu_name());
    display_print_line(12, buffer);
    
    snprintf(buffer, sizeof(buffer), "| Memory: %d KB                          |", 
             hw_95lx_get_memory_kb());
    display_print_line(13, buffer);
    
    /* Footer */
    display_print_line(15, "| [ANY KEY] Back to Mining                 |");
}

/*
 * Draw a box on the display
 * 
 * x1, y1: Top-left corner
 * x2, y2: Bottom-right corner
 */
void display_box(int x1, int y1, int x2, int y2)
{
    int x, y;
    
    /* Draw horizontal lines */
    for (x = x1; x <= x2; x++) {
        display_gotoxy(x, y1);
        display_print("-");
        display_gotoxy(x, y2);
        display_print("-");
    }
    
    /* Draw vertical lines */
    for (y = y1; y <= y2; y++) {
        display_gotoxy(x1, y);
        display_print("|");
        display_gotoxy(x2, y);
        display_print("|");
    }
    
    /* Draw corners */
    display_gotoxy(x1, y1);
    display_print("+");
    display_gotoxy(x2, y1);
    display_print("+");
    display_gotoxy(x1, y2);
    display_print("+");
    display_gotoxy(x2, y2);
    display_print("+");
}
