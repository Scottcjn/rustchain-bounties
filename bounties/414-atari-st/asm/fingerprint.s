; asm/fingerprint.s - Hardware Fingerprint Assembly
;
; Measures Motorola 68000 instruction timing jitter
; for unique hardware identification
;
; RustChain Miner for Atari ST
; Bounty #414
;

    .section .text
    .globl _asm_measure_jitter

; MFP Timer A register (68901 chip)
MFP_TIMER_A = 0x00FFFA01

;
; Measure CPU jitter
; Returns: D0 = jitter measurement
;
_asm_measure_jitter:
    ; Save registers
    MOVEM.L D1-D2, -(SP)
    
    ; Read MFP Timer A (lower 4 bits)
    MOVE.B  MFP_TIMER_A, D0
    ANDI    #$0F, D0
    MOVE.L  D0, D1          ; Save initial value
    
    ; Execute timing-sensitive instruction
    ; MULU takes 70 cycles but varies slightly
    ; based on CPU characteristics
    MOVE.L  D0, D2
    MULU    #123, D2        ; 70 cycles
    
    ; Read timer again
    MOVE.B  MFP_TIMER_A, D0
    ANDI    #$0F, D0
    
    ; Calculate difference (jitter)
    SUB.L   D1, D0
    BPL.S   .positive
    NEG.L   D0              ; Absolute value
    
.positive:
    ; Store result in D0
    ; Result is 0-15 (4-bit variance)
    
    ; Restore registers
    MOVEM.L (SP)+, D1-D2
    
    RTS

;
; Read MFP timer (C-callable)
; Returns: D0 = timer value (0-15)
;
    .globl _fingerprint_read_timer
    
_fingerprint_read_timer:
    MOVE.B  MFP_TIMER_A, D0
    ANDI    #$0F, D0
    RTS

    .end
