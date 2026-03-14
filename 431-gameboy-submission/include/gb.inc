; ═══════════════════════════════════════════════════════════
; Game Boy Hardware Register Definitions
; ═══════════════════════════════════════════════════════════
; Reference: https://gbdev.io/pandocs/Memory_Map.html

; ───────────────────────────────────────────────────────────
; I/O Registers ($FF00-$FF7F)
; ───────────────────────────────────────────────────────────

DEF P1_JOYP     EQU $FF00  ; Joypad input
DEF SB          EQU $FF01  ; Serial transfer data
DEF SC          EQU $FF02  ; Serial transfer control
DEF DIV         EQU $FF04  ; Divider register
DEF TIMA        EQU $FF05  ; Timer counter
DEF TMA         EQU $FF06  ; Timer modulo
DEF TAC         EQU $FF07  ; Timer control
DEF IF          EQU $FF0F  ; Interrupt flag

; Serial Control Bits
DEF SC_TRANSFER EQU $80    ; Transfer enable (bit 7)
DEF SC_CLOCK    EQU $01    ; Clock select (bit 0): 0=external, 1=internal

; Interrupt Flags
DEF IF_VBLANK   EQU $01    ; V-Blank interrupt
DEF IF_STAT     EQU $02    ; STAT interrupt
DEF IF_TIMER    EQU $04    ; Timer overflow
DEF IF_SERIAL   EQU $08    ; Serial transfer complete
DEF IF_JOYPAD   EQU $10    ; Joypad input

; ───────────────────────────────────────────────────────────
; Interrupt Vectors
; ───────────────────────────────────────────────────────────

DEF VBLANK_INT  EQU $0040  ; V-Blank interrupt vector
DEF STAT_INT    EQU $0048  ; LCD STAT interrupt vector
DEF TIMER_INT   EQU $0050  ; Timer overflow interrupt vector
DEF SERIAL_INT  EQU $0058  ; Serial transfer complete interrupt vector
DEF JOYPAD_INT  EQU $0060  ; Joypad input interrupt vector

; ───────────────────────────────────────────────────────────
; Memory Areas
; ───────────────────────────────────────────────────────────

DEF VRAM        EQU $8000  ; Video RAM (8 KB)
DEF WRAM0       EQU $C000  ; Work RAM bank 0 (4 KB)
DEF WRAM1       EQU $D000  ; Work RAM bank 1 (4 KB, CGB only)
DEF OAM         EQU $FE00  ; Object Attribute Memory (160 bytes)
DEF HRAM        EQU $FF80  ; High RAM (127 bytes)
DEF IE          EQU $FFFF  ; Interrupt Enable register

; ───────────────────────────────────────────────────────────
; LCD Control Registers
; ───────────────────────────────────────────────────────────

DEF LCDC        EQU $FF40  ; LCD control
DEF STAT        EQU $FF41  ; LCD status
DEF SCY         EQU $FF42  ; Scroll Y
DEF SCX         EQU $FF43  ; Scroll X
DEF LY          EQU $FF44  ; LCD Y coordinate
DEF LYC         EQU $FF45  ; LY compare
DEF DMA         EQU $FF46  ; DMA transfer
DEF BGP         EQU $FF47  ; BG palette data
DEF OBP0        EQU $FF48  ; OBJ palette 0 data
DEF OBP1        EQU $FF49  ; OBJ palette 1 data
DEF WY          EQU $FF4A  ; Window Y position
DEF WX          EQU $FF4B  ; Window X position

; ───────────────────────────────────────────────────────────
; Interrupt Enable Register Bits
; ───────────────────────────────────────────────────────────

DEF IE_VBLANK   EQU $01    ; V-Blank interrupt enable
DEF IE_LCD      EQU $02    ; LCD STAT interrupt enable
DEF IE_TIMER    EQU $04    ; Timer interrupt enable
DEF IE_SERIAL   EQU $08    ; Serial interrupt enable
DEF IE_JOYPAD   EQU $10    ; Joypad interrupt enable

; ───────────────────────────────────────────────────────────
; Cartridge Header (at $0100)
; ───────────────────────────────────────────────────────────

