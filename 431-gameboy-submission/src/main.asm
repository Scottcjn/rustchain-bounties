; ═══════════════════════════════════════════════════════════
; RustChain Game Boy Miner - Main Entry Point
; ═══════════════════════════════════════════════════════════
; 
; A native Game Boy attestation miner for RustChain blockchain
; Communicates via link cable with Raspberry Pi Pico bridge
;
; Author: AutoClaw Subagent
; License: Apache 2.0
; Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
; ═══════════════════════════════════════════════════════════

INCLUDE "include/gb.inc"

; ───────────────────────────────────────────────────────────
; Cartridge Header
; ───────────────────────────────────────────────────────────

SECTION "Header", ROM0[$0100]

    ; Entry point: jump to main
    nop
    jp Main

    ; Nintendo logo (required for boot ROM bypass)
    DB $CE, $ED, $66, $66, $CC, $0D, $00, $0B
    DB $03, $73, $00, $83, $00, $0C, $00, $0D
    DB $00, $08, $11, $1F, $88, $89, $00, $0E
    DB $DC, $CC, $6E, $E6, $DD, $DD, $D9, $99
    DB $BB, $BB, $67, $63, $6E, $0E, $EC, $CC
    DB $DD, $DC, $99, $9F, $BB, $B9, $33, $3E

    ; Game title (16 bytes max)
    DB "RUSTCHAIN MINER"

    ; CGB flag: $80 = supports CGB, $00 = GB only
    DB $00

    ; SGB flag: not supported
    DB $00

    ; Cartridge type: $01 = MBC1
    DB CART_MBC1

    ; ROM size: $02 = 32 KB (2 banks)
    DB $02

    ; RAM size: $01 = 8 KB (for SRAM wallet storage)
    DB $01

    ; Destination code: $01 = non-Japanese
    DB $01

    ; ROM version: $00
    DB $00

    ; Header checksum (calculated by rgbfix)
    DB $00

    ; Global checksum (calculated by rgbfix)
    DW $0000

; ───────────────────────────────────────────────────────────
; Main Code (ROM Bank 0)
; ───────────────────────────────────────────────────────────

SECTION "Main Code", ROM0[$0150]

Main:
    ; ───────────────────────────────────────────────────────
    ; Initialization
    ; ───────────────────────────────────────────────────────
    
    ; Disable interrupts during setup
    di
    
    ; Wait for LCD to be in VBlank (safe to initialize)
.wait_vblank
    ld a, [LY]
    cp $90          ; VBlank starts at line 144 ($90)
    jr c, .wait_vblank
    
    ; Initialize stack pointer
    ld sp, WRAM_STACK_BASE
    
    ; Clear WRAM (optional, for debugging)
    call ClearWRAM
    
    ; Initialize serial communication
    call Serial_Init
    
    ; Initialize SHA-256 (load constants)
    call SHA256_Init
    
    ; Load wallet ID from SRAM (or use default)
    call LoadWalletID
    
    ; Enable serial interrupts
    ld a, IE_SERIAL
    ld [IE], a
    ei              ; Enable interrupts
    
    ; ───────────────────────────────────────────────────────
    ; Main Loop
    ; ───────────────────────────────────────────────────────
    
.main_loop
    ; Check for serial data
    call Serial_Poll
    
    ; If we have a challenge, process it
    ld a, [wSerialChallengeReady]
    and a
    jr z, .no_challenge
    
    ; Process challenge (compute SHA-256)
    call ProcessChallenge
    
    ; Clear challenge flag
    xor a
    ld [wSerialChallengeReady], a
    
.no_challenge
    ; Wait a bit before next poll (power saving)
    call Delay_Short
    
    ; Go to HALT mode (wait for interrupt)
    halt
    
    jp .main_loop

; ───────────────────────────────────────────────────────────
; Clear Work RAM
; ───────────────────────────────────────────────────────────

ClearWRAM:
    push bc
    push hl
    
    ld hl, WRAM0
    ld bc, $1000    ; 4 KB
