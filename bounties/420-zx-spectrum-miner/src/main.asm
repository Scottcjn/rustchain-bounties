; ZX Spectrum RustChain Miner - Main Entry Point
; Copyright 2026 - MIT License

    OUTPUT miner.tap
    ORG $8000           ; Load address for 48K Spectrum

; ============================================================================
; Constants
; ============================================================================

; ZX Spectrum ULA port
ULA_PORT        EQU $FE

; Serial port constants
BAUD_RATE       EQU 9600
BAUD_DELAY      EQU 369   ; T-states per bit at 3.5469 MHz

; Attestation states
STATE_IDLE      EQU 0
STATE_CHALLENGE EQU 1
STATE_COMPUTE   EQU 2
STATE_SEND      EQU 3
STATE_WAIT      EQU 4

; ============================================================================
; Variables (stored in RAM)
; ============================================================================

    ORG $C000           ; Variable storage area

attestation_state:  DEFS 1
status_string:      DEFS 32
tx_data:            DEFS 1
rx_data:            DEFS 1
rom_checksum_lo:    DEFS 1
rom_checksum_hi:    DEFS 1
timing1_lo:         DEFS 1
timing1_hi:         DEFS 1
timing2_lo:         DEFS 1
timing2_hi:         DEFS 1
timing_variance:    DEFS 1
json_buffer:        DEFS 256
wallet_address:     DEFS 32

; ============================================================================
; Entry Point
; ============================================================================

start:
    ; Initialize
    CALL ui_init
    CALL build_fingerprint
    
    ; Show startup screen
    LD HL, welcome_msg
    CALL print_string
    
    ; Wait for keypress to start
    CALL wait_key
    
    ; Start attestation loop
    LD A, STATE_IDLE
    LD (attestation_state), A
    
main_loop:
    ; Handle current state
    LD A, (attestation_state)
    
    CP STATE_IDLE
    JR Z, state_idle
    
    CP STATE_CHALLENGE
    JR Z, state_challenge
    
    CP STATE_COMPUTE
    JR Z, state_compute
    
    CP STATE_SEND
    JR Z, state_send
    
    CP STATE_WAIT
    JR Z, state_wait
    
    ; Unknown state, reset
    LD A, STATE_IDLE
    LD (attestation_state), A
    JR main_loop

; ============================================================================
; State Machine Handlers
; ============================================================================

state_idle:
    ; Display "Waiting for challenge..."
    LD HL, waiting_msg
    LD (status_string), HL
    CALL ui_show_status
    
    ; Wait for serial data
    CALL serial_rx
    LD (rx_data), A
    
    ; Check for CHALLENGE message
    ; Simplified: assume direct nonce
    LD A, STATE_CHALLENGE
    LD (attestation_state), A
    JR main_loop

state_challenge:
    ; Display "Computing SHA-256..."
    LD HL, computing_msg
    LD (status_string), HL
    CALL ui_show_status
    
    ; Compute SHA-256(nonce || wallet)
    ; This is the performance-critical section
    CALL sha256_compute
    
    LD A, STATE_SEND
    LD (attestation_state), A
    JR main_loop

state_send:
    ; Display "Sending attestation..."
    LD HL, sending_msg
    LD (status_string), HL
    CALL ui_show_status
    
    ; Build and send JSON
    CALL build_attestation_json
    CALL serial_tx_string
    
    ; Wait for ACK
    CALL serial_rx
    ; Parse ACK response (simplified)
    
    LD A, STATE_WAIT
    LD (attestation_state), A
    JR main_loop

state_wait:
    ; Display countdown timer
    CALL ui_show_countdown
    
    ; Check if epoch complete (10 minutes)
    ; Simplified: wait for next challenge
    CALL check_epoch_complete
    JR Z, state_idle
    
    JR main_loop

; ============================================================================
; Hardware Fingerprinting
; ============================================================================

build_fingerprint:
    ; Calculate ROM checksum
    CALL rom_checksum
    
    ; Measure ULA timing variance
    CALL ula_timing_fingerprint
    
    ; Store wallet address
    LD HL, wallet_address
    LD DE, default_wallet
    CALL copy_string
    
    RET

rom_checksum:
    ; Calculate checksum of ROM (0x0000-0xBFFF for 48K)
    LD HL, $0000
    LD DE, $C000
    LD BC, $0000
    
.calc_loop
    LD A, (HL)
    ADD C
    LD C, A
    JR NC, .no_carry
    INC B
.no_carry
    INC HL
    
    LD A, H
    CP D
    JR NZ, .calc_loop
    LD A, L
    CP E
    JR NZ, .calc_loop
    
    LD (rom_checksum_lo), C
    LD (rom_checksum_hi), B
    RET

ula_timing_fingerprint:
    ; Measure timing variance (simplified)
    DI
    
    LD BC, 1000
.measure1
    DEC BC
    LD A, B
    OR C
    JR NZ, .measure1
    LD (timing1_lo), L
    LD (timing1_hi), H
    
    ; Small delay
    LD BC, 100
.delay
    DEC BC
    LD A, B
    OR C
    JR NZ, .delay
    
    ; Measure again
    LD BC, 1000
.measure2
    DEC BC
    LD A, B
    OR C
    JR NZ, .measure2
    
    ; Calculate variance
    LD (timing_variance), A
    
    EI
    RET

; ============================================================================
; Serial Communication (Bit-banged via ULA port)
; ============================================================================

serial_tx:
    ; Transmit byte in A
    LD (tx_data), A
    LD B, 8
    
    ; Start bit (low)
    LD A, 0
    OUT (ULA_PORT), A
    CALL delay_baud
    
    ; Data bits
