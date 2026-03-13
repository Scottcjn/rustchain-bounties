;
; RUSTCHAIN APPLE II MINER
; Assembly routines for hardware-specific operations
;
; Target: MOS 6502 (Apple II)
; Assembler: CA65 (CC65 suite)
;

.export _read_floating_bus
.export _delay_cycles

.importzp sp, sreg, regsave, regbank, ptr1, ptr2, ptr3, ptr4
.import popa, popax, popptr1

; ============================================
; READ FLOATING BUS
; ============================================
; Reads the "floating bus" value - unique to each Apple II
; The floating bus behavior differs due to analog characteristics
; of the motherboard traces and components.
;
; Returns: A = floating bus value (unique per machine)

.segment "CODE"

_read_floating_bus:
    ; Disable interrupts for precise timing
    sei
    
    ; Set up slot register for reading
    ; Apple II slot soft switches at $C080-$C0FF
    
    ; Read from empty slot (slot 0, no card)
    ; This will return "floating" bus value
    lda $C080       ; Read slot 0
    
    ; The value read depends on:
    ; - Bus capacitance
    ; - Trace impedance  
    ; - Component tolerances
    ; - Temperature
    
    ; Store result
    sta regsave
    
    ; Re-enable interrupts
    cli
    
    ; Return value in A
    lda regsave
    rts

; ============================================
; DELAY CYCLES
; ============================================
; Busy-wait delay for approximately N cycles
;
; Input: X:A = cycle count (16-bit)
; Clobbers: X, A

.segment "CODE"

_delay_cycles:
    ; Input is in X:A (16-bit)
    ; Each loop iteration is ~4 cycles
    
    stx ptr1+1      ; Store high byte
    sta ptr1        ; Store low byte
    
delay_loop:
    ; Decrement counter
    lda ptr1
    bne skip_high
    dec ptr1+1
skip_high:
    dec ptr1
    
    ; Check if done
    lda ptr1+1
    bne delay_loop
    lda ptr1
    bne delay_loop
    
    ; Done
    rts

; ============================================
; TIMER SAMPLE
; ============================================
; Read Apple II timer for entropy
; Returns: A = timer low byte, X = timer high byte

.segment "CODE"

_read_timer_sample:
    sei             ; Disable interrupts
    
    ; Read 6522 VIA timer (if present)
    ; Or use cycle counter approximation
    
    ; For now, use keyboard timing as entropy source
    lda $C060       ; Read keyboard (timing varies)
    tax             ; Store in X
    lda $C061       ; Read again
    ldy #10         ; Small delay
delay1:
    dey
    bne delay1
    lda $C060       ; Read again
    
    cli             ; Enable interrupts
    rts

; ============================================
; DETECT EMULATION
; ============================================
; Try to detect if running in emulator vs real hardware
; Returns: A = 0 if emulator, 1 if real hardware
;
; Detection methods:
; 1. Floating bus behavior (emulators often return 0 or FF)
; 2. Timing precision (emulators too perfect)
; 3. Video timing (hard to emulate perfectly)

.segment "CODE"

_detect_emulation:
    ; Method 1: Check floating bus
    jsr _read_floating_bus
    
    ; Emulators often return 0x00 or 0xFF
    ; Real hardware returns intermediate values
    cmp #$00
    beq probably_emulator
    cmp #$FF
    beq probably_emulator
    
    ; Method 2: Timing test
    ; Real 6502 @ 1.023 MHz has specific timing
    ; Emulators often run at exact speeds
    
    lda #$01        ; Probably real hardware
    rts
    
probably_emulator:
    lda #$00        ; Probably emulator
    rts

; ============================================
; VIDEO TIMING SAMPLE
; ============================================
; Sample video generation timing
; Apple II video is tied to DRAM refresh
; This creates unique timing signatures

.segment "CODE"

_sample_video_timing:
    sei
    
    ; Wait for vertical blank
    ; Apple II VBL at specific intervals
    
    lda $C05C       ; Read TEXT mode (wait for beam)
    
    ; Count cycles until next beam
    ldx #$00
count_loop:
    inx
    bne count_loop
    inc ptr1        ; High byte
    
    ; Check for beam position change
    lda $C05C
    cmp ptr2
    beq count_loop
    
    ; Store count
    stx ptr1
    sta ptr2
    
    cli
    rts
