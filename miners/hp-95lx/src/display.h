/*
 * display.h - HP 95LX LCD display routines
 * 
 * HP 95LX: 240×128 pixels, 40×16 characters, monochrome STN LCD
 * No backlight, no graphics mode (text only)
 */

#ifndef DISPLAY_H
#define DISPLAY_H

/* Include miner state for stats display */
#include "miner.h"

/* Display dimensions */
#define DISPLAY_COLS 40
#define DISPLAY_ROWS 16

/* Initialize display */
int display_init(void);

/* Close display */
void display_close(void);

/* Clear screen */
void display_clear(void);

/* Print text at specific line (0-15) */
void display_print_line(int line, const char *text);

/* Print text at current cursor position */
void display_print(const char *text);

/* Set cursor position */
void display_gotoxy(int x, int y);

/* Update status line */
void display_status(const char *status);

/* Display mining statistics */
void display_mining_stats(struct miner_state *state, unsigned long iterations, unsigned long elapsed);

/* Display main menu */
void display_menu(int selected);

/* Display statistics screen */
void display_stats_screen(struct miner_state *state, unsigned long iterations);

/* Draw a box on the display */
void display_box(int x1, int y1, int x2, int y2);

#endif /* DISPLAY_H */
