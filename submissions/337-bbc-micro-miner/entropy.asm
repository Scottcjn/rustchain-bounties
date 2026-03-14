; ============================================================================
; RustChain BBC Micro Miner - Hardware Entropy Collection
; Target: BBC Micro Model B (1981) - MOS 6502 @ 2MHz
; Purpose: Gather true randomness from hardware sources
; ============================================================================

; Zero Page Variables (from miner.asm)
ZEROPG_START    = $50
entropy_ptr     = ZEROPG_START    ; $50-$51: Entropy buffer pointer
random_seed     = $56             ; Random seed
timer_lo        = $54             ; Timer low byte
timer_hi        = $55             ; Timer high byte

; I/O Memory Mapped (SHEILA)
VIA_T1CL        = $FE04           ; Timer 1 Low
VIA_T1CH        = $FE05           ; Timer 1 High
VIA_IFR         = $FE0D           ; Interrupt Flag Register
KEYBOARD        = $FE00           ; Keyboard input
VIA_T2CL        = $FE08           ; Timer 2 Low
VIA_T2CH        = $FE09           ; Timer 2 High

; Entropy Buffer
ENTROPY_BUFFER  = $3000           ; 32-byte entropy storage
ENTROPY_SIZE    = 32

        .org $2100                ; Entropy module start

; ============================================================================
; INIT_ENTROPY - Initialize entropy collection system
; ============================================================================

INIT_ENTROPY:
        ; Clear entropy buffer
        LDA #$00
        LDX #$00
CLEAR_ENTROPY:
        STA ENTROPY_BUFFER,X
        INX
        CPX #ENTROPY_SIZE
        BNE CLEAR_ENTROPY
        
        ; Initialize random seed from hardware
        JSR READ_HARDWARE_SEED
        STA random_seed
        
        ; Initialize timer
        LDA #$00
        STA timer_lo
        STA timer_hi
        
        RTS

; ============================================================================
; READ_HARDWARE_SEED - Get initial seed from hardware
; ============================================================================

READ_HARDWARE_SEED:
        ; Source 1: Read interrupt flags (some randomness)
        LDA VIA_IFR
        AND #$7F                    ; Clear bit 7 (interrupt flag)
        
        ; Source 2: Read timer low byte
        EOR VIA_T1CL
        
        ; Source 3: Read timer high byte
        EOR VIA_T1CH
        
        ; Source 4: Read keyboard register (even if no key)
        EOR KEYBOARD
        
        ; Mix bits
        ROL A
        ROL A
        EOR #$5A                    ; Additional mixing
        
        RTS

; ============================================================================
; COLLECT_ENTROPY - Gather entropy from multiple sources
; Called periodically during mining loop
; ============================================================================

COLLECT_ENTROPY:
        PHA
        PHX
        PHY
        
        ; Get current entropy buffer position
        LDY entropy_ptr
        LDY entropy_ptr+1
        
        ; Source 1: VSYNC Timer Jitter
        ; The 50Hz vertical blank interrupt creates timing variations
        JSR COLLECT_VSYNC_ENTROPY
        
        ; Source 2: Keyboard Timing (if user interactive)
        JSR COLLECT_KEYBOARD_ENTROPY
        
        ; Source 3: DRAM Refresh Timing
        JSR COLLECT_DRAM_ENTROPY
        
        ; Source 4: CPU Flag Variations
        JSR COLLECT_CPU_ENTROPY
        
        ; Update buffer pointer
        INC entropy_ptr
        LDA entropy_ptr
        CMP #ENTROPY_SIZE
        BCC ENTROPY_DONE
        LDA #$00
        STA entropy_ptr
        
ENTROPY_DONE:
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; COLLECT_VSYNC_ENTROPY - Collect entropy from VSYNC timer
; ============================================================================

COLLECT_VSYNC_ENTROPY:
        ; Wait for VSYNC (vertical blank)
        ; Bit 7 of IFR is VSYNC flag
WAIT_VSYNC:
        BIT VIA_IFR
        BPL WAIT_VSYNC              ; Wait for VSYNC
        
        ; Read timer at exact VSYNC moment (jitter!)
        LDA VIA_T1CL
        EOR random_seed
        STA random_seed
        
        ; Rotate for mixing
        ROL random_seed
        
        RTS

; ============================================================================
; COLLECT_KEYBOARD_ENTROPY - Collect entropy from keyboard timing
; Human key presses are unpredictable
; ============================================================================

COLLECT_KEYBOARD_ENTROPY:
        ; Read keyboard
        LDA KEYBOARD
        AND #$7F                    ; Clear top bit
        BEQ NO_KEY                  ; No key pressed
        
        ; Key pressed - mix into entropy
        EOR random_seed
        EOR timer_lo
        STA random_seed
        
        ; Rotate multiple times for mixing
        ROL random_seed
        ROL random_seed
        
