/*
 * RustChain Miner for Commodore 64
 * User interface - 40-column text display
 */

#include <stdio.h>
#include <string.h>
#include <cbm.h>
#include <peekpoke.h>

#include "ui.h"

/* ============================================================================
 * Screen Constants
 * ============================================================================ */

#define SCREEN_WIDTH 40
#define SCREEN_HEIGHT 25
#define SCREEN_RAM_ADDR 0x0400
#define COLOR_RAM_ADDR 0xD800

/* PETSCII color codes */
#define COLOR_BLACK 0
#define COLOR_WHITE 1
#define COLOR_RED 2
#define COLOR_CYAN 3
#define COLOR_PURPLE 4
#define COLOR_GREEN 5
#define COLOR_BLUE 6
#define COLOR_YELLOW 7
#define COLOR_ORANGE 8
#define COLOR_BROWN 9
#define COLOR_LTRED 10
#define COLOR_DKGRAY 11
#define COLOR_GRAY 12
#define COLOR_LTGREEN 13
#define COLOR_LTBLUE 14
#define COLOR_LTGRAY 15

/* PETSCII control codes */
#define PET_CLR 147      /* Clear screen */
#define PET_HOME 19      /* Cursor home */
#define PET_REV_ON 18    /* Reverse on */
#define PET_REV_OFF 146  /* Reverse off */
#define PET_WHITE 5      /* White text */
#define PET_RED 28       /* Red text */
#define PET_GREEN 30     /* Green text */
#define PET_BLUE 159     /* Blue text */

/* ============================================================================
 * Global State
 * ============================================================================ */

static uint8_t g_screen_buffer[SCREEN_WIDTH * SCREEN_HEIGHT];

/* ============================================================================
 * Helper Functions
 * ============================================================================ */

static void plot_char(uint8_t x, uint8_t y, char c, uint8_t color)
{
    uint16_t screen_pos = SCREEN_RAM_ADDR + (y * SCREEN_WIDTH) + x;
    uint16_t color_pos = COLOR_RAM_ADDR + (y * SCREEN_WIDTH) + x;
    
    POKE(screen_pos, c);
    POKE(color_pos, color);
}

static void plot_string(uint8_t x, uint8_t y, const char* str, uint8_t color)
{
    uint8_t i = 0;
    
    while (str[i] && i < SCREEN_WIDTH) {
        plot_char(x + i, y, str[i], color);
        i++;
    }
}

static void clear_line(uint8_t y)
{
    uint8_t x;
    
    for (x = 0; x < SCREEN_WIDTH; x++) {
        plot_char(x, y, ' ', COLOR_WHITE);
    }
}

/* ============================================================================
 * Public API
 * ============================================================================ */

void ui_init(void)
{
    /* Clear screen */
    cbm_clrscr();
    
    /* Set white text on blue background */
    POKE(0xD020, COLOR_BLUE);  /* Border color */
    POKE(0xD021, COLOR_BLUE);  /* Background color */
}

void ui_clear(void)
{
    cbm_clrscr();
}

void ui_show_splash(const char* version)
{
    uint8_t y = 8;
    
    ui_clear();
    
    /* Center splash screen */
    plot_string(8, y++, "    #### RUSTCHAIN ####    ", COLOR_YELLOW);
    plot_string(6, y++, "    MINER FOR C64 v", COLOR_WHITE);
    plot_string(24, y, version, COLOR_CYAN);
    y += 2;
    
    plot_string(4, y++, "    Proof-of-Antiquity", COLOR_GREEN);
    plot_string(7, y++, "    4.0x Multiplier", COLOR_LTGREEN);
    y += 2;
    
    plot_string(3, y++, "    Initializing...", COLOR_WHITE);
}

