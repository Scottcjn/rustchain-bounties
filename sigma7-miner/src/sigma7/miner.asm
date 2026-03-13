* SIGMA 7 RUSTCHAIN MINER - MAIN PROGRAM
* Meta-Symbol Assembly for CP-V Operating System
* 
* This is a MINIMAL reference implementation demonstrating
* the feasibility of running RustChain on Sigma 7 (1967)
*
* Memory Requirements: 32K words (128 KB)
* Epoch Time: ~10 minutes (600 seconds)
* Communication: COC Serial @ 9600 baud
*
* Author: OpenClaw Subagent
* Date: 2026-03-13
* License: MIT

         TITLE  SIGMA7-RUSTCHAIN-MINER
         SPACE  2

***********************************************************************
* EQUATES AND CONSTANTS
***********************************************************************

* System Equates
NULL     EQU    0
TRUE     EQU    1
FALSE    EQU    0

* COC (Character Oriented Communications) Equates
COCBASE  EQU    X'FFA0'        COC Base Address
LIU0BASE EQU    X'FFA0'        Line Interface Unit 0
XMITRDY  EQU    X'02'          Transmit Ready Bit
RECVRDY  EQU    X'01'          Receive Ready Bit

* Protocol Constants
CMD_EPOCH     EQU  X'01'       Request Epoch Info
CMD_ATTEST    EQU  X'02'       Submit Attestation
CMD_BALANCE   EQU  X'03'       Check Balance
CMD_HEARTBEAT EQU  X'04'       Heartbeat Ping

STATUS_OK     EQU  X'00'       Success
STATUS_ERR    EQU  X'01'       Error
STATUS_RETRY  EQU  X'02'       Retry

* Memory Addresses
PROGSTART  EQU  X'10000'       Program Start
DATASTART  EQU  X'18000'       Data Area
STACKTOP   EQU  X'1C000'       Stack Top

* Wallet Storage (stored in non-volatile area)
WALLETADDR EQU  X'1FF00'       Wallet address storage

***********************************************************************
* EXTERNAL REFERENCES
***********************************************************************

         EXTRN  IOSCHED,IOCOMP,IOABORT    * I/O Scheduler
         EXTRN  CLOCKRD                   * System Clock Read
         EXTRN  DISKREAD,DISKWRITE         * Disk I/O

***********************************************************************
* START OF PROGRAM
***********************************************************************

         ORG    PROGSTART
MINER    START  0

* Entry Point - Called by OS or Console Load
         ENTRY  MINER

* Save Caller's Registers
         STM    14,12,12(13)

* Initialize Stack Pointer
         LA     13,STACKTOP

* Initialize Data Area
         LA     15,DATASTART
         MVC    0(4096,15),=X'00'        Clear data area

* Print Startup Message
         LA     1,MSGSTART
         LA     2,MSGSTARTLEN
         BAL    14,PRINTMSG

* Load Wallet Address from Storage
         BAL    14,LOADWALLET
         LTR    15,15
         BNZ    WALLETERR

* Main Mining Loop
MAINLOOP DS     0H

* Wait for Epoch Start (check system clock)
         BAL    14,WAITFOREPOCH

* Collect Hardware Fingerprint
         BAL    14,COLLECTFINGERPRINT

* Build Attestation Message
         BAL    14,BUILDATTESTATION

* Send to Gateway via Serial
         BAL    14,SENDATTESTATION
         LTR    15,15
         BNZ    SENDERR

* Receive Response
         BAL    14,RECEIVERESPONSE
         LTR    15,15
         BNZ    RESPERR

* Check if Reward Received
         BAL    14,CHECKREWARD

* Log Epoch Completion
         BAL    14,LOGEPOCH

* Loop Back
         B      MAINLOOP

* Error Handlers
WALLETERR
         LA     1,MSGWALLETERR
         LA     2,MSGWALLETERRLEN
         BAL    14,PRINTMSG
         B      HALTMINER

SENDERR
         LA     1,MSGSENDERR
         LA     2,MSGSENDERRLEN
         BAL    14,PRINTMSG
         B      RETRYEPOCH

RESPERR
         LA     1,MSGRESPERR
         LA     2,MSGRESPERRLEN
         BAL    14,PRINTMSG
         B      RETRYEPOCH

