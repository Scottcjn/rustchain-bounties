C
C     RustChain Miner for Cray-1
C     Common Definitions and Constants
C
C     Include this file in all Fortran source files
C
C$    INCLUDE 'miner.h'
C
C=======================================================================
C     Version Information
C=======================================================================
C
      CHARACTER*10 MINER_VERSION
      PARAMETER (MINER_VERSION = '0.1.0-cray1')
C
      CHARACTER*20 PLATFORM_NAME
      PARAMETER (PLATFORM_NAME = 'Cray-1')
C
C=======================================================================
C     Default Configuration
C=======================================================================
C
      CHARACTER*128 DEFAULT_NODE_URL
      PARAMETER (DEFAULT_NODE_URL = 'https://50.28.86.131')
C
      INTEGER*4 DEFAULT_BLOCK_TIME
      PARAMETER (DEFAULT_BLOCK_TIME = 600)  * 10 minutes
C
      INTEGER*4 DEFAULT_PORT
      PARAMETER (DEFAULT_PORT = 443)
C
C=======================================================================
C     Buffer Sizes
C=======================================================================
C
      INTEGER*4 MAX_WALLET_LEN
      PARAMETER (MAX_WALLET_LEN = 64)
C
      INTEGER*4 MAX_MINER_ID_LEN
      PARAMETER (MAX_MINER_ID_LEN = 64)
C
      INTEGER*4 MAX_NODE_URL_LEN
      PARAMETER (MAX_NODE_URL_LEN = 128)
C
      INTEGER*4 MAX_HASH_LEN
      PARAMETER (MAX_HASH_LEN = 64)
C
      INTEGER*4 MAX_REQUEST_LEN
      PARAMETER (MAX_REQUEST_LEN = 256)
C
      INTEGER*4 MAX_RESPONSE_LEN
      PARAMETER (MAX_RESPONSE_LEN = 256)
C
C=======================================================================
C     Mining Constants
C=======================================================================
C
      INTEGER*4 HASH_RATE_UPDATE_INTERVAL
      PARAMETER (HASH_RATE_UPDATE_INTERVAL = 10)
C
      INTEGER*4 STATUS_DISPLAY_INTERVAL
      PARAMETER (STATUS_DISPLAY_INTERVAL = 10)
C
      INTEGER*4 DEFAULT_DIFFICULTY
      PARAMETER (DEFAULT_DIFFICULTY = 1000)
C
      INTEGER*4 MAX_SHARE_RETRIES
      PARAMETER (MAX_SHARE_RETRIES = 3)
C
C=======================================================================
C     Hardware Detection Constants
C=======================================================================
C
      INTEGER*4 NUM_FINGERPRINT_TESTS
      PARAMETER (NUM_FINGERPRINT_TESTS = 6)
C
      INTEGER*4 VECTOR_ELEMENTS
      PARAMETER (VECTOR_ELEMENTS = 64)
C
      INTEGER*4 MEMORY_BANKS
      PARAMETER (MEMORY_BANKS = 16)
C
C     Timing thresholds (in cycles)
C
      INTEGER*4 MIN_VECTOR_TIME
      PARAMETER (MIN_VECTOR_TIME = 700)
C
      INTEGER*4 MAX_VECTOR_TIME
      PARAMETER (MAX_VECTOR_TIME = 900)
C
      INTEGER*4 EXPECTED_SCALAR_TIME
      PARAMETER (EXPECTED_SCALAR_TIME = 125)
C
      INTEGER*4 EXPECTED_MEMORY_TIME
      PARAMETER (EXPECTED_MEMORY_TIME = 200)
C
C=======================================================================
C     Error Codes
C=======================================================================
C
      INTEGER*4 ERR_SUCCESS
      PARAMETER (ERR_SUCCESS = 0)
C
      INTEGER*4 ERR_GENERAL
      PARAMETER (ERR_GENERAL = 1)
C
      INTEGER*4 ERR_NETWORK_INIT
      PARAMETER (ERR_NETWORK_INIT = 10)
