; ============================================================================
; RustChain Miner for Osborne 1
; Z80 Assembly Implementation
; 
; Target: Osborne 1 (Z80 @ 4 MHz, 64 KB RAM, CP/M 2.2)
; Algorithm: OsborneHash (16-bit PoW)
; 
; Build: z80asm -i miner.asm -o miner.com
; Run: miner.com (on CP/M or emulator)
; ============================================================================

; CP/M System Equates
BDOS    EQU 0x0005      ; BDOS entry point
WBOOT   EQU 0x0000      ; Warm boot (return to CCP)

; BDOS Functions
CONOUT  EQU 2           ; Console output
PRINTS  EQU 9           ; Print string

; Program Origin (CP/M .COM files load at 0x0100)
        ORG 0x0100

; ============================================================================
; MAIN ENTRY POINT
; ============================================================================

START:
        LD   SP, STACK  ; Initialize stack
        
        ; Print header
        LD   DE, HEADER
        CALL PRINT_STRING
        
        ; Print block data
        LD   DE, BLOCK_DATA
        CALL PRINT_STRING
        
        ; Initialize mining parameters
        LD   HL, BLOCK_DATA     ; Block data pointer
        LD   BC, BLOCK_LEN      ; Block length
        LD   DE, 0x1234         ; Seed value
        LD   (HASH_SEED), DE
        
        ; Print mining status
        LD   DE, MSG_MINING
        CALL PRINT_STRING
        
        ; Start mining
        LD   (NONCE), 0         ; Nonce = 0
        
MINING_LOOP:
        ; Load current nonce
        LD   DE, (NONCE)
        
        ; Hash block with nonce
        PUSH DE                 ; Save nonce
        PUSH BC                 ; Save block length
        CALL OSBORNE_HASH     ; Returns hash in DE
        POP BC
        POP DE
        
        ; Check if hash meets difficulty (leading zeros)
        ; Threshold for 3 leading zeros: 0x1FFF
        LD   HL, 0x1FFF
        CALL COMPARE_DE_HL      ; Compare DE with HL
        
        ; If hash <= threshold, we found it!
        JP   C, FOUND_NONCE     ; Carry set if DE < HL
        
        ; Increment nonce
        LD   HL, NONCE
        INC  (HL)
        JP   NZ, MINING_LOOP    ; If low byte != 0, continue
        INC  HL
        INC  (HL)
        JP   NZ, MINING_LOOP    ; If high byte != 0, continue
        
        ; Nonce overflow - no solution in 16-bit range
        LD   DE, MSG_FAILED
        CALL PRINT_STRING
        JP   WBOOT             ; Return to CP/M

; ============================================================================
; FOUND VALID NONCE!
; ============================================================================

FOUND_NONCE:
        ; Print success message
        LD   DE, MSG_SUCCESS
        CALL PRINT_STRING
        
        ; Print nonce value
        LD   DE, (NONCE)
        CALL PRINT_HEX16
        CALL PRINT_NEWLINE
        
        ; Print hash value
        LD   DE, (HASH_RESULT)
        CALL PRINT_HEX16
        CALL PRINT_NEWLINE
        
        ; Print bounty info
        LD   DE, MSG_BOUNTY
        CALL PRINT_STRING
        
        ; Return to CP/M
        JP   WBOOT

; ============================================================================
; OSBORNE_HASH - Compute 16-bit hash of block + nonce
; Input:  HL = block pointer
;         BC = block length
;         DE = seed
; Output: DE = hash value
; Clobbers: A, HL, BC
; ============================================================================

OSBORNE_HASH:
        PUSH HL
        PUSH BC
        
        ; Initialize hash with seed
        ; DE already contains seed
        
        ; Add nonce to hash (nonce is last 2 bytes conceptually)
        ; For simplicity, we'll process block then mix in nonce
        
HASH_LOOP:
        LD   A, B
        OR   C
        JP   Z, HASH_FINAL      ; If BC == 0, done
        
        ; Load byte from block
        LD   A, (HL)
        
        ; Add to hash (DE)
        ADD  A, E
        LD   E, A
        LD   A, D
        ADC  A, 0
        LD   D, A
        
        ; Rotate left by 1
        CALL ROTATE_LEFT_DE
        
        ; XOR mixing: DE = DE XOR (DE >> 2)
        CALL MIX_XOR
        
        INC  HL
        DEC  BC
        JP   HASH_LOOP

