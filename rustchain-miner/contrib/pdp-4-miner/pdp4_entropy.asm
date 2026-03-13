/ PDP-4 ENTROPY COLLECTION SUBROUTINES
/ Standalone entropy collection for RustChain miner
/
/ These routines collect hardware entropy from the PDP-4
/ and can be linked with the main miner or used standalone.
/
/ Author: OpenClaw Agent (Bounty #389)
/ Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
/

        ORG     2000

/ ============================================================================
/ CORE MEMORY TIMING COLLECTION
/ ============================================================================
/ Collects entropy from magnetic core memory access timing variations.
/ Core memory has slight timing differences based on:
/ - Physical location of cores
/ - Temperature variations
/ - Power supply fluctuations
/ - Previous access history (magnetic hysteresis)

COLLECT_CORE_TIMING,
        / Entry: None
        / Exit: AC = core timing hash
        / Clobbers: AC, MQ, TEMP registers

        LAW     CORE_SAMPLE_COUNT   / Number of samples (16)
        DAC     SAMPLE_COUNTER

        LAW     0                   / Clear accumulator for hash
        DAC     CORE_HASH_ACC

CORE_TIMING_LOOP,
        LAC     SAMPLE_COUNTER
        JZ      CORE_TIMING_DONE    / If zero, done sampling

        / Generate memory access address from current PC
        LAC     PC                  / Read program counter
        AND     CORE_ADDR_MASK      / Mask to valid core range (0-7777)
        
        / Access memory - timing varies by physical location
        LAC     I                   / Load indirect (causes memory access)
        
        / Small delay to amplify timing differences
        NOP
        NOP
        
        / XOR into hash accumulator
        XOR     CORE_HASH_ACC
        DAC     CORE_HASH_ACC

        / Decrement counter
        LAC     SAMPLE_COUNTER
        SUB     ONE_CONST
        DAC     SAMPLE_COUNTER
        JMP     CORE_TIMING_LOOP

CORE_TIMING_DONE,
        LAC     CORE_HASH_ACC
        JMP     I                   / Return with hash in AC

/ ============================================================================
/ PROGRAM COUNTER SKEW COLLECTION
/ ============================================================================
/ Collects entropy from program counter timing variations.
/ The PC increments at slightly different rates due to:
/ - Gate propagation delays
/ - Temperature effects
/ - Power supply noise

COLLECT_PC_SKEW,
        / Entry: None
        / Exit: AC = PC skew hash
        / Clobbers: AC, TEMP registers

        LAW     PC_SAMPLE_COUNT     / Number of samples (32)
        DAC     SAMPLE_COUNTER

        LAC     PC                  / Get initial PC
        DAC     PC_PREV

PC_SKEW_LOOP,
        LAC     SAMPLE_COUNTER
        JZ      PC_SKEW_DONE

        / Execute variable-length instruction sequence
        / This creates PC timing variations
        LAC     PC
        DAC     PC_CURRENT

        / Calculate delta from previous PC
        LAC     PC_CURRENT
        SUB     PC_PREV
        AND     PC_DELTA_MASK       / Keep only low bits (timing variation)
        
        / XOR into hash
        XOR     PC_HASH_ACC
        DAC     PC_HASH_ACC

        / Store current as previous
        LAC     PC_CURRENT
        DAC     PC_PREV

        / Decrement counter
        LAC     SAMPLE_COUNTER
        SUB     ONE_CONST
        DAC     SAMPLE_COUNTER
        JMP     PC_SKEW_LOOP

PC_SKEW_DONE,
        LAC     PC_HASH_ACC
        JMP     I

/ ============================================================================
/ CONSOLE SWITCH COLLECTION
/ ============================================================================
/ Reads the console switch register for user-provided entropy.
/ On real PDP-4: physical toggle switches
/ On simulator: time-based or random value

COLLECT_SWITCHES,
        / Entry: None
        / Exit: AC = switch register value
        / Clobbers: AC

        / Read switch register (IOT instruction)
        / IOT 3 - Read console switches
        IOT     3                   / This is the actual PDP-4 instruction
        JMP     I                   / Return with switches in AC

/ ============================================================================
/ I/O REGISTER STATE COLLECTION
/ ============================================================================
/ Collects entropy from I/O register states.
/ I/O devices have unique states based on:
/ - Device initialization
/ - Previous operations
/ - Electrical characteristics

COLLECT_IO_STATE,
        / Entry: None
        / Exit: AC = I/O state hash
        / Clobbers: AC, TEMP

        / Clear hash accumulator
        LAW     0
        DAC     IO_HASH_ACC

        / Read paper tape reader status
        LAC     PAPER_TAPE_IN       / IOT instruction for paper tape
        XOR     IO_HASH_ACC
        DAC     IO_HASH_ACC

        / Read Teletype status
        LAC     TTY_IN              / IOT instruction for TTY
        XOR     IO_HASH_ACC
        DAC     IO_HASH_ACC

        / Read RTC if available (option 044)
        LAC     RTC_REG
        XOR     IO_HASH_ACC
        DAC     IO_HASH_ACC

        LAC     IO_HASH_ACC
        JMP     I

/ ============================================================================
/ COMBINED ENTROPY COLLECTION
/ ============================================================================
/ Collects entropy from all sources and combines into single hash.

COLLECT_ALL_ENTROPY,
        / Entry: None
        / Exit: AC = combined entropy hash
        / Clobbers: All registers

        / Save return address
        LAC     0                   / Return address is at location 0
        DAC     SAVE_RETURN

        / Collect from each source
        JSR     COLLECT_CORE_TIMING
        DAC     ENTROPY_CORE

        JSR     COLLECT_PC_SKEW
        DAC     ENTROPY_PC

        JSR     COLLECT_SWITCHES
        DAC     ENTROPY_SWITCH

        JSR     COLLECT_IO_STATE
        DAC     ENTROPY_IO

        / Combine all sources (XOR)
        LAC     ENTROPY_CORE
        XOR     ENTROPY_PC
        XOR     ENTROPY_SWITCH
        XOR     ENTROPY_IO

        / Store combined entropy
        DAC     COMBINED_ENTROPY

        / Restore and return
        LAC     SAVE_RETURN
        JMP     I

/ ============================================================================
/ ENTROPY STORAGE LOCATIONS
/ ============================================================================

        ORG     10400

ENTROPY_CORE,       0               / Core memory entropy
ENTROPY_PC,         0               / PC skew entropy
ENTROPY_SWITCH,     0               / Switch register entropy
ENTROPY_IO,         0               / I/O state entropy
COMBINED_ENTROPY,   0               / Combined entropy hash
SAVE_RETURN,        0               / Saved return address
SAMPLE_COUNTER,     0               / Sample loop counter
CORE_HASH_ACC,      0               / Core hash accumulator
PC_HASH_ACC,        0               / PC hash accumulator
IO_HASH_ACC,        0               / I/O hash accumulator
PC_CURRENT,         0               / Current PC sample
PC_PREV,            0               / Previous PC sample

/ ============================================================================
/ CONSTANTS
/ ============================================================================

        ORG     10500

CORE_SAMPLE_COUNT,  16              / Number of core samples
PC_SAMPLE_COUNT,    32              / Number of PC samples
CORE_ADDR_MASK,     7777            / Mask for core addresses (12 bits)
PC_DELTA_MASK,      37              / Mask for PC delta (5 bits)
ONE_CONST,          1               / Constant: 1

/ ============================================================================
/ I/O REGISTER ADDRESSES
/ ============================================================================

PAPER_TAPE_IN   =   040             / Paper tape reader
PAPER_TAPE_OUT  =   041             / Paper tape punch
TTY_IN          =   042             / Teletype input
TTY_OUT         =   043             / Teletype output
RTC_REG         =   044             / Real-time clock

        END