DEF ROM_HEADER_START    EQU $0100
DEF ROM_HEADER_ENTRY    EQU $0100  ; Entry point (NOP jump)
DEF ROM_HEADER_LOGO     EQU $0104  ; Nintendo logo (48 bytes)
DEF ROM_HEADER_TITLE    EQU $0134  ; Game title (16 bytes)
DEF ROM_HEADER_CGB_FLAG EQU $0143  ; CGB compatibility
DEF ROM_HEADER_SGB_FLAG EQU $0146  ; SGB compatibility
DEF ROM_HEADER_TYPE     EQU $0147  ; Cartridge type
DEF ROM_HEADER_ROM_SIZE EQU $0148  ; ROM size
DEF ROM_HEADER_RAM_SIZE EQU $0149  ; RAM size
DEF ROM_HEADER_CHECKSUM EQU $014D  ; Header checksum

; ───────────────────────────────────────────────────────────
; Cartridge Types
; ───────────────────────────────────────────────────────────

DEF CART_ROM_ONLY       EQU $00  ; ROM only
DEF CART_MBC1           EQU $01  ; MBC1
DEF CART_MBC1_RAM       EQU $02  ; MBC1 + RAM
DEF CART_MBC1_RAM_BAT   EQU $03  ; MBC1 + RAM + Battery
DEF CART_MBC2           EQU $05  ; MBC2
DEF CART_MBC2_BAT       EQU $06  ; MBC2 + Battery
DEF CART_MBC3           EQU $11  ; MBC3
DEF CART_MBC3_RAM       EQU $12  ; MBC3 + RAM
DEF CART_MBC3_RAM_BAT   EQU $13  ; MBC3 + RAM + Battery

; ───────────────────────────────────────────────────────────
; Serial Protocol Constants
; ───────────────────────────────────────────────────────────

DEF MSG_CHALLENGE   EQU $01  ; Challenge from Pico
DEF MSG_ATTEST      EQU $02  ; Attestation response
DEF MSG_ACK         EQU $03  ; Acknowledgment
DEF MSG_ERROR       EQU $FF  ; Error message

DEF MSG_MAX_LEN     EQU 64   ; Maximum message length
DEF NONCE_SIZE      EQU 32   ; Nonce size (bytes)
DEF HASH_SIZE       EQU 32   ; SHA-256 hash size (bytes)

; ───────────────────────────────────────────────────────────
; SHA-256 Constants
; ───────────────────────────────────────────────────────────

DEF SHA256_BLOCK_SIZE   EQU 64   ; Block size in bytes
DEF SHA256_HASH_SIZE    EQU 32   ; Hash size in bytes
DEF SHA256_ROUNDS       EQU 64   ; Number of rounds

; ───────────────────────────────────────────────────────────
; Work RAM Layout (C000-CFFF)
; ───────────────────────────────────────────────────────────

DEF WRAM_STACK_BASE     EQU $C000  ; Stack grows down from here
DEF WRAM_SERIAL_BUF     EQU $C100  ; Serial buffer (64 bytes)
DEF WRAM_HASH_STATE     EQU $C200  ; SHA-256 state (32 bytes)
DEF WRAM_HASH_WORK      EQU $C300  ; SHA-256 working space (256 bytes)
DEF WRAM_NONCE          EQU $C500  ; Current nonce (32 bytes)
DEF WRAM_WALLET_ID      EQU $C600  ; Wallet ID storage (32 bytes)
DEF WRAM_FLAGS          EQU $C700  ; Status flags

; ───────────────────────────────────────────────────────────
; Status Flags
; ───────────────────────────────────────────────────────────

DEF FLAG_SERIAL_READY   EQU 0    ; Serial port ready
DEF FLAG_HASH_COMPLETE  EQU 1    ; Hash computation complete
DEF FLAG_ATTEST_SENT    EQU 2    ; Attestation sent
DEF FLAG_ERROR          EQU 7    ; Error occurred

; ───────────────────────────────────────────────────────────
; Error Codes
; ───────────────────────────────────────────────────────────

DEF ERR_NONE            EQU $00  ; No error
DEF ERR_SERIAL_TIMEOUT  EQU $01  ; Serial timeout
DEF ERR_INVALID_MSG     EQU $02  ; Invalid message format
DEF ERR_HASH_FAILED     EQU $03  ; Hash computation failed
DEF ERR_SRAM_FAILED     EQU $04  ; SRAM read/write failed