HASH_FINAL:
        ; Final mixing
        CALL ROTATE_LEFT_DE     ; Rotate left 1
        CALL ROTATE_LEFT_DE     ; Rotate left 2
        CALL ROTATE_LEFT_DE     ; Rotate left 3
        
        ; XOR with shifted version
        LD   A, D
        RRCA
        RRCA
        RRCA
        RRCA
        LD   B, A              ; B = D >> 4
        LD   A, E
        RRCA
        RRCA
        RRCA
        RRCA
        LD   C, A              ; C = E >> 4
        
        LD   A, D
        XOR  B
        LD   D, A
        LD   A, E
        XOR  C
        LD   E, A
        
        ; Mask to 16 bits
        LD   A, D
        AND  0xFF
        LD   D, A
        
        ; Store result
        LD   (HASH_RESULT), DE
        
        POP BC
        POP HL
        RET

; ============================================================================
; ROTATE_LEFT_DE - Rotate DE left by 1 bit
; ============================================================================

ROTATE_LEFT_DE:
        LD   A, D
        RLA                    ; Rotate D left through carry
        LD   D, A
        LD   A, E
        RLA                    ; Rotate E left through carry
        LD   E, A
        RET

; ============================================================================
; MIX_XOR - XOR DE with (DE rotated right by 2)
; ============================================================================

MIX_XOR:
        PUSH DE
        
        ; Rotate right by 2
        LD   A, D
        RRCA
        RRCA
        LD   B, A
        LD   A, E
        RRCA
        RRCA
        LD   C, A
        
        ; XOR
        LD   A, D
        XOR  B
        LD   D, A
        LD   A, E
        XOR  C
        LD   E, A
        
        POP DE
        RET

; ============================================================================
; COMPARE_DE_HL - Compare DE with HL
; Returns: Carry set if DE < HL
; ============================================================================

COMPARE_DE_HL:
        LD   A, D
        CP   H
        RET  C                 ; DE < HL
        RET  NZ                ; DE > HL
        LD   A, E
        CP   L
        RET                    ; Carry set if E < L

; ============================================================================
; PRINT_STRING - Print $-terminated string at DE
; ============================================================================

PRINT_STRING:
        PUSH DE
        PUSH BC
        PUSH AF
        
        LD   C, PRINTS
        CALL BDOS
        
        POP AF
        POP BC
        POP DE
        RET

; ============================================================================
; PRINT_HEX16 - Print DE as 4-digit hex
; ============================================================================

PRINT_HEX16:
        PUSH DE
        PUSH BC
        PUSH AF
        
        ; Print high nibble of D
        LD   A, D
        RRCA
        RRCA
        RRCA
        RRCA
        CALL PRINT_NIBBLE
        
        ; Print low nibble of D
        LD   A, D
        AND  0x0F
        CALL PRINT_NIBBLE
        
        ; Print high nibble of E
        LD   A, E
        RRCA
        RRCA
        RRCA
        RRCA
        CALL PRINT_NIBBLE
        
        ; Print low nibble of E
        LD   A, E
        AND  0x0F
        CALL PRINT_NIBBLE
        
        POP AF
        POP BC
        POP DE
        RET

PRINT_NIBBLE:
        AND  0x0F
        ADD  A, '0'
        CP   '9' + 1
        JR   C, PRINT_CHAR
        ADD  A, 7              ; Convert to A-F
PRINT_CHAR:
        LD   E, A
        LD   C, CONOUT
        CALL BDOS
        RET

PRINT_NEWLINE:
        LD   DE, NEWLINE
        CALL PRINT_STRING
        RET

; ============================================================================
; DATA SECTION
; ============================================================================

HASH_SEED:    DS 2            ; Seed storage
HASH_RESULT:  DS 2            ; Hash result storage
NONCE:        DS 2            ; Current nonce

HEADER:
        DB '=== Osborne 1 Miner ===', 0x0D, 0x0A, '$'

MSG_MINING:
        DB 'Mining...', 0x0D, 0x0A, '$'

MSG_SUCCESS:
        DB 'FOUND! Nonce: 0x', '$'

MSG_FAILED:
        DB 'No solution found', 0x0D, 0x0A, '$'

MSG_BOUNTY:
        DB 'Bounty: 200 RTC', 0x0D, 0x0A
        DB 'Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b', 0x0D, 0x0A, '$'

NEWLINE:
        DB 0x0D, 0x0A, '$'

BLOCK_DATA:
        DB 'RustChain-Osborne1-Bounty-408', 0
BLOCK_LEN:
        EQU $ - BLOCK_DATA - 1  ; Length without null terminator

; Stack at end of available memory
        ORG 0x00FF + 0x1000   ; ~4KB stack (adjust as needed)
STACK:

        END START
