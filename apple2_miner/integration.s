; Integration with the Apple II's memory and I/O systems

.org $C000
func:
	lda #\$00
	sta $2000
	jsr $FFD2
	jsr $FFD7
	rts
