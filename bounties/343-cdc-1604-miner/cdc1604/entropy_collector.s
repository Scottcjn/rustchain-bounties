C        RUSTCHAIN CDC 1604 ENTROPY COLLECTOR - ASSEMBLY VERSION
C        "Pantheon Edition" - For CDC 1604 (1960)
C        
C        Pure assembly implementation for maximum performance
C        and minimal memory footprint.
C
C        Assembler: CDC 1604 Assembly
C        Memory: ~500 words (out of 32K available)
C
C        Usage:
C          sim> cdc1604
C          sim> load entropy_collector.bin
C          sim> attach tp0 output.tap
C          sim> go
C
C=======================================================================
C        EQUATES AND CONSTANTS
C=======================================================================
C
ZERO     DEC     0               / Constant zero
ONE      DEC     1               / Constant one
TIMING_CT DEC    32              / Number of timing samples
JITTER_CT DEC    16              / Number of jitter samples
AUDIO_CT DEC     8               / Number of audio samples
BLOCK_SIZE DEC   1000            / Memory block stride
LOOP_COUNT DEC   999             / Jitter loop iterations
C
C        I/O DEVICE CODES
C
TIMER    OCT     1               / Timer device
CONSOLE  OCT     2               / Console I/O
PUNCH    OCT     7               / Paper tape punch
C
C        MEMORY LOCATIONS
C
         ORG     1000            / Program starts at word 1000
C
C=======================================================================
C        MAIN PROGRAM
C=======================================================================
C
START    HPR                      / Halt and prepare
         LXA     1,ZERO          / Index 1 = 0 (counter)
         LXA     2,TIMING_CT     / Index 2 = 32 (timing count)
         LXA     3,ZERO          / Index 3 = 0 (result storage offset)
C
C        Print banner
         LLM     BANNER          / Load message
         OUT     CONSOLE         / Print to console
C
C=======================================================================
C        PHASE 1: CORE MEMORY TIMING
C=======================================================================
C
TIMING   CLA     ZERO            / Clear accumulator
         STA     TIMER           / Reset timer
         LXA     4,BLOCK_SIZE    / Load block size
         LXA     5,1             / Load stride
         MLA     1,4             / Multiply: addr = i * 1000
         CLA     0,1             / Read memory at address
         NOP                      / Delay slot (timing)
         NOP                      / Delay slot
         INP     TIMER,A         / Read timer value
         STA     TIMING_DATA,1   / Store timing result
         LXA     1,1             / Increment counter
         TXJ     TIMING,2        / Transfer index, jump if > 0
C
         LLM     TIMING_MSG      / "Phase 1 complete"
         OUT     CONSOLE
C
C=======================================================================
C        PHASE 2: INSTRUCTION JITTER
C=======================================================================
C
         LXA     1,ZERO          / Reset counter
         LXA     2,JITTER_CT     / Jitter sample count
C
JITTER   CLA     ZERO            / Clear A
         STA     TIMER           / Reset timer
         LXA     3,LOOP_COUNT    / Inner loop count
C
JLOOP    CLA     3               / Load counter
         ADD     ONE             / Increment
         STA     3               / Store back
         TXJ     JLOOP,3         / Loop until count reached
C
         INP     TIMER,A         / Read timer
         STA     JITTER_DATA,1   / Store result
         LXA     1,1             / Increment outer counter
         TXJ     JITTER,2        / Continue if samples remain
C
         LLM     JITTER_MSG      / "Phase 2 complete"
         OUT     CONSOLE
C
C=======================================================================
C        PHASE 3: AUDIO DAC SAMPLING
C=======================================================================
C
         LXA     1,ZERO
         LXA     2,AUDIO_CT
C
AUDIO    CLA     ALL_ONES        / Load test pattern (all 1s)
         NOP                      / Allow DAC to settle
         INP     CONSOLE,A       / Read audio DAC (bits 47-45)
         ALS     45              / Shift to low bits
         STA     AUDIO_DATA,1    / Store sample
         LXA     1,1
         TXJ     AUDIO,2
C
         LLM     AUDIO_MSG       / "Phase 3 complete"
         OUT     CONSOLE
C
C=======================================================================
C        PHASE 4: HASH GENERATION
C=======================================================================
C
C        Initialize hash state
         CLA     HASH0_INIT
         STA     HASH0
         CLA     HASH1_INIT
         STA     HASH1
         CLA     HASH2_INIT
         STA     HASH2
         CLA     HASH3_INIT
         STA     HASH3
C
C        Mix timing data into hash
         LXA     1,ZERO
         LXA     2,TIMING_CT
C
HMIX     CLA     TIMING_DATA,1   / Load timing sample
         XOR     HASH0           / XOR into hash state
         RLS     5               / Rotate left 5
         STA     HASH0
C
         CLA     JITTER_DATA,1   / Also mix jitter
         XOR     HASH1
         RLS     7
         STA     HASH1
C
         LXA     1,1
         TXJ     HMIX,2
C
C        Additional mixing rounds
         LXA     2,8             / 8 rounds
