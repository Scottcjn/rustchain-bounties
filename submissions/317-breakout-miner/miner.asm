; ============================================
; RustChain Breakout Miner
; Atari Breakout Arcade (1976)
; ============================================
; MOS Technology 6502 @ 1.5 MHz
; 8 KB RAM
; 
; 功能:
; - 熵收集 (VBLANK, 拨盘，球位置)
; - 钱包生成
; - LED 编码输出
; - 离线证明
; ============================================

        .ORG $0200          ; 程序起始地址

; ============================================
; 内存映射 (Breakout 街机)
; ============================================
VBLANK_COUNTER  = $C040     ; VBLANK 计数器 (16 位)
PADDLE_POS      = $C060     ; 玩家拨盘位置 (8 位)
GAME_STATE      = $C061     ; 游戏状态 (8 位)
BALL_X          = $C062     ; 球 X 位置 (8 位)
BALL_Y          = $C063     ; 球 Y 位置 (8 位)
LED_CONTROL     = $C200     ; LED 控制寄存器

; ============================================
; 零页变量 (快速访问)
; ============================================
ENTROPY_PTR     = $00       ; 熵缓冲指针 (8 位)
ENTROPY_COUNT   = $01       ; 收集的熵字节数
WALLET_TEMP     = $02       ; 钱包生成临时存储
CHECKSUM        = $03       ; 熵缓冲校验和
VBLANK_LAST     = $04       ; 上次 VBLANK 值
PADDLE_LAST     = $05       ; 上次拨盘位置
ATTEST_READY    = $06       ; 证明就绪标志

; ============================================
; 中断向量
; ============================================
        .ORG $FFFA
        .WORD VBLANK_NMI    ; NMI 向量 (VBLANK)
        .WORD RESET         ; RESET 向量
        .WORD IRQ_HANDLER   ; IRQ 向量

; ============================================
; 主程序入口
; ============================================
RESET:
        SEI                 ; 禁用中断
        CLD                 ; 禁用十进制模式
        LDX #$FF            ; 初始化栈指针
        TXS
        
        ; 初始化变量
        LDA #$00
        STA ENTROPY_PTR
        STA ENTROPY_COUNT
        STA WALLET_TEMP
        STA CHECKSUM
        STA VBLANK_LAST
        STA PADDLE_LAST
        STA ATTEST_READY
        
        CLI                 ; 启用中断
        
        ; 显示启动信息 (通过 LED)
        JSR BLINK_STARTUP
        
        ; 主循环
MAIN_LOOP:
        JSR COLLECT_ENTROPY
        JSR CHECK_ATTESTATION
        JMP MAIN_LOOP

; ============================================
; VBLANK 中断处理程序
; ============================================
VBLANK_NMI:
        PHA                 ; 保存累加器
        
        ; 读取 VBLANK 计数器
        LDA VBLANK_COUNTER
        STA VBLANK_LAST
        
        ; 增加熵指针
        INC ENTROPY_PTR
        
        PLA                 ; 恢复累加器
        RTI

; ============================================
; IRQ 处理程序
; ============================================
IRQ_HANDLER:
        RTI

; ============================================
; 熵收集例程
; ============================================
COLLECT_ENTROPY:
        PHA
        PHX
        
        ; 读取 VBLANK 计数器 (低字节)
        LDA VBLANK_COUNTER
        EOR VBLANK_LAST     ; 与上次值异或
        JSR MIX_ENTROPY
        
        ; 读取拨盘位置
        LDA PADDLE_POS
        EOR PADDLE_LAST
        JSR MIX_ENTROPY
        
        ; 读取球位置
        LDA BALL_X
        JSR MIX_ENTROPY
        
        LDA BALL_Y
        JSR MIX_ENTROPY
        
        ; 读取游戏状态
        LDA GAME_STATE
        JSR MIX_ENTROPY
        
        ; 更新上次值
        LDA VBLANK_COUNTER
        STA VBLANK_LAST
        LDA PADDLE_POS
        STA PADDLE_LAST
        
        PLX
        PLA
        RTS

; ============================================
; 混合熵到缓冲
; ============================================
MIX_ENTROPY:
        PHA
        PHX
        
        ; 获取当前熵指针
        LDX ENTROPY_PTR
        
        ; 与缓冲异或
        EOR ENTROPY_BUFFER, X
        
        ; 存储回缓冲
        STA ENTROPY_BUFFER, X
        
        ; 更新校验和
        CLC
        ADC CHECKSUM
        STA CHECKSUM
        
        ; 增加指针
        INC ENTROPY_PTR
        BNE SKIP_WRAP
        INC ENTROPY_COUNT
SKIP_WRAP:
        
        ; 检查是否收集了 256 字节
        LDA ENTROPY_COUNT
        CMP #$01
        BCC NO_ATTEST
        
        ; 设置证明就绪
        LDA #$01
        STA ATTEST_READY
        
        ; LED 闪烁提示
        JSR BLINK_READY
        