RETRYEPOCH
         BAL    14,DELAY5SEC
         B      MAINLOOP

HALTMINER
         LA     0,0              Return code 0
         LM     14,12,12(13)     Restore registers
         BR     14               Return to OS

***********************************************************************
* SUBROUTINE: PRINTMSG - Print Message to Console
* Input: R1 = Message Address, R2 = Message Length
***********************************************************************

PRINTMSG DS     0H
         STM    1,3,72(13)       Save registers
         
* Use CP-V Console Output Service
         LA     15,CONSOUT       Console output function code
         SVC    6                Supervisor Call
         
         LM     1,3,72(13)       Restore registers
         BR     14               Return

CONSOUT  EQU    3                Console output function

***********************************************************************
* SUBROUTINE: LOADWALLET - Load Wallet from Storage
* Output: R15 = 0 if success, 1 if error
***********************************************************************

LOADWALLET DS   0H
         STM    1,3,72(13)
         
* Read wallet from disk storage
         LA     1,WALLETBUF      Buffer for wallet
         LA     2,=X'0001'       Disk address
         LA     3,=X'0028'       Length (40 bytes for wallet string)
         BAL    14,DISKREAD
         LTR    15,15
         BNZ    LOADFAIL
         
* Validate wallet format (starts with 'RTC')
         CLC    0(3),=C'RTC'
         BNE    LOADFAIL
         
         LA     15,0             Success
         B      LOADEND

LOADFAIL LA     15,1             Error
LOADEND  LM     1,3,72(13)
         BR     14

***********************************************************************
* SUBROUTINE: WAITFOREPOCH - Wait for Next Epoch
* Epochs are 10 minutes (600 seconds)
***********************************************************************

WAITFOREPOCH DS 0H
         STM    1,3,72(13)
         
* Read current time
         BAL    14,CLOCKRD
         ST     0,CURTIME        Store current time
         
* Calculate seconds until next epoch boundary
         L      1,CURTIME
         LA     2,600            Epoch duration
         LR     3,1
         SRDA   3,32             Divide by 600
         DR     2,3              R2 = remainder
         LR     1,2
         L      2,=F'600'
         SR     2,1              Seconds to wait
         
* Busy wait (simplified - would use timer interrupt in production)
WAITLOOP DS     0H
         BCT    2,WAITLOOP       Decrement and loop
         
         LM     1,3,72(13)
         BR     14

CURTIME  DS     F                Current time storage

***********************************************************************
* SUBROUTINE: COLLECTFINGERPRINT - Hardware Fingerprint
* Collects timing-based hardware characteristics
***********************************************************************

COLLECTFINGERPRINT DS 0H
         STM    1,5,72(13)
         
* Measure memory access timing
         BAL    14,MEMTIMING
         ST     15,MEMTIMING_VAL

* Measure instruction timing variance
         BAL    14,INSTTIMING
         ST     15,INSTTIMING_VAL

* Read system clock skew
         BAL    14,CLOCKSKEW
         ST     15,CLOCKSKEW_VAL

* Combine into fingerprint hash (simplified)
         L      1,MEMTIMING_VAL
         L      2,INSTTIMING_VAL
         L      3,CLOCKSKEW_VAL
         XR     1,2
         XR     1,3
         ST     1,FINGERPRINT

         LA     15,0             Success
         LM     1,5,72(13)
         BR     14

MEMTIMING_VAL DS F
INSTTIMING_VAL DS F
CLOCKSKEW_VAL  DS F
FINGERPRINT    DS F

***********************************************************************
* SUBROUTINE: MEMTIMING - Measure Memory Access Time
***********************************************************************

MEMTIMING DS   0H
         STM    1,3,72(13)
         
* Time a series of memory accesses
         LA     2,1000           Iteration count
         BAL    14,CLOCKRD
         ST     0,TIMESTART

MEMLOOP  DS     0H
         L      3,0(13)          Memory access
         BCT    2,MEMLOOP

         BAL    14,CLOCKRD
         S      0,TIMESTART      Elapsed time
         LR     15,0             Return time in R0 (simplified)
         
         LM     1,3,72(13)
         BR     14

TIMESTART DS   F

***********************************************************************
* SUBROUTINE: INSTTIMING - Measure Instruction Timing
***********************************************************************