.tx_loop
    LD A, (tx_data)
    RRA
    LD (tx_data), A
    JR C, .tx_one
    
    LD A, 0
    OUT (ULA_PORT), A
    JR .tx_delay
    
.tx_one
    LD A, 1
    OUT (ULA_PORT), A
    
.tx_delay
    CALL delay_baud
    DJNZ .tx_loop
    
    ; Stop bit (high)
    LD A, 1
    OUT (ULA_PORT), A
    CALL delay_baud
    
    RET

serial_rx:
    ; Receive byte into A
    ; Wait for start bit
.wait_start
    IN A, (ULA_PORT)
    AND $08           ; EAR bit
    JR NZ, .wait_start
    
    ; Wait half baud (sample in middle)
    CALL delay_half_baud
    
    ; Sample 8 bits
    LD B, 8
    LD C, 0
    
.rx_loop
    CALL delay_baud
    IN A, (ULA_PORT)
    AND $08
    RR C
    DJNZ .rx_loop
    
    ; Wait for stop bit
    CALL delay_baud
    
    LD A, C
    LD (rx_data), A
    RET

delay_baud:
    ; Delay for one bit period (~369 T-states)
    PUSH BC
    LD BC, BAUD_DELAY
.delay_loop
    DEC BC
    LD A, B
    OR C
    JR NZ, .delay_loop
    POP BC
    RET

delay_half_baud:
    ; Delay for half bit period (~184 T-states)
    PUSH BC
    LD BC, BAUD_DELAY / 2
.delay_half_loop
    DEC BC
    LD A, B
    OR C
    JR NZ, .delay_half_loop
    POP BC
    RET

; ============================================================================
; SHA-256 (Stub - Full implementation is ~2-3 KB)
; ============================================================================

sha256_compute:
    ; Placeholder for SHA-256 implementation
    ; Full version would:
    ; 1. Prepare message schedule
    ; 2. Initialize working variables
    ; 3. 64 rounds of mixing
    ; 4. Update hash state
    
    ; This takes ~5-10 seconds on real hardware
    
    ; For now, return dummy hash
    LD HL, dummy_hash
    RET

dummy_hash:
    DEFM "deadbeef0123456789abcdef0123456789abcdef0123456789abcdef01234567"

; ============================================================================
; JSON Builder
; ============================================================================

build_attestation_json:
    ; Build: {"device_arch":"zx_z80","wallet":"RTC..."}
    LD HL, json_buffer
    
    LD (HL), '{'
    INC HL
    
    LD DE, json_arch
    CALL copy_string_hl
    
    LD DE, json_wallet
    CALL copy_string_hl
    
    ; Add wallet address
    LD DE, wallet_address
    CALL copy_string_hl
    
    LD (HL), '}'
    INC HL
    LD (HL), 0
    
    RET

json_arch:    DEFM '"device_arch":"zx_z80",'
json_wallet:  DEFM '"wallet":"'

; ============================================================================
; User Interface
; ============================================================================

ui_init:
    ; Clear screen
    LD A, $0E       ; PRINT token
    RST $10
    LD A, $0C       ; CLS token
    RST $10
    RET

ui_show_status:
    ; Print status at row 5, column 2
    LD A, $10       ; PRINT AT token
    RST $10
    LD A, 5
    RST $10
    LD A, 2
    RST $10
    
    LD HL, (status_string)
    CALL print_string
    RET

ui_show_countdown:
    ; Display epoch countdown (simplified)
    LD A, $10
    RST $10
    LD A, 6
    RST $10
    LD A, 2
    RST $10
    
    LD HL, countdown_msg
    CALL print_string
    RET

print_string:
    LD A, (HL)
    OR A
    RET Z
    RST $10         ; PRINT char
    INC HL
    JR print_string

copy_string:
    ; Copy string from DE to HL
    LD A, (DE)
    LD (HL), A
    OR A
    RET Z
    INC DE
    INC HL
    JR copy_string

copy_string_hl:
    ; Copy string from DE to HL, update HL
    LD A, (DE)
    LD (HL), A
    OR A
    RET Z
    INC DE
    INC HL
    JR copy_string_hl

wait_key:
    ; Wait for any keypress
    ; Simplified keyboard scan
.wait
    LD A, $FE
    OUT ($FE), A
    IN A, ($FE)
    ; Check for keypress (any bit low)
    CP $FF
    JR Z, .wait
    RET

check_epoch_complete:
    ; Check if 10-minute epoch is complete
    ; Simplified: always return not complete
    XOR A
    RET

; ============================================================================
; Strings
; ============================================================================

welcome_msg:
    DEFM 13, 13
    DEFM "  +----------------------------------+", 13
    DEFM "  |  RUSTCHAIN MINER v0.1 - ZX SPEC  |", 13
    DEFM "  +----------------------------------+", 13
    DEFM "  |  Z80 @ 3.5 MHz                   |", 13
    DEFM "  |  48 KB RAM                       |", 13
    DEFM "  |                                  |", 13
    DEFM "  |  Press any key to start...       |", 13
    DEFM "  +----------------------------------+", 13
    DEFM 13
    DEFM 0

waiting_msg:    DEFM "WAITING FOR CHALLENGE...", 0
computing_msg:  DEFM "COMPUTING SHA-256...", 0
sending_msg:    DEFM "SENDING ATTESTATION...", 0
countdown_msg:  DEFM "EPOCH: 09:59 REMAINING", 0

default_wallet:
    DEFM "RTC4325af95d26d59c3ef025963656d22af638bb96b"

; ============================================================================
; End
; ============================================================================

    END start
