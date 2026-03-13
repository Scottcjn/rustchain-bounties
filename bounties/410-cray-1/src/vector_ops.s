*
*     RustChain Miner for Cray-1
*     Vector Operations (Cray Assembly Language - CAL)
*
*     This module implements optimized vector operations
*     for the Cray-1 vector processor.
*
*     Build: cal -o vector_ops.o vector_ops.s
*
        TITLE 'VECTOR_OPS - Cray-1 Vector Operations'
*
        ENTRY VECTOR_HASH_INIT
        ENTRY VECTOR_HASH_UPDATE
        ENTRY VECTOR_HASH_FINAL
        ENTRY VECTOR_MEMSET
        ENTRY VECTOR_MEMCPY
        ENTRY VECTOR_XOR
*
*=======================================================================
*
*     VECTOR_HASH_INIT - Initialize vector hash computation
*
*     Input:
*       A0 = Pointer to hash state (256 bytes)
*
        VECTOR_HASH_INIT
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    VLR
*
*     Set vector length to 64
*
        A1      64
        MTSP    A1,VLR
*
*     Initialize hash state with constants
*
        LVW     V0,HASH_CONSTS
        SVW     0(A0),V0
*
        LVW     V1,HASH_CONSTS+64
        SVW     64(A0),V1
*
        LVW     V2,HASH_CONSTS+128
        SVW     128(A0),V2
*
        LVW     V3,HASH_CONSTS+192
        SVW     192(A0),V3
*
        POP     VLR
        POP     A1
        POP     A0
*
        RETURN  ZERO
*
        END
*
*=======================================================================
*
*     VECTOR_HASH_UPDATE - Update hash with data block
*
*     Input:
*       A0 = Pointer to hash state
*       A1 = Pointer to data block
*       A2 = Data length
*
        VECTOR_HASH_UPDATE
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
        PUSH    VLR
*
*     Set vector length
*
        MTSP    A2,VLR
*
*     Load data into vector registers
*
        LVW     V4,0(A1)
        LVW     V5,64(A1)
*
*     Load hash state
*
        LVW     V0,0(A0)
        LVW     V1,64(A0)
*
*     Vector hash round 1: XOR
*
        VXOR    V0,V0,V4
        VXOR    V1,V1,V5
*
*     Vector hash round 2: Rotate and add
*
        VROT    V4,V0,7
        VADD    V0,V0,V4
*
        VROT    V5,V1,11
        VADD    V1,V1,V5
*
*     Vector hash round 3: Multiply (mixing)
*
        VMULT   V2,V0,V1
        VXOR    V0,V0,V2
*
*     Store updated state
*
        SVW     0(A0),V0
        SVW     64(A0),V1
*
        POP     VLR
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
*     VECTOR_HASH_FINAL - Finalize hash computation
*
*     Input:
*       A0 = Pointer to hash state
*       A1 = Pointer to output buffer (32 bytes)
*
        VECTOR_HASH_FINAL
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    VLR
*
*     Set vector length to 4
*
        A2      4
        MTSP    A2,VLR
*
*     Load final state
*
        LVW     V0,0(A0)
        LVW     V1,64(A0)
*
*     Final mixing
*
        VXOR    V2,V0,V1
        VROT    V3,V2,13
        VXOR    V0,V2,V3
*
*     Store hash output
*
        SVW     0(A1),V0
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
*     VECTOR_MEMSET - Vector memory set
*
*     Input:
*       A0 = Destination pointer
*       A1 = Value to set
*       A2 = Number of words
*
        VECTOR_MEMSET
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    VLR
*
*     Set vector length
*
        MTSP    A2,VLR
*
*     Broadcast value to vector register
*
        SBRD    V0,A1
*
*     Store vector to memory
*
        SVW     0(A0),V0
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
*     VECTOR_MEMCPY - Vector memory copy
*
*     Input:
*       A0 = Destination pointer
*       A1 = Source pointer
*       A2 = Number of words
*
        VECTOR_MEMCPY
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    VLR
*
*     Set vector length
*
        MTSP    A2,VLR
*
*     Load from source
*
        LVW     V0,0(A1)
*
*     Store to destination
*
        SVW     0(A0),V0
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
*     VECTOR_XOR - Vector XOR operation
*
*     Input:
*       A0 = Destination pointer
*       A1 = Source 1 pointer
*       A2 = Source 2 pointer
*       A3 = Number of words
*
        VECTOR_XOR
*
        BEGIN
*
        PUSH    A0
        PUSH    A1
        PUSH    A2
        PUSH    A3
        PUSH    VLR
*
*     Set vector length
*
        MTSP    A3,VLR
*
*     Load operands
*
        LVW     V0,0(A1)
        LVW     V1,0(A2)
*
*     XOR
*
        VXOR    V2,V0,V1
*
*     Store result
*
        SVW     0(A0),V2
*
        POP     VLR
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
*     Data section - Hash constants
*
        ORG     *+100H
*
HASH_CONSTS
*     SHA-256 initial hash values (first 8 words)
        DC      6A09E667H
        DC      BB67AE85H
        DC      3C6EF372H
        DC      A54FF53AH
        DC      510E527FH
        DC      9B05688CH
        DC      1F83D9ABH
        DC      5BE0CD19H
*
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
*
*     Additional constants for rounds 2-4
*
HASH_CONSTS+64
        DC      0DEADBEEFH
        DC      0CAFEBABEH
        DC      01234567H
        DC      89ABCDEFH
        DC      0FEDCBA98H
        DC      76543210H
        DC      0ABCDEF01H
        DC      23456789H
*
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
*
HASH_CONSTS+128
        DC      01111111H
        DC      02222222H
        DC      03333333H
        DC      04444444H
        DC      05555555H
        DC      06666666H
        DC      07777777H
        DC      08888888H
*
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
*
HASH_CONSTS+192
        DC      09999999H
        DC      0AAAAAAAH
        DC      0BBBBBBBH
        DC      0CCCCCCCCH
        DC      0DDDDDDDDH
        DC      0EEEEEEEEH
        DC      0FFFFFFFFH
        DC      00000000H
*
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
        DC      00000000H
*
*     Register definitions
*
VLR             EQU     0FBH    * Vector Length Register
*
ZERO            EQU     0
ONE             EQU     1
*
        END
