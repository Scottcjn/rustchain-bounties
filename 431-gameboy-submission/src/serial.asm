; ═══════════════════════════════════════════════════════════
; Serial Communication Driver
; ═══════════════════════════════════════════════════════════
; 
; Handles communication with Raspberry Pi Pico bridge
; via Game Boy link cable (8 Kbit/s)
;
; Protocol:
;   - CHALLENGE ($01): Pico → Game Boy (32-byte nonce)
;   - ATTEST ($02):    Game Boy → Pico (32-byte hash)
;   - ACK ($03):       Pico → Game Boy (acknowledgment)
;   - ERROR ($FF):     Error message
; ═══════════════════════════════════════════════════════════

INCLUDE "include/gb.inc"

; ───────────────────────────────────────────────────────────
; Serial Initialization
; ───────────────────────────────────────────────────────────

SECTION "Serial Driver", ROM0[$0400]

Serial_Init:
    push bc
    push af
    
    ; Set serial control: external clock (slave mode)
    ; Game Boy is slave, Pico is master
    ld a, SC_CLOCK        ; External clock, no transfer
    ld [SC], a
    
    ; Clear serial buffer
    xor a
    ld [SB], a
    
    ; Clear interrupt flag
    ld [IF], a
    
    ; Reset state
    ld a, 0
    ld [wSerialState], a
    ld [wSerialIndex], a
    
    pop af
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Poll Serial Port
; ───────────────────────────────────────────────────────────
; Check if data is available and process it

Serial_Poll:
    push bc
    push de
    push hl
    push af
    
    ; Check serial transfer status
    ld a, [SC]
    and SC_TRANSFER
    jr nz, .transfer_active
    
    ; No transfer active, check if we should receive
    ; In slave mode, we wait for master to initiate
    
    ; For now, just return
    jr .done
    
.transfer_active
    ; Transfer in progress, wait for completion
    ; (interrupt will handle completion)
    
.done
    pop af
    pop hl
    pop de
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Send Byte
; ───────────────────────────────────────────────────────────
; Input: A = byte to send
; Output: A = received byte (or 0 on timeout)

Serial_SendByte:
    push bc
    push hl
    
    ; Load byte into SB
    ld [SB], a
    
    ; Start transfer (external clock - slave mode)
    ; Master (Pico) will provide clock
    ld a, SC_TRANSFER     ; Bit 7 = 1, enable transfer
    ld [SC], a
    
    ; Wait for transfer complete (with timeout)
    ld bc, $FFFF          ; Timeout counter
.wait_transfer
    ld a, [SC]
    and SC_TRANSFER
    jr z, .transfer_done  ; Transfer complete when bit 7 clears
    
    dec bc
    ld a, b
    or c
    jr nz, .wait_transfer
    
    ; Timeout - return 0
    xor a
    jr .return
    
.transfer_done
    ; Read received byte
    ld a, [SB]
    
.return
    pop hl
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Send Message
; ───────────────────────────────────────────────────────────
; Input: HL = message buffer, B = length
; Output: None

Serial_SendMessage:
    push af
    push bc
    push de
    push hl
    
.send_loop
    ld a, b
    and a
    jr z, .done
    
    ld a, [hl+]
    call Serial_SendByte
    
    ; Small delay between bytes
    call .delay_byte
    
    dec b
    jr .send_loop
    
.done
    pop hl
    pop de
    pop bc
    pop af
    ret

.delay_byte
    ; ~1ms delay
    push bc
    ld bc, $300
.delay_loop
    dec bc
    ld a, b
    or c
    jr nz, .delay_loop
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Send Attestation Response
; ───────────────────────────────────────────────────────────
; Format: [MSG_ATTEST][32-byte hash]

Serial_SendAttest:
    push bc
    push de
    push hl
    
    ; Build message: ATTEST + hash
    ld hl, wAttestBuffer
    ld [hl], MSG_ATTEST   ; Message type
    inc hl
    
    ; Copy hash from WRAM_HASH_STATE
    ld de, WRAM_HASH_STATE
    ld bc, 32
