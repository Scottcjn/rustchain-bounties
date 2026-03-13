; SWAC SHA256 压缩函数 - 汇编实现
; 内存限制：256 字 × 37 位
; 目标：极简实现，外部预处理

; 内存布局
; 0-31:   程序代码
; 32-63:  SHA256 K 常量
; 64-71:  哈希状态 H0-H7
; 72-79:  工作变量 a-h
; 80-143: 消息调度 W[0..63]
; 144-191:临时计算区
; 192-223:栈/寄存器保存
; 224-255:I/O 缓冲区

        ORG 0

; ========== 主程序入口 ==========
START:
        ; 初始化工作变量 a-h = H0-H7
        LD      H0
        ST      A_REG
        LD      H1
        ST      B_REG
        LD      H2
        ST      C_REG
        LD      H3
        ST      D_REG
        LD      H4
        ST      E_REG
        LD      H5
        ST      F_REG
        LD      H6
        ST      G_REG
        LD      H7
        ST      H_REG
        
        ; 初始化轮数计数器
        LD      ZERO
        ST      ROUND_CNT
        
; ========== 64 轮压缩主循环 ==========
MAIN_LOOP:
        ; 检查轮数
        LD      ROUND_CNT
        SUB     CONST_64
        JZ      DONE            ; 如果 64 轮完成，跳转到完成
        
        ; 计算 T1 = h + Σ1(e) + Ch(e,f,g) + K[t] + W[t]
        ; Σ1(e) = ROTR(e,6) ⊕ ROTR(e,11) ⊕ ROTR(e,25)
        ; Ch(e,f,g) = (e ∧ f) ⊕ (¬e ∧ g)
        
        LD      H_REG           ; 加载 h
        ADD     SIGMA1_E        ; + Σ1(e)
        ADD     CH_EFG          ; + Ch(e,f,g)
        ADD     K_TABLE         ; + K[t] (当前轮)
        ADD     W_TABLE         ; + W[t] (当前轮)
        ST      T1              ; 存储 T1
        
        ; 计算 T2 = Σ0(a) + Maj(a,b,c)
        ; Σ0(a) = ROTR(a,2) ⊕ ROTR(a,13) ⊕ ROTR(a,22)
        ; Maj(a,b,c) = (a ∧ b) ⊕ (a ∧ c) ⊕ (b ∧ c)
        
        LD      SIGMA0_A
        ADD     Maj_ABC
        ST      T2              ; 存储 T2
        
        ; 更新工作变量
        ; h = g
        ; g = f
        ; f = e
        ; e = d + T1
        ; d = c
        ; c = b
        ; b = a
        ; a = T1 + T2
        
        LD      G_REG
        ST      H_REG
        LD      F_REG
        ST      G_REG
        LD      E_REG
        ST      F_REG
        LD      D_REG
        ADD     T1
        ST      E_REG
        LD      C_REG
        ST      D_REG
        LD      B_REG
        ST      C_REG
        LD      A_REG
        ST      B_REG
        LD      T1
        ADD     T2
        ST      A_REG
        
        ; 轮数 +1
        LD      ROUND_CNT
        ADD     ONE
        ST      ROUND_CNT
        
        ; 更新 W 表和 K 表指针
        ; (需要间接寻址，这里简化)
        
        JMP     MAIN_LOOP

; ========== 完成 - 更新哈希状态 ==========
DONE:
        ; H0 = H0 + a, H1 = H1 + b, ...
        LD      H0
        ADD     A_REG
        ST      H0
        LD      H1
        ADD     B_REG
        ST      H1
        LD      H2
        ADD     C_REG
        ST      H2
        LD      H3
        ADD     D_REG
        ST      H3
        LD      H4
        ADD     E_REG
        ST      H4
        LD      H5
        ADD     F_REG
        ST      H5
        LD      H6
        ADD     G_REG
        ST      H6
        LD      H7
        ADD     H_REG
        ST      H7
        
        ; 输出结果到 I/O 缓冲区
        LD      H0
        ST      IO_BUF
        LD      H1
        ST      IO_BUF+1
        LD      H2
        ST      IO_BUF+2
        LD      H3
        ST      IO_BUF+3
        LD      H4
        ST      IO_BUF+4
        LD      H5
        ST      IO_BUF+5
        LD      H6
        ST      IO_BUF+6
        LD      H7
        ST      IO_BUF+7
        
        ; 发送完成信号
        LD      CONST_DONE
        ST      STATUS_REG
        
        JMP     START           ; 准备下一块

; ========== 数据区 ==========
        ORG 64

H0:     DS      1
H1:     DS      1
H2:     DS      1
H3:     DS      1
H4:     DS      1
H5:     DS      1
H6:     DS      1
H7:     DS      1

A_REG:  DS      1
B_REG:  DS      1
C_REG:  DS      1
D_REG:  DS      1
E_REG:  DS      1
F_REG:  DS      1
G_REG:  DS      1
H_REG:  DS      1

T1:     DS      1
T2:     DS      1
ROUND_CNT: DS  1

        ORG 80
W_TABLE: DS     64              ; W[0..63]

        ORG 144
SIGMA1_E: DS    1
CH_EFG:   DS    1
SIGMA0_A: DS    1
Maj_ABC:  DS    1

        ORG 192
K_TABLE: DS     32              ; K 常量 (分页加载)

        ORG 224
IO_BUF:  DS     8               ; 输出缓冲区
STATUS_REG: DS  1

        ORG 250
ZERO:    DC     0
ONE:     DC     1
CONST_64: DC    64
CONST_DONE: DC  0xFFFF

        END
