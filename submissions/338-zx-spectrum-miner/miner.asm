; ============================================================================
; ZX Spectrum Miner - Z80 Assembly
; A conceptual proof-of-work miner for the ZX Spectrum (1982)
; 
; Target: ZX Spectrum 48K
; CPU: Z80 @ 3.5 MHz
; 
; Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
; ============================================================================

; Memory Map
; ==========
; 0x8000 - Program Start
; 0x8100 - Block Header (simplified, 32 bytes)
; 0x8120 - Nonce (2 bytes)
; 0x8122 - Hash Result (32 bytes)
; 0x8142 - Target Difficulty (2 bytes)

    ORG $8000

; ============================================================================
; Main Entry Point
; ============================================================================
START:
    ; Initialize screen
    CALL CLS
    
    ; Display title
    LD HL, TITLE_TEXT
    CALL PRINT_STRING
    
    ; Initialize mining
    CALL INIT_MINER
    
    ; Start mining loop
    JP MINING_LOOP

; ============================================================================
; Clear Screen (using ROM routine)
; ============================================================================
CLS:
    LD A, $0E          ; CLS token
    RST $10            ; Print character
    RET

; ============================================================================
; Print String (HL points to string, terminated by 0)
; ============================================================================
PRINT_STRING:
    LD A, (HL)
    OR A
    RET Z
    RST $10
    INC HL
    JP PRINT_STRING

; ============================================================================
; Initialize Miner
; ============================================================================
INIT_MINER:
    ; Set initial nonce to 0
    LD HL, 0
    LD (NONCE), HL
    
    ; Set difficulty target (simplified)
    LD HL, $0100       ; Target: hash must be < 256
    LD (TARGET), HL
    
    RET

; ============================================================================
; Main Mining Loop
; ============================================================================
MINING_LOOP:
    ; Increment nonce
    LD HL, (NONCE)
    INC HL
    LD (NONCE), HL
    
    ; Display current nonce
    CALL DISPLAY_NONCE
    
    ; Compute hash (simplified XOR-based)
    CALL COMPUTE_HASH
    
    ; Check if hash meets difficulty
    CALL CHECK_DIFFICULTY
    JR NZ, MINING_LOOP
    
    ; Found a valid block!
    CALL DISPLAY_SUCCESS
    
    ; Halt
    HALT

; ============================================================================
; Display Current Nonce
; ============================================================================
DISPLAY_NONCE:
    PUSH HL
    PUSH DE
    
    ; Position cursor (row 10, col 0)
    LD A, $16          ; AT token
    RST $10
    LD A, 10           ; Row
    RST $10
    LD A, 0            ; Column
    RST $10
    
    ; Print "Nonce: "
    LD HL, NONCE_LABEL
    CALL PRINT_STRING
    
    ; Convert and print nonce value
    LD HL, (NONCE)
    CALL PRINT_NUMBER
    
    POP DE
    POP HL
    RET

; ============================================================================
; Print 16-bit Number (HL)
; ============================================================================
PRINT_NUMBER:
    ; Simplified: just print hex
    PUSH HL
    
    ; Print high byte
    LD A, H
    CALL PRINT_HEX_BYTE
    
    ; Print low byte
    LD A, L
    CALL PRINT_HEX_BYTE
    
    POP HL
    RET

; ============================================================================
; Print Hex Byte (A)
; ============================================================================
PRINT_HEX_BYTE:
    PUSH AF
    
    ; High nibble
    RRCA
    RRCA
    RRCA
    RRCA
    AND $0F
    CALL PRINT_HEX_NIBBLE
    
    ; Low nibble
    POP AF
    AND $0F
    CALL PRINT_HEX_NIBBLE
    
    RET

; ============================================================================
; Print Hex Nibble (A, 0-15)
; ============================================================================
PRINT_HEX_NIBBLE:
    CP $0A
    JR C, PRINT_HEX_DIGIT
    ADD $07            ; Adjust for A-F
PRINT_HEX_DIGIT:
    ADD $30            ; Convert to ASCII
    RST $10
    RET

; ============================================================================
; Compute Hash (Simplified XOR-based Hash)
; Input: Block header at BLOCK_HEADER, Nonce at NONCE
; Output: Hash at HASH_RESULT
; ============================================================================
COMPUTE_HASH:
    PUSH HL
    PUSH DE
    PUSH BC
    
    LD DE, BLOCK_HEADER
    LD HL, HASH_RESULT
    LD BC, 32          ; 32 bytes output
    
    ; Simple XOR hash with nonce
    LD A, (NONCE)
    LD (HL), A
    INC HL
    LD A, (NONCE+1)
    LD (HL), A
    INC HL
    
    ; XOR block header bytes
    LD B, 30
HASH_LOOP:
    LD A, (DE)
    XOR (HL)
    LD (HL), A
    INC DE
    INC HL
    DJNZ HASH_LOOP
    
    POP BC
    POP DE
    POP HL
    RET

; ============================================================================
; Check Difficulty
; Returns Z if hash < target (valid block found)
; ============================================================================
CHECK_DIFFICULTY:
    ; Compare first 2 bytes of hash with target
    LD HL, (HASH_RESULT)
    LD DE, (TARGET)
    
    ; Simple comparison
    LD A, H
    CP D
    JR C, VALID        ; High byte less than target
    JR NZ, INVALID     ; High byte greater than target
    
    ; High bytes equal, check low byte
    LD A, L
    CP E
    JR C, VALID
    JR INVALID

VALID:
    AND A              ; Set Z flag
    RET

INVALID:
    OR $FF             ; Clear Z flag
    RET

; ============================================================================
; Display Success Message
; ============================================================================
DISPLAY_SUCCESS:
    LD HL, SUCCESS_TEXT
    CALL PRINT_STRING
    
    ; Display found nonce
    LD HL, (NONCE)
    CALL PRINT_NUMBER
    
    RET

; ============================================================================
; Data Section
; ============================================================================
TITLE_TEXT:
    DEFM "ZX SPECTRUM MINER"
    DEFM 13, 10        ; CR LF
    DEFM "Wallet: RTC4325..."
    DEFM 13, 10
    DEFM "Mining..."
    DEFM 13, 10
    DEFM 0

NONCE_LABEL:
    DEFM "Nonce: $"
    DEFM 0

SUCCESS_TEXT:
    DEFM 13, 10
    DEFM "*** BLOCK FOUND! ***"
    DEFM 13, 10
    DEFM "Nonce: $"
    DEFM 0

; Memory allocations
    ORG $8100
BLOCK_HEADER:
    DS 32              ; 32 bytes block header

    ORG $8120
NONCE:
    DS 2               ; 16-bit nonce

    ORG $8122
HASH_RESULT:
    DS 32              ; 32-byte hash output

    ORG $8142
TARGET:
    DS 2               ; Difficulty target

    END START