.clear_loop
    ld [hl], $00
    inc hl
    dec bc
    ld a, b
    or c
    jr nz, .clear_loop
    
    pop hl
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Load Wallet ID from SRAM
; ───────────────────────────────────────────────────────────
; Wallet is stored in cartridge SRAM (battery-backed)
; If SRAM not available, use hardcoded default

LoadWalletID:
    push bc
    push de
    push hl
    
    ; Enable SRAM (MBC1)
    ld hl, $0000
    ld [hl], $0A    ; Enable SRAM
    
    ; Read wallet ID from SRAM address $A000
    ld de, WRAM_WALLET_ID
    ld hl, $A000
    ld bc, 32       ; 32 bytes wallet ID
.copy_loop
    ld a, [hl]
    ld [de], a
    inc hl
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copy_loop
    
    ; Disable SRAM
    ld hl, $0000
    ld [hl], $00
    
    pop hl
    pop de
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Process Challenge
; ───────────────────────────────────────────────────────────
; Input: Nonce in WRAM_NONCE (32 bytes)
;        Wallet ID in WRAM_WALLET_ID (32 bytes)
; Output: Hash in WRAM_HASH_STATE (32 bytes)

ProcessChallenge:
    push bc
    push de
    push hl
    
    ; Prepare message: nonce || wallet_id (64 bytes = 1 block)
    ; Copy nonce to hash work area
    ld de, WRAM_HASH_WORK
    ld hl, WRAM_NONCE
    ld bc, 32
.copy_nonce
    ld a, [hl+]
    ld [de+], a
    dec bc
    ld a, b
    or c
    jr nz, .copy_nonce
    
    ; Append wallet ID
    ld hl, WRAM_WALLET_ID
    ld bc, 32
.copy_wallet
    ld a, [hl+]
    ld [de+], a
    dec bc
    ld a, b
    or c
    jr nz, .copy_wallet
    
    ; Compute SHA-256
    call SHA256_Compute
    
    ; Send attestation response via serial
    call Serial_SendAttest
    
    pop hl
    pop de
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Delay Routines
; ───────────────────────────────────────────────────────────

Delay_Short:
    ; ~100ms delay using timer
    push bc
    
    ld bc, $3000    ; Adjust for desired delay
.delay_loop
    dec bc
    ld a, b
    or c
    jr nz, .delay_loop
    
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Variables (Work RAM)
; ───────────────────────────────────────────────────────────

SECTION "Miner Variables", WRAM0[$C800]

wSerialChallengeReady:  DS 1    ; Flag: challenge received
wSerialError:           DS 1    ; Last error code
wSerialBuffer:          DS 64   ; Serial message buffer
wHashComplete:          DS 1    ; Flag: hash computation done

; ───────────────────────────────────────────────────────────
; Interrupt Handlers (High RAM for speed)
; ───────────────────────────────────────────────────────────

SECTION "Serial Interrupt Handler", HRAM[$FFF8]

; Serial interrupt handler - called when transfer complete
Serial_Interrupt:
    push af
    push bc
    
    ; Read received byte
    ld a, [SB]
    
    ; Store in buffer (simplified - full implementation needed)
    ld hl, wSerialBuffer
    ld [hl], a
    
    ; Check if this is start of challenge
    cp MSG_CHALLENGE
    jr z, .challenge_start
    
    ; Continue receiving...
    jr .done
    
.challenge_start
    ; Set challenge ready flag
    ld a, 1
    ld [wSerialChallengeReady], a
    
.done
    ; Clear interrupt flag
    ld a, IF_SERIAL
    ld [IF], a
    
    pop bc
    pop af
    reti

; ───────────────────────────────────────────────────────────
; Include Other Modules
; ───────────────────────────────────────────────────────────

INCLUDE "src/serial.asm"
INCLUDE "src/sha256.asm"

; ───────────────────────────────────────────────────────────
; End of ROM
; ───────────────────────────────────────────────────────────

SECTION "End Marker", ROM0[$7FFF]
    DB $FF  ; Padding
