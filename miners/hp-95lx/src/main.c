/*
 * RustChain Miner for HP 95LX Palmtop
 * 
 * Target: HP 95LX (NEC V20 @ 5.37 MHz, 512 KB/1 MB RAM, MS-DOS 3.22)
 * 
 * This is a port of the IBM PC/XT miner, adapted for the HP 95LX palmtop.
 * Key differences:
 * - NEC V20 CPU (8088-compatible)
 * - Integrated SoC (no ISA bus)
 * - 240×128 monochrome LCD (40×16 characters)
 * - Serial networking (RS-232, SLIP/PPP)
 * - Battery-powered operation
 *
 * Build: Open Watcom C (wcl -bt=dos -ml)
 * 
 * Bounty: #417 - 100 RTC (~$10 USD)
 * Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dos.h>
#include <conio.h>

#include "miner.h"
#include "hw_95lx.h"
#include "display.h"
#include "serial.h"
#include "keyboard.h"

/* Version information */
#define MINER_VERSION "0.1.0-95lx"
#define MINER_NAME "RustChain HP 95LX Miner"

/* Global state */
static struct miner_state state;

/*
 * Display the main mining screen
 * HP 95LX: 40×16 character LCD
 */
static void display_main_screen(void)
{
    display_clear();
    
    /* Header */
    display_print_line(0, "+----------------------------------------+");
    display_print_line(1, "| RUSTCHAIN MINER v0.1 - HP 95LX        |");
    display_print_line(2, "+----------------------------------------+");
    
    /* Status area - will be updated by display_mining_stats */
    display_print_line(4, "| STATUS: INITIALIZING...                |");
    display_print_line(5, "| EARNED: 0.0000 RTC                     |");
    display_print_line(6, "| UPTIME: 00:00:00                       |");
    display_print_line(7, "| HASHES: 0 H/s                          |");
    
    /* Hardware info */
    display_print_line(8, "+----------------------------------------+");
    display_print_line(9, "| HW: NEC V20 @ 5.37 MHz                 |");
    display_print_line(10, "| MEM: 512 KB                           |");
    display_print_line(11, "| SERIAL: NOT CONNECTED                 |");
    display_print_line(12, "+----------------------------------------+");
    
    /* Footer */
    display_print_line(13, "+----------------------------------------+");
    display_print_line(14, "| [F1] Menu  [F2] Stats  [F3] Exit      |");
    display_print_line(15, "+----------------------------------------+");
}

/*
 * Show main menu and handle user interaction
 * Returns: 0=continue mining, 1=show stats, 2=settings, 3=exit
 */
static int show_menu(void)
{
    int selected = 0;
    int key;
    int result = 0;
    
    display_menu(selected);
    
    while (1) {
        key = keyboard_getch_timeout(100);
        
        switch (key) {
            case 0:  /* Extended key prefix */
                key = keyboard_getch();
                switch (key) {
                    case KEY_UP:
                        selected = (selected > 0) ? selected - 1 : 3;
                        display_menu(selected);
                        break;
                    case KEY_DOWN:
                        selected = (selected < 3) ? selected + 1 : 0;
                        display_menu(selected);
                        break;
                    case KEY_ENTER:
                        /* User selected an option */
                        return selected;
                }
                break;
            case KEY_ESC:
                return -1;  /* Back to mining */
        }
    }
    
    return result;
}

/*
 * Show statistics screen
 */
static void show_statistics(struct miner_state *state, unsigned long iterations)
{
    display_stats_screen(state, iterations);
    keyboard_getch();  /* Wait for any key */
}

/*
 * Initialize the miner state
 */
static int miner_init(void)
{
    memset(&state, 0, sizeof(state));
    
    /* Initialize display */
    if (display_init() != 0) {
        fprintf(stderr, "Failed to initialize display\n");
        return -1;
    }
    
    /* Initialize keyboard */
    if (keyboard_init() != 0) {
        fprintf(stderr, "Failed to initialize keyboard\n");
        display_close();
        return -1;
    }
    
    /* Initialize serial port */
    if (serial_init(COM1, 9600) != 0) {
        /* Serial is optional for offline mode */
        state.serial_connected = 0;
    } else {
        state.serial_connected = 1;
    }
    
    /* Detect hardware */
    if (hw_95lx_detect() != 0) {
        fprintf(stderr, "Hardware detection failed\n");
        keyboard_close();
        display_close();
        return -1;
    }
    
    /* Check if running on real hardware or emulator */
    if (hw_95lx_is_emulator()) {
        state.is_emulator = 1;
        state.reward_multiplier = 0.0;  /* No reward for emulators */
    } else {
        state.is_emulator = 0;
        state.reward_multiplier = 2.0;  /* 2.0x for real HP 95LX */
    }
    
    return 0;
}

