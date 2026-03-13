MINER.RSH - GEM Resource File Header
;
; RustChain Miner for Atari ST
; Bounty #414
;
; This is a placeholder for the GEM resource file
; In real implementation, use Resource Construction Set (RCS)
; to create the actual .RSC file
;

; Menu bar indices
FILEMENU    = 0
STARTITEM   = 0
STOPITEM    = 1
QUITITEM    = 2

INFOMENU    = 1
STATUSITEM  = 0
HARDWAREITEM = 1

OPTIONSMENU = 2
NETWORKITEM = 0
SETTINGSITEM = 1

HELPMENU    = 3
ABOUTITEM   = 0

; Dialog box indices
STATUSBOX   = 0
TITLETXT    = 0
STATUSTXT   = 1
EPOCHTXT    = 2
REWARDTXT   = 3
OKBTN       = 4

HARDWAREBOX = 1
HW_TITLE    = 0
HW_CPU      = 1
HW_RAM      = 2
HW_FP       = 3
HW_CLOSE    = 4

ABOUTBOX    = 2
AB_TITLE    = 0
AB_TEXT1    = 1
AB_TEXT2    = 2
AB_TEXT3    = 3
AB_OK       = 4

; Object flags
OF_NONE         = 0x0000
OF_SELECTABLE   = 0x0001
OF_DEFAULT      = 0x0002
OF_EXIT         = 0x0004
OF_EDITABLE     = 0x0008
OF_RBUTTON      = 0x0010
OF_LASTOB       = 0x0020
OF_TOUCHEXIT    = 0x0040
OF_HIDETREE     = 0x0080
OF_INDIRECT     = 0x0100

; Object states
OS_NORMAL       = 0x0000
OS_SELECTED     = 0x0001
OS_CROSSED      = 0x0002
OS_CHECKED      = 0x0004
OS_DISABLED     = 0x0008
OS_OUTLINED     = 0x0010
OS_SHADOWED     = 0x0020
OS_WHITEOUT     = 0x0040

; Object types
G_BOX       = 0
G_TEXT      = 1
G_BOXTEXT   = 2
G_IMAGE     = 3
G_USERDEF   = 4
G_IBOX      = 5
G_BUTTON    = 6
G_BOXCHAR   = 7
G_STRING    = 8
G_FTEXT     = 9
G_FBOXTEXT  = 10
G_ICON      = 11
G_TITLE     = 12
G_CICON     = 13
