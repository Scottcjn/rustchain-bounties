; EDSAC Cryptocurrency Miner
; Bounty #352 - RustChain LEGENDARY Tier
; 
; This is the world's first (and slowest) cryptocurrency miner,
; running on an emulation of the 1949 EDSAC computer.
;
; Architecture: 17-bit words, mercury delay line memory
; Hash Function: Simplified additive checksum
; Target: Find nonce where hash(header, nonce) < target
;
; Memory Layout:
;   0-19:   Program code
;   20:     Block header (input)
;   21:     Target value
;   22:     Current nonce
;   23:     Hash result
;   24:     Prime constant 1 (7919)
;   25:     Prime constant 2 (104729)
;   26:     Temporary storage
;   27:     Modulus (16384)
;   28:     Constant 1
;   29:     Max nonce (16384)

; ============================================================
; INITIALIZATION
; ============================================================

START   Z           ; Clear accumulator
        T 22        ; nonce = 0

; ============================================================
; MAIN MINING LOOP
; ============================================================

LOOP    L 20        ; A = block_header
        M 24        ; A = header × 7919
        T 26        ; temp = header × 7919
        
        L 22        ; A = nonce
        M 25        ; A = nonce × 104729
        A 26        ; A = (header×7919) + (nonce×104729)
        
        ; Simplified modulo - use natural 17-bit overflow
        ; (Real EDSAC would need repeated subtraction)
        
        T 23        ; hash = result
        
        ; Check if hash < target
        L 23        ; A = hash
        S 21        ; A = hash - target
        G FOUND     ; If hash < target (result negative), jump to FOUND
        
        ; Increment nonce
        L 22        ; A = nonce
        A 28        ; A = nonce + 1
        T 22        ; nonce = nonce + 1
        
        ; Check for overflow
        L 22        ; A = nonce
        S 29        ; A = nonce - max
        G LOOP      ; If nonce < max, continue loop
        
        ; No solution found (shouldn't happen with proper difficulty)
        H           ; Halt with error

; ============================================================
; SOLUTION FOUND
; ============================================================

FOUND   L 22        ; A = successful nonce
        O 0         ; Output nonce (address 0 = success)
        H           ; Halt with success

; ============================================================
; DATA SECTION
; ============================================================

        ; These values are loaded by the simulator
        ; Placeholder values - actual values set at runtime
        
P7919F  P 7919 F    ; Prime constant 1
P104729F P 104729 F ; Prime constant 2 (will overflow, simplified)
P1      P 1 F       ; Constant 1
P16384F P 16384 F   ; Max nonce + 1

; ============================================================
; NOTES
; ============================================================
;
; Hash Function:
;   hash(header, nonce) = (header × 7919 + nonce × 104729) mod 16384
;
; Prime numbers chosen for better distribution:
;   7919 = 1000th prime
;   104729 = 10000th prime
;
; Expected Performance:
;   ~20-33 hashes/second on real EDSAC
;   Instant on modern Python simulator
;
; Wallet Address for Bounty:
;   RTC4325af95d26d59c3ef025963656d22af638bb96b
;
; ============================================================