/*
 * Main mining loop
 */
static void miner_run(void)
{
    unsigned long iterations = 0;
    unsigned long start_time = get_timer_ticks();
    unsigned long last_update = 0;
    
    display_main_screen();
    
    while (!state.exit_requested) {
        /* Check for user input */
        if (keyboard_kbhit()) {
            int key = keyboard_getch();
            switch (key) {
                case 0:  /* Extended key (function keys) */
                    key = keyboard_getch();
                    switch (key) {
                        case KEY_F1:  /* F1 - Menu */
                            {
                                int menu_result = show_menu();
                                if (menu_result == 3) {
                                    state.exit_requested = 1;
                                } else if (menu_result == 1) {
                                    show_statistics(&state, iterations);
                                    display_main_screen();
                                }
                            }
                            break;
                        case KEY_F2:  /* F2 - Stats */
                            show_statistics(&state, iterations);
                            display_main_screen();
                            break;
                        case KEY_F3:  /* F3 - Exit */
                            state.exit_requested = 1;
                            break;
                    }
                    break;
                case KEY_ESC:  /* ESC - Exit */
                    state.exit_requested = 1;
                    break;
            }
        }
        
        /* Mining iteration */
        mining_iteration(&state);
        iterations++;
        
        /* Update display every 50 iterations (more frequent updates) */
        if (iterations % 50 == 0) {
            unsigned long elapsed = get_timer_ticks() - start_time;
            display_mining_stats(&state, iterations, elapsed);
            last_update = elapsed;
        }
        
        /* Small delay to prevent CPU hogging and save battery */
        delay(10);
    }
}

/*
 * Print usage information
 */
static void print_usage(const char *prog_name)
{
    printf("RustChain HP 95LX Miner v%s\n", MINER_VERSION);
    printf("Usage: %s [options]\n\n", prog_name);
    printf("Options:\n");
    printf("  -h, --help     Show this help message\n");
    printf("  -v, --version  Show version information\n");
    printf("  -s, --serial   Enable serial networking (COM1)\n");
    printf("  -b, --baud N   Set serial baud rate (default: 9600)\n");
    printf("\n");
    printf("HP 95LX: NEC V20 @ 5.37 MHz, 512 KB RAM, MS-DOS 3.22\n");
    printf("Bounty: #417 - 100 RTC\n");
    printf("Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b\n");
}

/*
 * Main entry point
 */
int main(int argc, char *argv[])
{
    int i;
    int use_serial = 0;
    
    /* Parse command line arguments */
    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--version") == 0) {
            printf("%s v%s\n", MINER_NAME, MINER_VERSION);
            return 0;
        } else if (strcmp(argv[i], "-s") == 0 || strcmp(argv[i], "--serial") == 0) {
            use_serial = 1;
        } else if (strcmp(argv[i], "-b") == 0 || strcmp(argv[i], "--baud") == 0) {
            if (i + 1 < argc) {
                int baud = atoi(argv[++i]);
                if (baud > 0) {
                    serial_set_baud(baud);
                }
            }
        }
    }
    
    /* Initialize miner */
    if (miner_init() != 0) {
        fprintf(stderr, "Miner initialization failed\n");
        return 1;
    }
    
    /* Override serial if requested */
    if (use_serial && state.serial_connected == 0) {
        if (serial_init(COM1, 9600) == 0) {
            state.serial_connected = 1;
        }
    }
    
    /* Print startup message */
    printf("%s v%s\n", MINER_NAME, MINER_VERSION);
    printf("HP 95LX Palmtop (NEC V20 @ 5.37 MHz)\n");
    printf("Bounty #417 - Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b\n");
    printf("\n");
    
    if (state.is_emulator) {
        printf("[WARNING] Emulator detected! No rewards will be earned.\n");
        printf("[INFO] This is expected when running in an emulator.\n");
    } else {
        printf("[OK] Real HP 95LX hardware detected.\n");
        printf("[INFO] Reward multiplier: 2.0x\n");
    }
    
    if (state.serial_connected) {
        printf("[OK] Serial port connected (COM1, 9600 baud)\n");
    } else {
        printf("[INFO] Running in offline mode (no serial)\n");
    }
    
    printf("\nStarting mining loop... Press F3 or ESC to exit.\n\n");
    
    /* Run mining loop */
    miner_run();
    
    /* Cleanup */
    keyboard_close();
    serial_close();
    display_close();
    
    printf("\nMiner stopped. Total iterations: %lu\n", state.total_iterations);
    printf("Total earned: %.4f RTC\n", state.total_earned);
    
    return 0;
}
