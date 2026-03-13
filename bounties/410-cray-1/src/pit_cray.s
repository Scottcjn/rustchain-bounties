*
*     RustChain Miner for Cray-1
*     Timing Measurements (Cray Assembly Language - CAL)
*
*     This module implements precise timing measurements
*     for hardware fingerprinting.
*
*     Build: cal -o pit_cray.o pit_cray.s
*
        TITLE 'PIT_CRAY - Timing Measurements'
*
        ENTRY MEASURE_VECTOR_TIME
        ENTRY MEASURE_SCALAR_TIME
        ENTRY MEASURE_MEMORY_TIME
        ENTRY GET_CYCLE_COUNT
*
*=======================================================================
*
*     MEASURE_VECTOR_TIME - Measure vector operation timing
*
*     Returns:
*       A0 = Timing signature (lower = faster)
*
        MEASURE_VECTOR_TIME
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    VLR
*
*     Set vector length to 64
*
        A1      64
        MTSP    A1,VLR
*
*     Get start cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,START_TIME
*
*     Execute vector operations
*
        LVW     V0,TEST_DATA
        LVW     V1,TEST_DATA+64
*
        VADD    V2,V0,V1
        VMULT   V3,V0,V1
        VXOR    V4,V2,V3
        VROT    V5,V4,7
*
*     Get end cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,END_TIME
*
*     Calculate delta
*
        LVW     A0,END_TIME
        LVW     A1,START_TIME
        SUB     A0,A1
*
*     Store timing signature
*
        STI     A0,VECTOR_TIME_SIG
*
        POP     VLR
        POP     A2
        POP     A1
        POP     A0
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     MEASURE_SCALAR_TIME - Measure scalar operation timing
*
*     Returns:
*       A0 = Timing signature
*
        MEASURE_SCALAR_TIME
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
*
*     Get start cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,START_TIME
*
*     Execute scalar operations (1000 iterations)
*
        A1      ZERO
        A2      1000
*
LOOP_SCALAR
        ADD     A1,ONE
        SUB     A2,ONE
        JNZ     A0,LOOP_SCALAR
*
*     Get end cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,END_TIME
*
*     Calculate delta
*
        LVW     A0,END_TIME
        LVW     A1,START_TIME
        SUB     A0,A1
*
*     Store timing signature
*
        STI     A0,SCALAR_TIME_SIG
*
        POP     A3
        POP     A2
        POP     A1
        POP     A0
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     MEASURE_MEMORY_TIME - Measure memory access timing
*
*     Returns:
*       A0 = Timing signature
*
        MEASURE_MEMORY_TIME
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
*
*     Get start cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,START_TIME
*
*     Access memory with stride pattern (test interleaving)
*
        A1      MEM_BASE
        A2      16              * 16-way interleaving
        A3      ZERO
*
LOOP_MEM
        LVW     A3,0(A1)
        ADD     A1,8            * Next word (64-bit)
        SUB     A2,ONE
        JNZ     A0,LOOP_MEM
*
*     Get end cycle count
*
        CALL    GET_CYCLE_COUNT
        STI     A0,END_TIME
*
*     Calculate delta
*
        LVW     A0,END_TIME
        LVW     A1,START_TIME
        SUB     A0,A1
*
*     Store timing signature
*
        STI     A0,MEMORY_TIME_SIG
*
        POP     A3
        POP     A2
        POP     A1
        POP     A0
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_CYCLE_COUNT - Get current cycle count
*
*     Returns:
*       A0 = Cycle count
*
        GET_CYCLE_COUNT
*
        BEGIN
*
*     Read cycle counter register
*
        MFSP    A0,CYCLE_CNT
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     Data section
*
        ORG     *+100H
*
TEST_DATA
        DS      128             * 16 words for vector ops
*
START_TIME
        DS      1
*
END_TIME
        DS      1
*
VECTOR_TIME_SIG
        DS      1
*
SCALAR_TIME_SIG
        DS      1
*
MEMORY_TIME_SIG
        DS      1
*
MEM_BASE
        DC      01000000H       * Base memory address
*
CYCLE_CNT       EQU     0FDH    * Cycle counter register
*
ZERO            EQU     0
ONE             EQU     1
*
        END
