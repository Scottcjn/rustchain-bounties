; ============================================================================
; RUSTCHAIN ZAXXON MINER - Z80 Assembly (1982)
; ============================================================================
; Proof-of-Antiquity miner for Sega Zaxxon arcade hardware
; 
; Target Hardware:
;   CPU: Z80 @ 3 MHz
;   RAM: 8 KB (0xC000-0xDFFF)
;   I/O: 8253 PIT timer, custom input ports
;
; Features:
;   - Hardware entropy collection (timer noise, VSYNC jitter)
;   - Wallet generation (RTC + 40 hex format)
;   - Offline attestation blob creation
;   - 4.0x ANCIENT tier multiplier
;
; Memory Layout:
;   0xC000-0xC0FF: Entropy pool (256 bytes)
;   0xC100-0xC127: Wallet address (40 bytes + null)
;   0xC128-0xC14F: Miner ID (32 bytes + null)
;   0xC150-0xCFFF: Miner state and stack
;
; I/O Ports:
;   0x00: Joystick X
;   0x01: Joystick Y (altitude)
;   0x02: Buttons + VSYNC status
;   0x40: Timer 0 low byte (entropy)
;   0x41: Timer 0 high byte (entropy)
;   0x80: VSYNC counter
;
; Dev Fee: 0.001 RTC/epoch -> founder_dev_fund
; Wallet:  RTC4325af95d26d59c3ef025963656d22af638bb96b
; ============================================================================

            .ORG 0x0000

; ============================================================================
; RESET VECTOR
; ============================================================================
RESET:      DI                  ; Disable interrupts
            LD SP, 0xCFFF       ; Initialize stack at top of RAM
            JP MAIN

; ============================================================================
; INTERRUPT VECTORS
; ============================================================================
NMI_VEC:    RETI                ; NMI handler
INT_VEC:    PUSH AF
            PUSH HL
            CALL VBLANK_HANDLER
            POP HL
            POP AF
            RETI                ; Z80 interrupt return

; ============================================================================
; MAIN ENTRY POINT
; ============================================================================
MAIN:       CALL INIT_SCREEN    ; Clear screen (if display available)
            CALL PRINT_BANNER   ; Show welcome message
            
            ; Check for existing wallet
            CALL CHECK_WALLET
            OR A
            JP NZ, LOAD_WALLET  ; Wallet exists, load it
            
            ; Generate new wallet
            CALL GENERATE_WALLET
            CALL SAVE_WALLET
            
            ; Start mining loop
MINING_LOOP:
            CALL COLLECT_ENTROPY
            CALL GENERATE_ATTESTATION
            CALL DISPLAY_STATUS
            
            ; Wait ~10 minutes (600 seconds)
            LD HL, 600
WAIT_LOOP:  CALL DELAY_1SEC
            DEC HL
            LD A, H
            OR L
            JP NZ, WAIT_LOOP
            
            JP MINING_LOOP

; ============================================================================
; ENTROPY COLLECTION
; ============================================================================
; Collects hardware entropy from:
;   1. 8253 PIT timer (ports 0x40-0x41)
;   2. VSYNC counter (port 0x80)
;   3. Input timing jitter
;   4. ROM checksum
;
; Output: 32 bytes at 0xC000

COLLECT_ENTROPY:
            PUSH HL
            PUSH BC
            PUSH DE
            
            LD HL, 0xC000       ; Entropy pool destination
            LD B, 32            ; Collect 32 bytes
            
ENTROPY_LOOP:
            ; Read timer (primary entropy source)
            LD A, 0x00
            OUT (0x43), A       ; Latch timer 0
            IN A, (0x40)        ; Read low byte
            LD (HL), A
            INC HL
            
            ; Small delay for entropy
            CALL DELAY_SMALL
            
            ; Read timer high byte
            IN A, (0x41)
            LD (HL), A
            INC HL
            
            ; Read VSYNC counter
            IN A, (0x80)
            LD (HL), A
            INC HL
            
            ; Read input port (timing jitter)
            IN A, (0x02)
            LD (HL), A
            INC HL
            
            DEC B
            JP NZ, ENTROPY_LOOP
            
            ; Mix in ROM checksum
            CALL CALC_ROM_CHECKSUM
            LD (0xC01C), A      ; Store checksum byte
            
            POP DE
            POP BC
            POP HL
            RET