C
MROUND   CLA     HASH0
         ADD     HASH1
         STA     HASH0
         CLA     HASH1
         RLS     13
         STA     HASH1
         CLA     HASH2
         ADD     HASH3
         STA     HASH2
         CLA     HASH3
         RLS     17
         STA     HASH3
         CLA     HASH0
         XOR     HASH3
         STA     HASH0
         CLA     HASH2
         XOR     HASH1
         STA     HASH2
         TXJ     MROUND,2
C
         LLM     HASH_MSG        / "Hash generated"
         OUT     CONSOLE
C
C=======================================================================
C        PHASE 5: WALLET GENERATION
C=======================================================================
C
C        Extract wallet ID from hash
C        Format: RTC + 40 hex chars
C
         LLM     WALLET_PREFIX   / "RTC"
         OUT     CONSOLE
C
         LXA     1,ZERO
         LXA     2,20            / 20 bytes = 40 hex chars
C
WEXTRACT CLA     HASH0
         ALS     4               / Shift to get nibble
         ANA     HEX_MASK        / Mask to 4 bits
         CALL    HEX_CONV        / Convert to hex char
         OUT     CONSOLE
C
         CLA     HASH0
         ANA     HEX_MASK
         CALL    HEX_CONV
         OUT     CONSOLE
C
         LXA     1,1
         TXJ     WEXTRACT,2
C
C        Output newline
         CLA     NEWLINE
         OUT     CONSOLE
C
C        Output miner ID
         LLM     MINER_PREFIX    / "CDC1604-"
         OUT     CONSOLE
C
         LXA     1,0
         LXA     2,8
C
MEXTRACT CLA     HASH0
         ALS     4
         ANA     HEX_MASK
         CALL    HEX_CONV
         OUT     CONSOLE
         LXA     1,1
         TXJ     MEXTRACT,2
C
         CLA     NEWLINE
         OUT     CONSOLE
C
C=======================================================================
C        PHASE 6: PUNCH TO PAPER TAPE
C=======================================================================
C
         LLM     PUNCH_MSG
         OUT     CONSOLE
C
         LLM     PUNCH_START     / Start tape marker
         OUT     PUNCH
C
C        Punch wallet ID
         LXA     1,0
         LXA     2,43
C
WPUNCH   CLA     WALLET_BUF,1
         OUT     PUNCH
         LXA     1,1
         TXJ     WPUNCH,2
C
         LLM     PUNCH_END       / End tape marker
         OUT     PUNCH
C
         LLM     COMPLETE_MSG
         OUT     CONSOLE
C
C        Halt
         HRS     0
C
C=======================================================================
C        DATA STORAGE
C=======================================================================
C
         ORG     2000            / Data section
C
TIMING_DATA REZ    TIMING_CT      / 32 words for timing
JITTER_DATA REZ    JITTER_CT      / 16 words for jitter
AUDIO_DATA  REZ    AUDIO_CT       / 8 words for audio
C
HASH0     REZ     1               / Hash state
HASH1     REZ     1
HASH2     REZ     1
HASH3     REZ     1
C
WALLET_BUF REZ    43              / Wallet ID buffer
C
C        Constants
C
HASH0_INIT OCT    67452301        / Hash initialization constants
HASH1_INIT OCT    EFCDAB89
HASH2_INIT OCT    98BADCFE
HASH3_INIT OCT    10325476
C
ALL_ONES OCT     777777777777777  / All bits set
HEX_MASK  OCT     17              / Mask for 4 bits
NEWLINE   OCT     12              / Line feed
C
C        Messages
C
BANNER    HLT     RUSTCHAIN CDC 1604 ENTROPY COLLECTOR
          HLT     Pantheon Edition
          HLT     ================================
          OCT     0
C
TIMING_MSG HLT    Phase 1: Timing complete
          OCT     0
C
JITTER_MSG HLT    Phase 2: Jitter complete
          OCT     0
C
AUDIO_MSG HLT     Phase 3: Audio complete
          OCT     0
C
HASH_MSG  HLT     Phase 4: Hash generated
          OCT     0
C
WALLET_PREFIX HLT RTC
          OCT     0
C
MINER_PREFIX HLT  CDC1604-
          OCT     0
C
PUNCH_MSG HLT     Punching to tape...
          OCT     0
C
COMPLETE_MSG HLT  COMPLETE - Wallet ready
          OCT     0
C
PUNCH_START OCT   2                 / Tape start marker
PUNCH_END   OCT   3                 / Tape end marker
C
C        Subroutines
C
HEX_CONV  ENTRY                     / Convert nibble to hex char
          CAS     HEX_TABLE         / Case jump on accumulator
          HRS     0                 / Return
C
HEX_TABLE OCT     60                / '0'
          OCT     61                / '1'
          OCT     62                / '2'
          OCT     63                / '3'
          OCT     64                / '4'
          OCT     65                / '5'
          OCT     66                / '6'
          OCT     67                / '7'
          OCT     70                / '8' (octal)
          OCT     71                / '9'
          OCT     61                / 'A'
          OCT     62                / 'B'
          OCT     63                / 'C'
          OCT     64                / 'D'
          OCT     65                / 'E'
          OCT     66                / 'F'
C
         END     START
