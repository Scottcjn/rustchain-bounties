/*
 * RustChain Miner for Commodore 64
 * User interface header
 */

#ifndef UI_H
#define UI_H

#include <stdint.h>

/* UI state */
extern uint8_t g_status_y;
extern uint8_t g_timer_y;
extern uint8_t g_earned_y;
extern uint8_t g_count_y;

/* Function prototypes */
void ui_init(void);
void ui_clear(void);
void ui_show_splash(const char* version);
void ui_draw_main_screen(void);
void ui_show_status(const char* status);
void ui_update_timer(uint8_t minutes, uint8_t seconds);
void ui_update_earned(float earned);
void ui_update_count(uint16_t count);
void ui_show_error(const char* error);
void ui_show_menu(void);

#endif /* UI_H */