NO_ATTEST:
        PLX
        PLA
        RTS

; ============================================
; 检查证明
; ============================================
CHECK_ATTESTATION:
        LDA ATTEST_READY
        BEQ NO_ATTESTATION
        
        ; 生成钱包
        JSR GENERATE_WALLET
        
        ; 显示钱包 (通过 LED 编码)
        JSR DISPLAY_WALLET_LED
        
        ; 重置熵收集
        LDA #$00
        STA ENTROPY_PTR
        STA ENTROPY_COUNT
        STA ATTEST_READY
        STA CHECKSUM
        
NO_ATTESTATION:
        RTS

; ============================================
; 钱包生成 (简化版 SHA-256)
; ============================================
GENERATE_WALLET:
        PHA
        PHX
        PHY
        
        ; 使用熵缓冲生成哈希
        ; 简化：直接复制前 20 字节作为地址
        LDX #$00
WALLET_LOOP:
        LDA ENTROPY_BUFFER, X
        STA WALLET_ADDR, X
        INX
        CPX #$14            ; 20 字节地址
        BCC WALLET_LOOP
        
        ; 添加 "RTC" 前缀
        LDA #'R'
        STA WALLET_ADDR - 3
        LDA #'T'
        STA WALLET_ADDR - 2
        LDA #'C'
        STA WALLET_ADDR - 1
        
        PLY
        PLX
        PLA
        RTS

; ============================================
; LED 编码输出钱包
; ============================================
DISPLAY_WALLET_LED:
        ; 通过 LED 闪烁编码钱包地址
        ; 每个字节用 8 次闪烁表示 (Morse 码变体)
        PHA
        PHX
        
        LDX #$00
LED_WALLET_LOOP:
        LDA WALLET_ADDR, X
        JSR BLINK_BYTE
        INX
        CPX #$14
        BCC LED_WALLET_LOOP
        
        PLX
        PLA
        RTS

; ============================================
; LED 闪烁字节
; ============================================
BLINK_BYTE:
        PHA
        PHX
        
        TAX                 ; 字节值到 X
        LDX #$08            ; 8 位
BLINK_BIT_LOOP:
        ASL                 ; 左移，最高位到进位
        BCC BLINK_ZERO
        JSR BLINK_ONE
        JMP BLINK_NEXT
BLINK_ZERO:
        JSR BLINK_ZERO_LED
BLINK_NEXT:
        DEX
        BNE BLINK_BIT_LOOP
        
        ; 字节间暂停
        JSR DELAY_LONG
        
        PLX
        PLA
        RTS

; ============================================
; LED 闪烁例程
; ============================================
BLINK_STARTUP:
        ; 启动时闪烁 3 次
        LDX #$03
STARTUP_LOOP:
        JSR BLINK_ON
        JSR DELAY_SHORT
        JSR BLINK_OFF
        JSR DELAY_SHORT
        DEX
        BNE STARTUP_LOOP
        RTS

BLINK_READY:
        ; 证明就绪时快速闪烁 5 次
        LDX #$05
READY_LOOP:
        JSR BLINK_ON
        JSR DELAY_VERY_SHORT
        JSR BLINK_OFF
        JSR DELAY_VERY_SHORT
        DEX
        BNE READY_LOOP
        RTS

BLINK_ON:
        LDA #$01
        STA LED_CONTROL
        RTS

BLINK_OFF:
        LDA #$00
        STA LED_CONTROL
        RTS

BLINK_ONE:
        ; 长闪烁表示 1
        JSR BLINK_ON
        JSR DELAY_LONG
        JSR BLINK_OFF
        JSR DELAY_SHORT
        RTS

BLINK_ZERO_LED:
        ; 短闪烁表示 0
        JSR BLINK_ON
        JSR DELAY_SHORT
        JSR BLINK_OFF
        JSR DELAY_SHORT
        RTS

; ============================================
; 延时例程
; ============================================
DELAY_VERY_SHORT:
        LDX #$10
DELAY_VS_LOOP:
        DEX
        BNE DELAY_VS_LOOP
        RTS

DELAY_SHORT:
        LDX #$FF
DELAY_S_LOOP:
        DEX
        BNE DELAY_S_LOOP
        RTS

DELAY_LONG:
        LDX #$FF
DELAY_L_LOOP1:
        LDY #$FF
DELAY_L_LOOP2:
        DEY
        BNE DELAY_L_LOOP2
        DEX
        BNE DELAY_L_LOOP1
        RTS

; ============================================
; 数据段
; ============================================
        .ORG $0400
ENTROPY_BUFFER:
        .DS 256             ; 256 字节熵缓冲

        .ORG $0500
WALLET_ADDR:
        .DS 20              ; 20 字节钱包地址

        .ORG $0600
ATTESTATION_DATA:
        .DS 64              ; 证明数据缓冲

; ============================================
; 结束
; ============================================
        .END