C
      INTEGER*4 ERR_NETWORK_SEND
      PARAMETER (ERR_NETWORK_SEND = 11)
C
      INTEGER*4 ERR_NETWORK_RECV
      PARAMETER (ERR_NETWORK_RECV = 12)
C
      INTEGER*4 ERR_ATTESTATION
      PARAMETER (ERR_ATTESTATION = 20)
C
      INTEGER*4 ERR_HARDWARE_INIT
      PARAMETER (ERR_HARDWARE_INIT = 30)
C
      INTEGER*4 ERR_EMULATOR_DETECTED
      PARAMETER (ERR_EMULATOR_DETECTED = 31)
C
      INTEGER*4 ERR_INVALID_WALLET
      PARAMETER (ERR_INVALID_WALLET = 40)
C
      INTEGER*4 ERR_INVALID_SHARE
      PARAMETER (ERR_INVALID_SHARE = 50)
C
C=======================================================================
C     Log Levels
C=======================================================================
C
      INTEGER*4 LOG_ERROR
      PARAMETER (LOG_ERROR = 0)
C
      INTEGER*4 LOG_WARNING
      PARAMETER (LOG_WARNING = 1)
C
      INTEGER*4 LOG_INFO
      PARAMETER (LOG_INFO = 2)
C
      INTEGER*4 LOG_DEBUG
      PARAMETER (LOG_DEBUG = 3)
C
      INTEGER*4 LOG_VERBOSE
      PARAMETER (LOG_VERBOSE = 4)
C
C=======================================================================
C     Common Blocks
C=======================================================================
C
      COMMON /MINER_STATE/ 
     +    WALLET(MAX_WALLET_LEN),
     +    MINER_ID(MAX_MINER_ID_LEN),
     +    NODE_URL(MAX_NODE_URL_LEN),
     +    VERBOSE,
     +    RUNNING
C
      COMMON /MINING_STATS/
     +    BLOCK_HEIGHT,
     +    HASH_RATE,
     +    SHARES_SUBMITTED,
     +    SHARES_ACCEPTED,
     +    SHARES_REJECTED,
     +    START_TIME
C
      COMMON /HARDWARE_INFO/
     +    CPU_TYPE,
     +    CPU_SPEED,
     +    MEMORY_SIZE,
     +    VECTOR_UNITS,
     +    IS_REAL_HARDWARE
C
      CHARACTER*64 WALLET
      CHARACTER*64 MINER_ID
      CHARACTER*128 NODE_URL
      INTEGER*4 VERBOSE
      INTEGER*4 RUNNING
C
      INTEGER*4 BLOCK_HEIGHT
      INTEGER*4 HASH_RATE
      INTEGER*4 SHARES_SUBMITTED
      INTEGER*4 SHARES_ACCEPTED
      INTEGER*4 SHARES_REJECTED
      INTEGER*4 START_TIME
C
      CHARACTER*20 CPU_TYPE
      INTEGER*4 CPU_SPEED
      INTEGER*4 MEMORY_SIZE
      INTEGER*4 VECTOR_UNITS
      INTEGER*4 IS_REAL_HARDWARE
C
C=======================================================================
C     External Function Declarations
C=======================================================================
C
C     Hardware detection
C
      INTEGER*4 HW_CRAY_INIT
      INTEGER*4 GENERATE_MINER_ID_CRAY
      INTEGER*4 DETECT_EMULATOR
      INTEGER*4 GET_MEM_SIZE_CRAY
      INTEGER*4 GET_BIOS_DATE_CRAY
C
C     Mining
C
      INTEGER*4 COMPUTE_HASH_VECTOR
      INTEGER*4 SUBMIT_SHARE
C
C     Network
C
      INTEGER*4 NETWORK_INIT
      INTEGER*4 ATTEST_TO_NODE
C
C     Timing
C
      INTEGER*4 MEASURE_VECTOR_TIME
      INTEGER*4 MEASURE_SCALAR_TIME
      INTEGER*4 MEASURE_MEMORY_TIME
C
C=======================================================================
C     End of Header
C=======================================================================