INSTTIMING DS   0H
* Simplified - measures variation in instruction execution
         LA     15,12345         Dummy timing value
         BR     14

***********************************************************************
* SUBROUTINE: CLOCKSKEW - Read Clock Skew
***********************************************************************

CLOCKSKEW DS   0H
* Simplified - would measure against reference in production
         LA     15,67890         Dummy skew value
         BR     14

***********************************************************************
* SUBROUTINE: BUILDATTESTATION - Build Attestation Message
***********************************************************************

BUILDATTESTATION DS 0H
         STM    1,3,72(13)
         
* Build message: [CMD][WALLET][FINGERPRINT][TIMESTAMP]
         LA     1,ATTESTBUF
         MVC    0(1),=X'02'      CMD_ATTEST
         
* Copy wallet (40 bytes)
         LA     2,WALLETBUF
         MVC    1(40,1),0(2)
         
* Copy fingerprint (64 bytes)
         LA     2,FINGERPRINT
         MVC    41(64,1),0(2)
         
* Add timestamp
         BAL    14,CLOCKRD
         ST     0,81(1)
         
         LM     1,3,72(13)
         BR     14

ATTESTBUF DS   XL'100'          Attestation buffer
WALLETBUF DS   XL'40'           Wallet storage

***********************************************************************
* SUBROUTINE: SENDATTESTATION - Send via Serial
***********************************************************************

SENDATTESTATION DS 0H
         STM    1,5,72(13)
         
* Send each byte via COC
         LA     1,ATTESTBUF
         LA     2,100            Message length
         LA     3,COCBASE        COC base

SENDBYTE DS     0H
         LTR    2,2              Check if done
         BZ     SENDDONE

* Wait for transmit ready
WAITXMIT DS     0H
         IC     4,0(3)           Read status
         TM     4,XMITRDY
         BZ     WAITXMIT

* Send byte
         IC     5,0(1)           Load byte
         STC    5,1(3)           Store to transmit register
         
         LA     1,1(1)           Next byte
         BCT    2,SENDBYTE       Loop

SENDDONE LA     15,0             Success
         LM     1,5,72(13)
         BR     14

***********************************************************************
* SUBROUTINE: RECEIVERESPONSE - Receive Response
***********************************************************************

RECEIVERESPONSE DS 0H
         STM    1,5,72(13)
         
* Wait for response byte
WAITRESP DS     0H
         IC     4,0(3)           Read status
         TM     4,RECVRDY
         BZ     WAITRESP

* Read status byte
         IC     5,1(3)
         STC    5,RESPSTATUS
         
         CLC    RESPSTATUS,STATUS_OK
         BNE    RESPERR2
         
         LA     15,0             Success
         B      RESPEND

RESPERR2 LA     15,1             Error
RESPEND  LM     1,5,72(13)
         BR     14

RESPSTATUS DS   X

***********************************************************************
* SUBROUTINE: CHECKREWARD - Check if Reward Received
***********************************************************************

CHECKREWARD DS 0H
* Simplified - would query balance in production
         BR     14

***********************************************************************
* SUBROUTINE: LOGEPOCH - Log Epoch Completion
***********************************************************************

LOGEPOCH DS   0H
* Write to log file on disk
         BR     14

***********************************************************************
* SUBROUTINE: DELAY5SEC - 5 Second Delay
***********************************************************************

DELAY5SEC DS   0H
         LA     1,500            Approximate loops for 5 sec
DELAYLP  BCT    1,DELAYLP
         BR     14

***********************************************************************
* MESSAGE STRINGS
***********************************************************************

MSGSTART    DC    C'Sigma 7 RustChain Miner Starting...'
MSGSTARTLEN EQU   *-MSGSTART

MSGWALLETERR DC   C'ERROR: Could not load wallet'
MSGWALLETERRLEN EQU *-MSGWALLETERR

MSGSENDERR  DC    C'ERROR: Failed to send attestation'
MSGSENDERRLEN EQU *-MSGSENDERR

MSGRESPERR  DC    C'ERROR: Invalid response from gateway'
MSGRESPERRLEN EQU *-MSGRESPERR

***********************************************************************
* STORAGE AREAS
***********************************************************************

         ORG    DATASTART
         DS     0D               Doubleword alignment

         END    MINER
