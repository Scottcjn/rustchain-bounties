; HP 2116 Assembly - Miner Core
        ORG 400H
START   CLA
        JSB INIT
LOOP    JSB FINGERPRINT
        JSB SUBMIT
        JMP LOOP
INIT    STA INIT+1
INIT+1  JMP 0
FINGERPRINT
        ; RIP-PoA checks
        JMP 0
SUBMIT  ; Submit to node
        JMP 0
        END START