void ui_draw_main_screen(void)
{
    uint8_t y = 0;
    
    ui_clear();
    
    /* Header */
    plot_string(0, y++, "########################################", COLOR_CYAN);
    plot_string(2, y++, "RUSTCHAIN MINER v0.1.0 - C64", COLOR_YELLOW);
    plot_string(0, y++, "########################################", COLOR_CYAN);
    y++;
    
    /* Status section */
    plot_string(2, y++, "STATUS:", COLOR_WHITE);
    g_status_y = y - 1;
    plot_string(12, g_status_y, "INITIALIZING...", COLOR_YELLOW);
    y++;
    
    /* Epoch timer */
    plot_string(2, y++, "EPOCH:", COLOR_WHITE);
    g_timer_y = y - 1;
    plot_string(12, g_timer_y, "10:00 REMAINING", COLOR_CYAN);
    y++;
    
    /* Earned RTC */
    plot_string(2, y++, "EARNED:", COLOR_WHITE);
    g_earned_y = y - 1;
    plot_string(12, g_earned_y, "0.0000 RTC", COLOR_GREEN);
    y++;
    
    /* Attestation count */
    plot_string(2, y++, "ATTESTS:", COLOR_WHITE);
    g_count_y = y - 1;
    plot_string(12, g_count_y, "0", COLOR_LTGREEN);
    y++;
    
    /* Separator */
    plot_string(0, y++, "----------------------------------------", COLOR_DKGRAY);
    y++;
    
    /* Hardware info */
    plot_string(2, y++, "HARDWARE:", COLOR_WHITE);
    plot_string(2, y++, "CPU: MOS 6510 @ 1.023 MHZ", COLOR_LTGRAY);
    plot_string(2, y++, "RAM: 64 KB", COLOR_LTGRAY);
    plot_string(2, y++, "NET: RR-NET", COLOR_LTGRAY);
    y++;
    
    /* Separator */
    plot_string(0, y++, "----------------------------------------", COLOR_DKGRAY);
    y++;
    
    /* Help */
    plot_string(2, y++, "[F1] PAUSE [F3] MENU [F5] QUIT", COLOR_DKGRAY);
}

void ui_show_status(const char* status)
{
    uint8_t len = strlen(status);
    uint8_t x = 12;
    
    /* Clear old status */
    clear_line(g_status_y);
    
    /* Plot new status */
    if (len > SCREEN_WIDTH - x) {
        len = SCREEN_WIDTH - x;
    }
    
    plot_string(x, g_status_y, status, COLOR_YELLOW);
}

void ui_update_timer(uint8_t minutes, uint8_t seconds)
{
    char buffer[20];
    
    sprintf(buffer, "%02u:%02u REMAINING", minutes, seconds);
    
    /* Clear old timer */
    clear_line(g_timer_y);
    
    /* Plot new timer */
    plot_string(12, g_timer_y, buffer, COLOR_CYAN);
}

void ui_update_earned(float earned)
{
    char buffer[20];
    
    sprintf(buffer, "%.4f RTC", earned);
    
    /* Clear old value */
    clear_line(g_earned_y);
    
    /* Plot new value */
    plot_string(12, g_earned_y, buffer, COLOR_GREEN);
}

void ui_update_count(uint16_t count)
{
    char buffer[10];
    
    sprintf(buffer, "%u", count);
    
    /* Clear old value */
    clear_line(g_count_y);
    
    /* Plot new value */
    plot_string(12, g_count_y, buffer, COLOR_LTGREEN);
}

void ui_show_error(const char* error)
{
    uint8_t y = 20;
    
    /* Clear area */
    clear_line(y);
    clear_line(y + 1);
    clear_line(y + 2);
    
    /* Show error */
    plot_string(10, y, "##################", COLOR_RED);
    plot_string(12, y + 1, "ERROR", COLOR_RED);
    plot_string(8, y + 2, error, COLOR_LTRED);
    plot_string(10, y + 3, "##################", COLOR_RED);
}

void ui_show_menu(void)
{
    uint8_t y = 8;
    
    /* Menu box */
    plot_string(10, y++, "##########################", COLOR_CYAN);
    plot_string(12, y++, "MINER MENU", COLOR_YELLOW);
    plot_string(10, y++, "##########################", COLOR_CYAN);
    y++;
    plot_string(12, y++, "[1] RESUME", COLOR_WHITE);
    plot_string(12, y++, "[2] NETWORK STATUS", COLOR_WHITE);
    plot_string(12, y++, "[3] WALLET INFO", COLOR_WHITE);
    plot_string(12, y++, "[4] EXIT", COLOR_RED);
    plot_string(10, y++, "##########################", COLOR_CYAN);
}
