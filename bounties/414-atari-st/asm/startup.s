; asm/startup.s - Atari ST 68000 Startup Code
;
; RustChain Miner for Atari ST
; Bounty #414
;
; This is the entry point for the TOS executable
;

    .section .text
    .globl _main
    .globl _Pterm0

; TOS base pointer (at address $000004)
TOS_BASE = 0x000004

; Entry point
_start:
    ; Save TOS base pointer on stack
    MOVE.L  TOS_BASE, A0
    MOVE.L  A0, -(SP)
    
    ; Initialize stack pointer
    LEA     _stack_top, A7
    
    ; Clear BSS section
    LEA     _bss_start, A0
    LEA     _bss_end, A1
    CMPA.L  A0, A1
    BEQ.S   .bss_done
    
.bss_clear:
    CLR.B   -(A1)
    CMPA.L  A0, A1
    BNE.S   .bss_clear
    
.bss_done:
    ; Call C main function
    JSR     _main
    
    ; Exit to TOS
    JSR     _Pterm0
    
    ; Should never reach here
    BRA.S   .

; TOS termination (trap #1, D0=0)
_Pterm0:
    MOVEQ   #0, D0
    TRAP    #1
    RTS

; Stack storage (16 KB)
    .section .bss
    .globl _stack_top
    .globl _stack_bottom
    .globl _bss_start
    .globl _bss_end

_bss_start:
    .space  1024          ; Reserve space for BSS
    
_bss_end:

_stack_bottom:
    .space  16384         ; 16 KB stack
    
_stack_top:

    .end