.copy_hash
    ld a, [de+]
    ld [hl+], a
    dec bc
    ld a, b
    or c
    jr nz, .copy_hash
    
    ; Send message (33 bytes total)
    ld hl, wAttestBuffer
    ld b, 33
    call Serial_SendMessage
    
    pop hl
    pop de
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Receive Challenge
; ───────────────────────────────────────────────────────────
; Format: [MSG_CHALLENGE][32-byte nonce]
; Stores nonce in WRAM_NONCE

Serial_ReceiveChallenge:
    push bc
    push de
    push hl
    push af
    
    ; Wait for message type
    call Serial_WaitByte
    cp MSG_CHALLENGE
    jr nz, .error
    
    ; Read 32-byte nonce
    ld de, WRAM_NONCE
    ld bc, 32
.read_nonce
    call Serial_WaitByte
    ld [de+], a
    dec bc
    ld a, b
    or c
    jr nz, .read_nonce
    
    ; Set challenge ready flag
    ld a, 1
    ld [wSerialChallengeReady], a
    
    xor a
    pop af
    pop hl
    pop de
    pop bc
    ret
    
.error
    ld a, ERR_INVALID_MSG
    ld [wSerialError], a
    pop af
    pop hl
    pop de
    pop bc
    ret

; ───────────────────────────────────────────────────────────
; Wait for Byte with Timeout
; ───────────────────────────────────────────────────────────
; Output: A = received byte, Z flag = success

Serial_WaitByte:
    push bc
    
    ld bc, $FFFF          ; Timeout counter
.wait_loop
    ld a, [SC]
    and SC_TRANSFER
    jr z, .check_data     ; Transfer complete
    
    dec bc
    ld a, b
    or c
    jr nz, .wait_loop
    
    ; Timeout
    xor a
    ld [wSerialError], a
    pop bc
    or $FF                ; Set Z flag to indicate error
    ret
    
.check_data
    ld a, [SB]
    pop bc
    and a                 ; Clear Z flag to indicate success
    ret

; ───────────────────────────────────────────────────────────
; Serial State Variables
; ───────────────────────────────────────────────────────────

SECTION "Serial Variables", WRAM0[$C900]

wSerialState:     DS 1    ; Current state (0=idle, 1=receiving, 2=sending)
wSerialIndex:     DS 1    ; Current byte index
wAttestBuffer:    DS 33   ; Attestation message buffer

; ───────────────────────────────────────────────────────────
; Serial Interrupt Handler (in HRAM for speed)
; ───────────────────────────────────────────────────────────

SECTION "Serial ISR", HRAM[$FF80]

Serial_ISR:
    push af
    push bc
    push hl
    
    ; Read received byte
    ld a, [SB]
    
    ; State machine
    ld a, [wSerialState]
    
.state_idle
    cp 0
    jr nz, .state_receiving
    
    ; Check if this is start of message
    ld a, [SB]
    cp MSG_CHALLENGE
    jr z, .start_challenge
    cp MSG_ACK
    jr z, .start_ack
    jr .ignore
    
.start_challenge
    ld a, 1             ; State: receiving challenge
    ld [wSerialState], a
    xor a
    ld [wSerialIndex], a
    jr .done
    
.start_ack
    ld a, 2             ; State: receiving ACK
    ld [wSerialState], a
    xor a
    ld [wSerialIndex], a
    jr .done
    
.state_receiving
    cp 1
    jr nz, .state_ack
    
    ; Receiving challenge
    ld hl, wSerialIndex
    ld a, [hl]
    cp 32               ; 32 bytes of nonce
    jr nc, .challenge_complete
    
    ; Store byte
    ld hl, WRAM_NONCE
    ld e, a
    ld d, 0
    add hl, de
    ld a, [SB]
    ld [hl], a
    
    ; Increment index
    inc [wSerialIndex]
    jr .done
    
.challenge_complete
    ; Challenge complete, set flag
    ld a, 1
    ld [wSerialChallengeReady], a
    
    ; Reset state
    xor a
    ld [wSerialState], a
    jr .done
    
.state_ack
    ; Receiving ACK - just reset state
    xor a
    ld [wSerialState], a
    jr .done
    
.ignore
    ; Unknown message, ignore
    
.done
    ; Clear interrupt flag
    ld a, IF_SERIAL
    ld [IF], a
    
    pop hl
    pop bc
    pop af
    reti
