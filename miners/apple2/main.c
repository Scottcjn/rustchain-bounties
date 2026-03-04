/* SPDX-License-Identifier: MIT
 *
 * RustChain Apple II Miner — stub implementation
 * ------------------------------------------------
 * This is an early placeholder that compiles with the CC65 toolchain for
 * the Apple II target. It does not yet implement networking or mining, but
 * establishes a reproducible build that boots on real Apple II hardware.
 *
 * Build (requires CC65):
 *     make   # produces rustchain_apple2_miner.dsk disk image
 *
 * Runtime behaviour:
 *     Prints a banner identifying the miner and loops forever. The infinite
 *     loop is intentional to keep the program resident and ready for future
 *     networking logic once implemented.
 */

#include <stdio.h>

void main(void) {
    puts("RustChain Apple II Miner — INITIAL SKELETON\n");
    puts("device_arch: 6502, device_family: apple2\n");
    puts("(network + mining logic to be added)\n");

    /* Endless loop to keep program running */
    while (1) {
        /* Idle — future mining work will execute here */
    }
}
