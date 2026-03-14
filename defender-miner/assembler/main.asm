; ============================================================================
; Defender 矿工 - Motorola 6809 汇编实现
; RustChain 移植到 1981 年街机硬件
; ============================================================================
; 
; 硬件：Motorola 6809 @ 1 MHz
; 内存：4 KB RAM, 48 KB ROM
; 功能：简化挖矿循环，利用硬件乘法器
;
; 汇编器：lwasm 或 as09
; 构建：lwasm -f bin -o miner.rom main.asm
; ============================================================================

            .org    $C000           ; RAM 起始地址

; ============================================================================
; 零页变量 (直接寻址，更快)
; ============================================================================
ZERO_PAGE   .equ    $0000           ; 直接页基址

nonce_lo    .equ    $00             ; Nonce 低字节
nonce_hi    .equ    $01             ; Nonce 高字节
hash_lo     .equ    $02             ; 哈希结果低字节
hash_hi     .equ    $03             ; 哈希结果高字节
block_hdr   .equ    $04             ; 区块头指针 (16 位)
diff_target .equ    $06             ; 难度目标 (16 位)
temp_a      .equ    $08             ; 临时变量 A
temp_b      .equ    $09             ; 临时变量 B
counter     .equ    $0A             ; 循环计数器

; ============================================================================
; I/O 端口 (Defender 硬件)
; ============================================================================
VIDEO_CTRL  .equ    $E000           ; 视频控制寄存器
SCORE_LO    .equ    $E002           ; 得分 (哈希率) 低字节
SCORE_HI    .equ    $E003           ; 得分 (哈希率) 高字节
BUTTONS     .equ    $E010           ; 按钮输入
LED_CONTROL .equ    $E020           ; LED 控制 (挖矿状态)

; ============================================================================
; 程序入口
; ============================================================================
            .org    $C100           ; 程序起始

start:
            LDS     #$CFFF          ; 初始化系统栈顶
            LDU     #$C800          ; 初始化用户栈
            
            ; 清零变量
            CLR     nonce_lo
            CLR     nonce_hi
            CLR     hash_lo
            CLR     hash_hi
            
            ; 设置难度目标 (简化：0x0100 = 256)
            LDD     #$0100
            STD     diff_target
            
            ; 初始化区块头指针
            LDX     #block_data
            STX     block_hdr
            
            JMP     mining_loop     ; 进入主挖矿循环

; ============================================================================
; 主挖矿循环
; ============================================================================
mining_loop:
            ; 递增 Nonce
            INC     nonce_lo
            BNE     check_overflow
            INC     nonce_hi
            
check_overflow:
            ; 检查是否溢出 (65535 次尝试)
            LDD     nonce_lo
            CMPD    #$FFFF
            BNE     compute_hash
            
            ; Nonce 溢出，重置并继续
            CLR     nonce_lo
            CLR     nonce_hi
            
compute_hash:
            ; 调用哈希计算函数
            JSR     compute_hash_6809
            
            ; 检查是否找到有效区块
            JSR     check_difficulty
            BCS     found_block     ; C=1 表示哈希 < 难度
            
            ; 更新得分显示 (哈希率计数)
            LDD     SCORE_LO
            ADDD    #1
            STD     SCORE_LO
            
            ; 继续循环
            BRA     mining_loop

; ============================================================================
; 找到有效区块!
; ============================================================================
found_block:
            ; 闪烁 LED 指示成功
            LDA     #$FF
            STA     LED_CONTROL
            
            ; 显示成功消息 (通过视频系统)
            LDX     #success_msg
            JSR     display_message
            
            ; 等待玩家确认 (按按钮)
wait_button:
            LDA     BUTTONS
            ANDA    #$01            ; 检查按钮 1
            BEQ     wait_button
            
            ; 清零 LED
            CLR     LED_CONTROL
            
            ; 重置 Nonce，继续挖矿
            CLR     nonce_lo
            CLR     nonce_hi
            BRA     mining_loop

; ============================================================================
; 6809 风格哈希计算
; 使用硬件乘法器加速
; ============================================================================
compute_hash_6809:
            ; 保存寄存器
            PSHS    A, B, D, X, Y
            
            ; 初始化哈希值
            LDD     #$1234
            STD     hash_lo
            
            ; 从区块头加载数据并混合
            LDX     block_hdr
            
            ; 轮次 1: 乘法混合
            LDA     ,X+             ; 加载字节 0
            LDB     ,X+             ; 加载字节 1
            MUL                     ; A×B→D (硬件乘法!)
            
            LDX     hash_lo
            EORA    hash_lo         ; XOR 到哈希
            EORB    hash_hi
            STD     hash_lo
            
            ; 轮次 2: 加入 Nonce
            LDA     nonce_lo
            LDB     nonce_hi
            MUL                     ; Nonce 乘法
            
            LDX     hash_lo
            EORA    hash_lo
            EORB    hash_hi
            STD     hash_lo
            
            ; 轮次 3: 常量混合
            LDA     #$56
            LDB     #$78
            MUL
            
            LDX     hash_lo
            EORA    hash_lo
            EORB    hash_hi
            STD     hash_lo
            
            ; 轮次 4: 最终混合
            LDA     hash_lo
            LDB     hash_hi
            MUL
            
            STD     hash_lo
            
            ; 恢复寄存器
            PULS    A, B, D, X, Y
            RTS

; ============================================================================
; 检查难度目标
; 返回：C=1 如果哈希 < 难度 (成功)
;       C=0 如果哈希 >= 难度 (失败)
; ============================================================================
check_difficulty:
            ; 比较哈希与难度
            LDD     hash_lo
            SUBD    diff_target
            
            ; 如果结果为负 (借位)，则哈希 < 难度
            ; 6809: SUBD 设置 C 标志如果结果<0
            RTS                     ; 返回，C 标志已设置

; ============================================================================
; 显示消息 (简化版)
; 输入：X = 消息指针
; ============================================================================
display_message:
            ; 保存到视频 RAM (简化实现)
            PSHS    A, B, X
            
            ; 实际实现会逐字符写入 VRAM
            ; 这里简化为设置标志
            
            PULS    A, B, X
            RTS

; ============================================================================
; 数据区
; ============================================================================
block_data:
            .byte   $01             ; 版本
            .byte   $DE             ; 前块哈希 (简化)
            .byte   $AD
            .byte   $BE
            .byte   $EF
            .byte   $CA             ; Merkle 根
            .byte   $FE
            .byte   $BA
            .byte   $BE
            .byte   $00             ; 时间戳 (简化)
            .byte   $00
            .byte   $00
            .byte   $00
            .byte   $1D             ; 难度位
            .byte   $00
            .byte   $FF
            .byte   $FF

success_msg:
            .ascii  "BLOCK FOUND!"
            .byte   $00             ; 字符串结束

; ============================================================================
; 中断向量表 (Defender 硬件要求)
; ============================================================================
            .org    $FFF6           ; 复位向量
            .word   start           ; 复位时跳转到 start

            .org    $FFF4           ; SWI2 向量
            .word   $0000

            .org    $FFF2           ; SWI 向量
            .word   $0000

            .org    $FFF0           ; FIRQ 向量
            .word   $0000

            .org    $FFFE           ; IRQ 向量
            .word   $0000

            .org    $FFFC           ; NMI 向量
            .word   $0000

; ============================================================================
; 文件结束
; ============================================================================
            .end
