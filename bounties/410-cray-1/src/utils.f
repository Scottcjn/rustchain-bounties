C
C     RustChain Miner for Cray-1
C     Utility Functions
C
C     Build: cft -o utils.o utils.f
C
      SUBROUTINE DELAY_MS(MS)
C
      IMPLICIT NONE
C
      INTEGER*4 MS
      INTEGER*4 I, J, K
      INTEGER*4 LOOPS
C
C     Calculate loop count (approximately MS milliseconds)
C     Cray-1 @ 80 MHz: ~80,000 cycles per ms
C
      LOOPS = MS * 80
C
      DO 100 I = 1, LOOPS
         J = I * 2
         K = J + 1
  100 CONTINUE
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE GETENV_CRAY(VAR_NAME, VAR_VALUE)
C
      IMPLICIT NONE
C
      CHARACTER*(*) VAR_NAME
      CHARACTER*(*) VAR_VALUE
C
C     Get environment variable (COS-specific)
C     Placeholder implementation
C
      VAR_VALUE = ' '
C
      RETURN
      END
C
C=======================================================================
C
      INTEGER*4 FUNCTION IARGC_CRAY()
C
      IMPLICIT NONE
C
C     Get argument count (COS-specific)
C
      IARGC_CRAY = 0
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE GETARG_CRAY(ARG_NUM, ARG_VALUE)
C
      IMPLICIT NONE
C
      INTEGER*4 ARG_NUM
      CHARACTER*(*) ARG_VALUE
C
C     Get argument value (COS-specific)
C
      ARG_VALUE = ' '
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE PRINT_HEX(VALUE)
C
      IMPLICIT NONE
C
      INTEGER*4 VALUE
      CHARACTER*16 HEX_CHARS
      PARAMETER (HEX_CHARS = '0123456789ABCDEF')
C
      INTEGER*4 I, V, POS
      CHARACTER*8 HEX_STR
C
      HEX_STR = '        '
      V = VALUE
C
      DO 100 I = 1, 8
         POS = MOD(V, 16) + 1
         HEX_STR(9-I:9-I) = HEX_CHARS(POS:POS)
         V = V / 16
  100 CONTINUE
C
      WRITE(*,*) '0x', HEX_STR
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE PRINT_BINARY(VALUE)
C
      IMPLICIT NONE
C
      INTEGER*4 VALUE
      INTEGER*4 I, V, BIT
      CHARACTER*32 BIN_STR
C
      BIN_STR = '                                '
      V = VALUE
C
      DO 100 I = 1, 32
         BIT = MOD(V, 2)
         IF (BIT .EQ. 1) THEN
            BIN_STR(33-I:33-I) = '1'
         ELSE
            BIN_STR(33-I:33-I) = '0'
         ENDIF
         V = V / 2
  100 CONTINUE
C
      WRITE(*,*) BIN_STR
C
      RETURN
      END
C
C=======================================================================
C
      INTEGER*4 FUNCTION RANDOM_CRAY()
C
      IMPLICIT NONE
C
      INTEGER*4 SEED
      SAVE SEED
      DATA SEED /12345/
C
C     Simple LCG random number generator
C
      SEED = MOD(SEED * 1103515245 + 12345, 2147483648)
      RANDOM_CRAY = SEED
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE INIT_RANDOM(SEED)
C
      IMPLICIT NONE
C
      INTEGER*4 SEED
C
C     Initialize random number generator
C
      CALL RANDOM_SEED(SEED)
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE SLEEP_SECONDS(SECS)
C
      IMPLICIT NONE
C
      INTEGER*4 SECS
C
C     Sleep for specified seconds
C
      CALL DELAY_MS(SECS * 1000)
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE GET_TIME(TIME_STR)
C
      IMPLICIT NONE
C
      CHARACTER*20 TIME_STR
C
C     Get current time as string
C     Placeholder implementation
C
      TIME_STR = '00:00:00'
C
      RETURN
      END
C
C=======================================================================
C
      SUBROUTINE LOG_MESSAGE(LEVEL, MESSAGE)
C
      IMPLICIT NONE
C
      CHARACTER*10 LEVEL
      CHARACTER*(*) MESSAGE
      CHARACTER*20 TIME_STR
C
C     Log message with timestamp
C
      CALL GET_TIME(TIME_STR)
C
      WRITE(*,1000) TIME_STR, LEVEL, MESSAGE
 1000 FORMAT('[', A, '] [', A, '] ', A)
C
      RETURN
      END
