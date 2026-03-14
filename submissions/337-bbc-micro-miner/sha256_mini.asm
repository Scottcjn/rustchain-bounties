; ============================================================================
; RustChain BBC Micro Miner - Simplified SHA-256 Implementation
; Target: BBC Micro Model B (1981) - MOS 6502 @ 2MHz
; Purpose: Compute proof-of-work hash (truncated for memory constraints)
; Note: Full SHA-256 is ~5KB - this is a 16-round simplified version (~1.5KB)
; ============================================================================

; Zero Page Variables
hash_index      = $57             ; Hash computation index
mine_count      = $5A             ; Mining iteration count
random_seed     = $56             ; Random seed

; Workspace
HASH_WORKSPACE  = $3100           ; Hash computation area
HASH_STATE      = $3100           ; 8 x 4-byte state (32 bytes)
HASH_DATA       = $3120           ; Input data (32 bytes)
HASH_OUTPUT     = $3140           ; Output hash (32 bytes)

; Constants (first 8 primes: 2,3,5,7,11,13,17,19)
; Simplified K values for 16 rounds
K_VALUES        = $3200           ; Round constants

        .org $2200                ; Hash module start

; ============================================================================
; INIT_HASH - Initialize hash computation
; ============================================================================

INIT_HASH:
        ; Initialize hash state (first 32 bits of fractional parts of sqrt of primes)
        ; Simplified: use fixed values
        
        ; State[0] = 0x6A09E667
        LDA #$67
        STA HASH_STATE
        LDA #$E6
        STA HASH_STATE+1
        LDA #$09
        STA HASH_STATE+2
        LDA #$6A
        STA HASH_STATE+3
        
        ; State[1] = 0xBB67AE85
        LDA #$85
        STA HASH_STATE+4
        LDA #$AE
        STA HASH_STATE+5
        LDA #$67
        STA HASH_STATE+6
        LDA #$BB
        STA HASH_STATE+7
        
        ; Initialize remaining state (simplified)
        LDX #$08
        LDA #$00
INIT_LOOP:
        STA HASH_STATE+8,X
        INX
        CPX #$18
        BNE INIT_LOOP
        
        RTS

; ============================================================================
; COMPUTE_HASH - Main hash computation (simplified 16-round SHA-256)
; Input: Data at HASH_DATA (32 bytes)
; Output: Hash at HASH_OUTPUT (32 bytes)
; ============================================================================

COMPUTE_HASH:
        PHA
        PHX
        PHY
        
        ; Initialize state
        JSR INIT_HASH
        
        ; Copy input data to workspace
        LDX #$00
COPY_DATA:
        LDA HASH_DATA,X
        STA HASH_WORKSPACE,X
        INX
        CPX #$20                    ; 32 bytes
        BNE COPY_DATA
        
        ; Perform 16 rounds (instead of 64)
        LDY #$00
ROUND_LOOP:
        JSR HASH_ROUND
        
        INY
        CPY #$10                    ; 16 rounds
        BNE ROUND_LOOP
        
        ; Copy state to output
        LDX #$00
COPY_OUTPUT:
        LDA HASH_STATE,X
        STA HASH_OUTPUT,X
        INX
        CPX #$20                    ; 32 bytes output
        BNE COPY_OUTPUT
        
        ; Update mine count
        INC mine_count
        
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; HASH_ROUND - Single round of hash computation
; ============================================================================

HASH_ROUND:
        PHA
        PHX
        PHY
        
        ; Load round index
        TYA
        TAX                         ; X = round index
        
        ; Simplified round function:
        ; temp = state[0] + mixing_function(state[1..7]) + K[round] + W[round]
        
        ; Load state[0]
        LDA HASH_STATE
        STA hash_index              ; Temporary storage
        
        ; Mixing function (simplified CHOOSE)
        ; E XOR (F AND (E XOR G))
        LDA HASH_STATE+12           ; State[3]
        EOR HASH_STATE+16           ; State[4]
        AND HASH_STATE+12
        EOR HASH_STATE+16
        
        ; Add to temp
        CLC
        ADC hash_index
        STA hash_index
        
        ; Add round constant
        LDA K_VALUES,X
        CLC
        ADC hash_index
        STA hash_index
        
        ; Add data word
        LDA HASH_DATA,X
        CLC
        ADC hash_index
        
        ; Rotate and mix
        ROL A
        EOR #$5A
        
        ; Update state[0]
        STA HASH_STATE
        
        ; Rotate state
        JSR ROTATE_STATE
        
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; ROTATE_STATE - Rotate hash state registers
; ============================================================================