NO_KEY:
        RTS

; ============================================================================
; COLLECT_DRAM_ENTROPY - Collect entropy from DRAM refresh
; Memory timing has small variations
; ============================================================================

COLLECT_DRAM_ENTROPY:
        ; Access memory in a pattern that creates timing variations
        LDX #$00
DRAM_LOOP:
        LDA ENTROPY_BUFFER,X
        EOR #$FF
        STA ENTROPY_BUFFER,X
        INX
        CPX #$08
        BNE DRAM_LOOP
        
        ; Read timer after memory access
        LDA VIA_T2CL
        EOR random_seed
        STA random_seed
        
        RTS

; ============================================================================
; COLLECT_CPU_ENTROPY - Collect entropy from CPU state
; Processor flags vary slightly
; ============================================================================

COLLECT_CPU_ENTROPY:
        ; Use processor flags as entropy source
        PHP                         ; Push processor flags
        PLA                         ; Pull into accumulator
        EOR random_seed
        STA random_seed
        
        ; Additional mixing using arithmetic
        CLC
        LDA random_seed
        ADC timer_lo
        STA random_seed
        
        RTS

; ============================================================================
; GET_ENTROPY_BYTE - Get single entropy byte
; Returns: A = entropy byte
; ============================================================================

GET_ENTROPY_BYTE:
        PHX
        PHY
        
        ; Collect fresh entropy
        JSR COLLECT_ENTROPY
        
        ; Get byte from buffer
        LDY entropy_ptr
        LDA ENTROPY_BUFFER,Y
        
        ; Mix with current seed
        EOR random_seed
        
        PLY
        PLX
        RTS

; ============================================================================
; FILL_ENTROPY_BUFFER - Fill entire entropy buffer
; Called during wallet generation
; ============================================================================

FILL_ENTROPY_BUFFER:
        PHA
        PHX
        PHY
        
        ; Fill buffer with fresh entropy
        LDX #$00
FILL_LOOP:
        JSR COLLECT_ENTROPY
        
        ; Get entropy byte
        LDA random_seed
        EOR timer_lo
        EOR timer_hi
        STA ENTROPY_BUFFER,X
        
        ; Small delay for entropy variation
        JSR SMALL_DELAY
        
        INX
        CPX #ENTROPY_SIZE
        BNE FILL_LOOP
        
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; SMALL_DELAY - Create small timing variation
; ============================================================================

SMALL_DELAY:
        ; Variable delay based on timer
        LDA VIA_T1CL
        AND #$0F                    ; 0-15 iterations
        TAX
DELAY_LOOP:
        DEX
        BNE DELAY_LOOP
        RTS

; ============================================================================
; MIX_ENTROPY - Mix entropy buffer (whitening)
; Improves randomness quality
; ============================================================================

MIX_ENTROPY:
        PHA
        PHX
        PHY
        
        ; XOR adjacent bytes
        LDX #$00
MIX_LOOP:
        LDA ENTROPY_BUFFER,X
        EOR ENTROPY_BUFFER+1,X
        STA ENTROPY_BUFFER,X
        INX
        CPX #ENTROPY_SIZE-1
        BNE MIX_LOOP
        
        ; Rotate entire buffer
        LDX #$00
        LDA #$00
        STA entropy_ptr             ; Reset pointer
        
        PLY
        PLX
        PLA
        RTS

; ============================================================================
; VERIFY_ENTROPY - Check entropy quality
; Returns: Z=0 if good entropy, Z=1 if poor
; ============================================================================

VERIFY_ENTROPY:
        PHA
        PHX
        
        ; Count unique values in buffer
        LDX #$00
        STX entropy_ptr             ; Use as counter
        
COUNT_UNIQUE:
        LDA ENTROPY_BUFFER,X
        ; Simplified: just check for all-zeros or all-ones
        INX
        CPX #ENTROPY_SIZE
        BNE COUNT_UNIQUE
        
        ; Check if buffer is all zeros (bad entropy)
        LDX #$00
        LDA #$00
CHECK_ZERO:
        CMP ENTROPY_BUFFER,X
        BNE ENTROPY_GOOD
        INX
        CPX #ENTROPY_SIZE
        BNE CHECK_ZERO
        
        ; All zeros - bad entropy
        SEC
        LDA #$00
        JMP VERIFY_DONE
        
ENTROPY_GOOD:
        CLC
        LDA #$01
        
VERIFY_DONE:
        PLX
        PLA
        RTS

; ============================================================================
; End of Entropy Module
; ============================================================================
