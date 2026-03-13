*
*     RustChain Miner for Cray-1
*     Hardware Detection (Cray Assembly Language - CAL)
*
*     This module implements Cray-1 specific hardware detection
*     and fingerprinting to verify real vintage hardware.
*
*     Build: cal -o hw_cray.o hw_cray.s
*
        TITLE 'HW_CRAY - Cray-1 Hardware Detection'
*
        ENTRY HW_CRAY_INIT
        ENTRY GENERATE_MINER_ID_CRAY
        ENTRY DETECT_EMULATOR
        ENTRY GET_MEM_SIZE_CRAY
        ENTRY GET_BIOS_DATE_CRAY
*
*=======================================================================
*
*     HW_CRAY_INIT - Initialize hardware detection
*
*     Returns:
*       A0 = 0 on success, non-zero on failure
*
        HW_CRAY_INIT
*
        BEGIN
*
*     Test vector unit availability
*
        LVW     V0,0(A0)          * Load test word
        SVW     V0,0(A0)          * Store test word
*
*     Check for Cray-1 specific instruction timing
*
        MFSP    A1,VCR            * Get vector control register
        MTSP    A1,VCR            * Restore (test access)
*
*     Test memory interleaving
*
        CALL    TEST_MEM_INTERLEAVE
*
*     Return success
*
        A0      ZERO
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GENERATE_MINER_ID_CRAY - Generate unique miner ID
*
*     Input:
*       A0 = Pointer to output buffer (64 bytes)
*
*     Uses hardware fingerprint to create unique identifier
*
        GENERATE_MINER_ID_CRAY
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
*
*     Gather hardware fingerprint components
*
        CALL    GET_VECTOR_TIMING     * A1 = vector timing signature
        CALL    GET_MEMORY_SIGNATURE  * A2 = memory signature
        CALL    GET_SCALAR_SIGNATURE  * A3 = scalar signature
*
*     Combine into hash (simplified)
*
        XOR     A1,A2
        XOR     A1,A3
*
*     Store to output buffer
*
        POP     A0
        STI     A1,0(A0)
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
*     DETECT_EMULATOR - Check if running in emulator
*
*     Returns:
*       A0 = 0 if real hardware, 1 if emulator
*
        DETECT_EMULATOR
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
*
*     Test 1: Vector timing analysis
*
        CALL    TEST_VECTOR_TIMING
        JZ      A0,TEST2            * If passes, continue
*
        A0      ONE
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
*     Test 2: Memory interleaving
*
TEST2   CALL    TEST_MEM_INTERLEAVE
        JZ      A0,TEST3
*
        A0      ONE
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
*     Test 3: Scalar processor timing
*
TEST3   CALL    TEST_SCALAR_TIMING
        JZ      A0,PASS
*
        A0      ONE
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
*     All tests passed - real hardware
*
PASS    A0      ZERO
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_MEM_SIZE_CRAY - Get memory size in million words
*
*     Returns:
*       A0 = Memory size in MW
*
        GET_MEM_SIZE_CRAY
*
        BEGIN
*
*     Read memory configuration register
*
        MFSP    A0,MEMCFG
*
*     Extract size field (bits 0-7)
*
        AND     A0,0FFH
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_BIOS_DATE_CRAY - Get system date
*
*     Input:
*       A0 = Pointer to output buffer (20 bytes)
*
        GET_BIOS_DATE_CRAY
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
*
*     Read real-time clock
*
        MFSP    A1,RTC
*
*     Convert to string (simplified)
*
        POP     A0
        STI     A1,0(A0)
*
        POP     A1
        POP     A0
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     TEST_VECTOR_TIMING - Test vector processor timing
*
*     Returns:
*       A0 = 0 if passes, 1 if fails (emulator)
*
        TEST_VECTOR_TIMING
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
*
*     Load vector with known data
*
        LVW     V0,TEST_DATA
*
*     Time vector operation
*
        MFSP    A1,CLOCK          * Start time
        VADD    V1,V0,V0          * Vector add
        MFSP    A2,CLOCK          * End time
*
*     Calculate delta
*
        SUB     A2,A1