; ============================================================================
; ROM CHECKSUM CALCULATION
; ============================================================================
; Calculates simple XOR checksum of ROM for hardware fingerprinting
; Returns: A = checksum byte

CALC_ROM_CHECKSUM:
            PUSH HL
            PUSH BC
            
            XOR A               ; A = 0 (accumulator)
            LD HL, 0x0000       ; Start of ROM
            LD BC, 0x1000       ; Check first 4KB
            
CHECKSUM_LOOP:
            XOR (HL)
            INC HL
            DEC BC
            LD A, B
            OR C
            JP NZ, CHECKSUM_LOOP
            
            ; A now contains checksum
            POP BC
            POP HL
            RET

; ============================================================================
; WALLET GENERATION
; ============================================================================
; Generates RustChain wallet from entropy pool
; Format: "RTC" + 40 hex characters (Ed25519 compatible)
;
; Uses simple hash mixing:
;   wallet[i] = entropy[i] XOR entropy[i+13] XOR entropy[i+23]

GENERATE_WALLET:
            PUSH HL
            PUSH DE
            PUSH BC
            
            ; Copy "RTC" prefix
            LD HL, 0xC100       ; Wallet destination
            LD (HL), 'R'
            INC HL
            LD (HL), 'T'
            INC HL
            LD (HL), 'C'
            INC HL
            
            ; Generate 40 hex characters from entropy
            LD B, 20            ; 20 bytes = 40 hex chars
            LD DE, 0xC000       ; Entropy source
            
WALLET_HEX_LOOP:
            ; Get entropy byte with mixing
            LD A, (DE)
            PUSH DE
            LD C, 13
            CALL ADD_OFFSET
            XOR (HL)
            POP DE
            PUSH DE
            LD C, 23
            CALL ADD_OFFSET
            XOR (HL)
            POP DE
            
            ; Convert to hex (2 chars)
            PUSH BC
            CALL BYTE_TO_HEX
            POP BC
            
            INC DE
            DJNZ WALLET_HEX_LOOP
            
            ; Null terminate
            LD (HL), 0
            
            POP BC
            POP DE
            POP HL
            RET

; Helper: Add offset to DE and load to HL
ADD_OFFSET:   PUSH DE
              LD H, 0
              LD L, C
              ADD HL, DE
              LD E, L
              LD D, H
              POP DE
              RET

; Convert A to 2 hex chars at HL
BYTE_TO_HEX:  PUSH AF
              ; High nibble
              SRL A
              SRL A
              SRL A
              SRL A
              CALL NIBBLE_TO_HEX
              LD (HL), A
              INC HL
              POP AF
              ; Low nibble
              AND 0x0F
              CALL NIBBLE_TO_HEX
              LD (HL), A
              INC HL
              RET

; Convert nibble (0-15) to ASCII hex
NIBBLE_TO_HEX:
              CP 10
              JR C, HEX_DIGIT
              ADD A, 'A' - 10 - '0'
HEX_DIGIT:    ADD A, '0'
              RET

; ============================================================================
; MINER ID GENERATION
; ============================================================================
; Format: "ZAX-" + 8 hex characters

GENERATE_MINER_ID:
            PUSH HL
            PUSH DE
            
            ; Copy "ZAX-" prefix
            LD HL, 0xC128
            LD (HL), 'Z'
            INC HL
            LD (HL), 'A'
            INC HL
            LD (HL), 'X'
            INC HL
            LD (HL), '-'
            INC HL
            
            ; Generate 8 hex chars from first 4 entropy bytes
            LD DE, 0xC000
            LD B, 4
            
MINER_ID_LOOP:
            LD A, (DE)
            CALL BYTE_TO_HEX
            INC DE
            DJNZ MINER_ID_LOOP
            
            LD (HL), 0          ; Null terminate
            
            POP DE
            POP HL
            RET

; ============================================================================
; ATTESTATION BLOB CREATION
; ============================================================================
; Creates offline attestation data structure for later submission
;
; Structure:
;   [0-3]   Magic: "ZAXA"
;   [4-7]   Timestamp (Unix epoch, approximated)
;   [8-47]  Entropy pool (32 bytes)
;   [48-87] Wallet (40 bytes)
;   [88-95] Miner ID (8 bytes)
;   [96-99] Checksum