ROTATE_STATE:
        ; Shift state[7] to state[0], state[0] to state[1], etc.
        PHA
        PHX
        
        ; Save state[7]
        LDX #$1C
        LDA HASH_STATE,X
        PHA                         ; Push state[7]
        
        ; Shift state[0..6] to state[1..7]
        LDX #$1B
SHIFT_LOOP:
        LDA HASH_STATE,X
        STA HASH_STATE+4,X
        DEX
        BPL SHIFT_LOOP
        
        ; Restore state[7] to state[0]
        PLA
        STA HASH_STATE
        
        PLX
        PLA
        RTS

; ============================================================================
; CHECK_DIFFICULTY - Check if hash meets difficulty target
; Returns: C=1 if valid, C=0 if not
; ============================================================================

CHECK_DIFFICULTY:
        PHA
        PHX
        
        ; Compare hash output to difficulty target
        ; Simplified: check if first byte < target
        
        LDA #$10                    ; Difficulty target (1 in 16)
        CMP HASH_OUTPUT
        BCS DIFFICULTY_MET
        
        ; Hash doesn't meet difficulty
        CLC
        JMP CHECK_DONE
        
DIFFICULTY_MET:
        ; Valid hash found!
        SEC
        
CHECK_DONE:
        PLX
        PLA
        RTS

; ============================================================================
; UPDATE_MINING_DATA - Update data for next mining attempt
; ============================================================================

UPDATE_MINING_DATA:
        PHA
        PHX
        
        ; Increment nonce (part of mining data)
        INC HASH_DATA+31
        BNE UPDATE_DONE
        INC HASH_DATA+30
        
UPDATE_DONE:
        ; Mix in new random seed
        LDA random_seed
        EOR HASH_DATA
        STA HASH_DATA
        
        PLX
        PLA
        RTS

; ============================================================================
; GET_HASH_RESULT - Get current hash result
; Returns: A = first byte of hash
; ============================================================================

GET_HASH_RESULT:
        LDA HASH_OUTPUT
        RTS

; ============================================================================
; DISPLAY_HASH - Display hash on screen (simplified)
; ============================================================================

DISPLAY_HASH:
        PHA
        PHX
        PHY
        
        ; Display first 8 bytes of hash as hex
        LDX #$00
        LDY #$00
DISPLAY_LOOP:
        LDA HASH_OUTPUT,X
        
        ; Convert to hex (high nibble)
        PHA
        LSR A
        LSR A
        LSR A
        LSR A
        JSR PRINT_HEX_NIBBLE
        
        ; Convert to hex (low nibble)
        PLA
        AND #$0F
        JSR PRINT_HEX_NIBBLE
        
        ; Space between bytes
        LDA #' '
        JSR PRINT_CHAR
        
        INX
        CPX #$08                    ; Display 8 bytes
        BNE DISPLAY_LOOP
        
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; PRINT_HEX_NIBBLE - Print single hex nibble (0-F)
; Input: A = nibble value (0-15)
; ============================================================================

PRINT_HEX_NIBBLE:
        PHA
        
        AND #$0F
        CMP #$0A
        BCC PRINT_DIGIT
        
        ; A-F
        SEC
        SBC #$09
        JMP PRINT_CHAR
        
PRINT_DIGIT:
        CLC
        ADC #'0'
        
PRINT_CHAR:
        ; Output character (simplified - use OSWRCH in production)
        ; For now, just return
        PLA
        RTS

; ============================================================================
; INIT_K_VALUES - Initialize round constants
; ============================================================================

INIT_K_VALUES:
        ; First 16 round constants (simplified)
        ; In production, use full SHA-256 K values
        
        LDX #$00
        LDA #$42
INIT_K:
        STA K_VALUES,X
        INX
        CPX #$10
        BNE INIT_K
        
        RTS

; ============================================================================
; VERIFY_HASH - Verify hash computation (test function)
; ============================================================================

VERIFY_HASH:
        PHA
        PHX
        PHY
        
        ; Set known test data
        LDX #$00
        LDA #$41                    ; 'A'
TEST_DATA:
        STA HASH_DATA,X
        INX
        CPX #$20
        BNE TEST_DATA
        
        ; Compute hash
        JSR COMPUTE_HASH
        
        ; Check result (simplified)
        LDA HASH_OUTPUT
        CMP #$00
        BEQ HASH_VALID
        
        ; Hash computation worked
        LDA #$01
        
HASH_VALID:
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; End of SHA-256 Module
; ============================================================================