*
*     Real Cray-1: 12.5 ns per element (80 MHz)
*     Emulator: Usually much different
*
        CMP     A2,EXPECTED_TIME
        JZ      A0,PASS_VECTOR
*
        A0      ONE
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
PASS_VECTOR
        A0      ZERO
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     TEST_MEM_INTERLEAVE - Test memory interleaving pattern
*
*     Returns:
*       A0 = 0 if passes, 1 if fails
*
        TEST_MEM_INTERLEAVE
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
*
*     Access pattern to test 16-way interleaving
*
        A1      ZERO
        A2      ZERO
*
LOOP_MEM
        CMP     A1,16
        JGE     A0,CHECK_RESULT
*
        LVW     A3,MEM_BASE(A1)
        ADD     A2,A3
        ADD     A1,ONE
        JMP     LOOP_MEM
*
CHECK_RESULT
*
*     Check for expected interleaving signature
*
        CMP     A2,EXPECTED_INTERLEAVE
        JZ      A0,PASS_INTERLEAVE
*
        A0      ONE
        POP     A3
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
PASS_INTERLEAVE
        A0      ZERO
        POP     A3
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     TEST_SCALAR_TIMING - Test scalar processor timing
*
*     Returns:
*       A0 = 0 if passes, 1 if fails
*
        TEST_SCALAR_TIMING
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
*
*     Time scalar operations
*
        MFSP    A1,CLOCK
*
        A2      ZERO
        A3      1000
LOOP_SCALAR
        ADD     A2,ONE
        SUB     A3,ONE
        JNZ     A0,LOOP_SCALAR
*
        MFSP    A2,CLOCK
        SUB     A2,A1
*
*     Check timing
*
        CMP     A2,EXPECTED_SCALAR_TIME
        JZ      A0,PASS_SCALAR
*
        A0      ONE
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
PASS_SCALAR
        A0      ZERO
        POP     A2
        POP     A1
        POP     A0
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_VECTOR_TIMING - Get vector timing signature
*
*     Returns:
*       A0 = Vector timing signature
*
        GET_VECTOR_TIMING
*
        BEGIN
*
        PUSH    A1
        PUSH    A2
*
        MFSP    A1,CLOCK
        LVW     V0,TEST_DATA
        VADD    V1,V0,V0
        MFSP    A2,CLOCK
        SUB     A0,A2,A1
*
        POP     A2
        POP     A1
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_MEMORY_SIGNATURE - Get memory signature
*
*     Returns:
*       A0 = Memory signature
*
        GET_MEMORY_SIGNATURE
*
        BEGIN
*
        PUSH    A1
        PUSH    A2
*
        A0      ZERO
        A1      MEM_BASE
        A2      64
LOOP_MEM_SIG
        LVW     A3,0(A1)
        XOR     A0,A3
        ADD     A1,8
        SUB     A2,ONE
        JNZ     A0,LOOP_MEM_SIG
*
        POP     A2
        POP     A1
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     GET_SCALAR_SIGNATURE - Get scalar processor signature
*
*     Returns:
*       A0 = Scalar signature
*
        GET_SCALAR_SIGNATURE
*
        BEGIN
*
        PUSH    A1
        PUSH    A2
*
        A0      ZERO
        A1      1000
LOOP_SCALAR_SIG
        ADD     A0,ONE
        SUB     A1,ONE
        JNZ     A0,LOOP_SCALAR_SIG
*
        POP     A2
        POP     A1
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
        DC      0DEADBEEFH
*
EXPECTED_TIME
        DC      800             * 80 MHz = 12.5ns * 64 elements
*
EXPECTED_INTERLEAVE
        DC      012345678H
*

EXPECTED_SCALAR_TIME
        DC      125             * Scalar timing at 80 MHz
*
MEM_BASE
        DC      01000000H       * Base memory address
*
MEMCFG          EQU     0FFH    * Memory config register
RTC             EQU     0FEH    * Real-time clock
CLOCK           EQU     0FDH    * Cycle counter
VCR             EQU     0FCH    * Vector control register
*
ZERO            EQU     0
ONE             EQU     1
*
        END