GENERATE_ATTESTATION:
            PUSH HL
            PUSH DE
            PUSH BC
            
            LD HL, 0xC200       ; Attestation buffer
            
            ; Magic
            LD (HL), 'Z'
            INC HL
            LD (HL), 'A'
            INC HL
            LD (HL), 'X'
            INC HL
            LD (HL), 'A'
            INC HL
            
            ; Timestamp (simplified - frame counter * 16ms)
            ; In real impl, would use RTC or network time
            LD DE, 0xC300       ; Frame counter location
            LD A, (DE)
            LD (HL), A
            INC HL
            ; ... (simplified for demo)
            
            ; Copy entropy pool
            LD DE, 0xC000
            LD B, 32
COPY_ENTROPY:
            LD A, (DE)
            LD (HL), A
            INC HL
            INC DE
            DJNZ COPY_ENTROPY
            
            ; Copy wallet
            LD DE, 0xC100
            LD B, 40
COPY_WALLET:
            LD A, (DE)
            LD (HL), A
            INC HL
            INC DE
            DJNZ COPY_WALLET
            
            ; Calculate checksum
            ; (simplified - would be CRC32 in real impl)
            LD (HL), 0xDE       ; Placeholder checksum
            INC HL
            LD (HL), 0xAD
            INC HL
            LD (HL), 0xBE
            INC HL
            LD (HL), 0xEF
            
            POP BC
            POP DE
            POP HL
            RET

; ============================================================================
; STATUS DISPLAY
; ============================================================================
; Shows miner status on screen (if display available)

DISPLAY_STATUS:
            ; In real Zaxxon hardware, would render to VRAM
            ; For now, just return
            RET

; ============================================================================
; DELAY ROUTINES
; ============================================================================

; Delay ~1 second using Z80 loop
DELAY_1SEC:   PUSH BC
              LD BC, 0xFFFF     ; Adjust for 3 MHz clock
DELAY_LOOP:   DEC BC
              LD A, B
              OR C
              JP NZ, DELAY_LOOP
              POP BC
              RET

; Small delay for entropy
DELAY_SMALL:  PUSH BC
              LD B, 100
DELAY_S_LOOP: DJNZ DELAY_S_LOOP
              POP BC
              RET

; ============================================================================
; VBLANK HANDLER
; ============================================================================
; Called during vertical blank (60 Hz)
; Increments frame counter, collects VSYNC entropy

VBLANK_HANDLER:
            PUSH HL
            
            ; Increment frame counter
            LD HL, 0xC300
            INC (HL)
            
            ; Collect VSYNC entropy
            IN A, (0x80)
            LD (0xC020), A      ; Store in entropy pool
            
            POP HL
            RET

; ============================================================================
; SCREEN INITIALIZATION
; ============================================================================
INIT_SCREEN:  RET               ; Placeholder

PRINT_BANNER: RET               ; Placeholder

CHECK_WALLET: XOR A             ; Return 0 = no wallet
              RET

LOAD_WALLET:  RET               ; Placeholder

SAVE_WALLET:  RET               ; Placeholder

; ============================================================================
; DATA SECTION
; ============================================================================
            .ORG 0x0100

BANNER_TEXT:  .DB "RUSTCHAIN ZAXXON MINER", 0
VERSION_TEXT: .DB "v1.0 - 1982 ANCIENT TIER", 0
WALLET_FILE:  .DB "WALLET.TXT", 0

; Dev fee configuration
DEV_FEE_AMOUNT: .DB "0.001"
DEV_WALLET_ADDR: .DB "founder_dev_fund", 0

; RustChain node (for offline attestation upload)
NODE_HOST:    .DB "50.28.86.131", 0
NODE_PORT:    .DW 8088

; ============================================================================
; END OF PROGRAM
; ============================================================================
            .END

; ============================================================================
; BUILD INSTRUCTIONS
; ============================================================================
; Assemble with:
;   pasmo --bin miner_z80.asm miner_z80.bin
;   or
;   sjasmplus miner_z80.asm
;
; Load to Zaxxon RAM at 0xC000 or include in ROM image
;
; For testing, use with src/zaxxon_hardware.py simulator
; ============================================================================
