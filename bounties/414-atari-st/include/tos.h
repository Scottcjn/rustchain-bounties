/*
 * tos.h - TOS (Tramiel Operating System) Function Bindings
 * 
 * Atari ST TOS function calls and data structures
 * Reference: http://toshyp.atari.org/
 */

#ifndef _TOS_H
#define _TOS_H

#include <stdint.h>

/* TOS Base Pointer (at $000004) */
typedef struct {
    void *oss_conf;      /* OSS configuration */
    void *oss_memory;    /* Memory configuration */
    void *hw_version;    /* Hardware version */
    void *reserved1;
    void *memvalid;      /* Memory validation */
    void *cart;          /* Cartridge base */
    void *reseth;        /* Reset handler */
    void *reserved2[5];
    void *memtop;        /* Top of RAM */
    void *membot;        /* Bottom of RAM */
    void *shido;         /* Screen pointer */
    void *reserved3[2];
    void *phystop;       /* Physical memory top */
    void *reserved4[3];
    void *memvalid2;     /* Memory validation */
    void *etv_critic;    /* Critical error handler */
    void *etv_timer;     /* Timer D handler */
    void *etv_vsync;     /* VBL handler */
    void *etv_cconin;    /* Console input handler */
    void *etv_cconout;   /* Console output handler */
    void *etv_cconws;    /* Console write string handler */
    void *etv_term;      /* Terminal handler */
    void *reserved5[10];
    void *hdv_init;      /* Hard disk init */
    void *hdv_bpb;       /* Hard disk BPB */
    void *hdv_rw;        /* Hard disk read/write */
    void *hdv_boot;      /* Hard disk boot */
    void *hdv_mediach;   /* Hard disk media change */
} TOS_BASE;

/* Global TOS base pointer */
extern TOS_BASE *_SysBase;

/* Memory functions */
extern void *Malloc(long size);
extern void Mfree(void *block);

/* Console I/O */
extern int Cconin(void);
extern int Cconout(int c);
extern int Cconws(const char *str);
extern int Cconrs(char *buf);

/* Date/Time */
extern long Tgetdate(void);
extern long Tsetdate(long date);
extern long Tgettime(void);
extern long Tsettime(long time);

/* Screen functions */
extern void Setscreen(void *logscreen, void *physcreen, void *colortable);
extern void *Getscreen(void);

/* File I/O */
extern int Fopen(const char *filename, int mode);
extern int Fclose(int fd);
extern int Fread(int fd, int count, void *buf);
extern int Fwrite(int fd, int count, const void *buf);
extern int Fseek(int offset, int fd, int mode);
extern int Fdelete(const char *filename);
extern int Frename(int old_handle, const char *old_name, const char *new_name);

/* GEM AES functions (via trap) */
extern int appl_init(void);
extern int appl_exit(void);
extern int evnt_multi(int flags, int bclick, int bmask, int bstate,
                      int mclick, int mmask, int mstate,
                      int tlow, int thigh,
                      int *msg, int *mx, int *my);
extern int form_alert(int default_button, const char *alert_string);
extern int menu_bar(OBJECT *tree, int show);
extern int objc_draw(OBJECT *tree, int start_obj, int depth,
                     int xclip, int yclip, int wclip, int hclip);
extern int objc_offset(OBJECT *tree, int obj, int *x, int *y);

/* GEM VDI functions (via trap) */
extern void v_opnwk(int *work_in, int *handle, int *work_out);
extern void v_clswk(int handle);
extern void v_pline(int handle, int count, int *xyarray);
extern void v_gtext(int handle, int x, int y, const char *text);

/* Hardware access */
#define MFP_BASE      0x00FFFA00
#define STLINK_BASE   0x00FF8000
#define SHIFTER_BASE  0x00FF8200
#define YM_BASE       0x00FF8800

/* Error codes */
#define E_OK          0
#define E_ERROR      -1
#define E_NOMEM      -2
#define E_NOFILE     -3
#define E_NOHANDLER  -4

/* File modes */
#define FO_READ       0
#define FO_WRITE      1
#define FO_RDWR       2

/* Seek modes */
#define SEEK_SET      0
#define SEEK_CUR      1
#define SEEK_END      2

/* GEM message types */
#define MN_SELECTED   10
#define WM_CLOSED     20
#define WM_REDRAW     20
#define WM_TOPPED     21
#define WM_BOTTOMED   22
#define WM_FULLED     23
#define WM_ARROWED    24
#define WM_HSLID      25
#define WM_VSLID      26
#define WM_SIZED      27
#define WM_MOVED      28

/* Event masks */
#define MU_MESAG      0x0001
#define MU_TIMER      0x0010
#define MU_KEYBD      0x0020
#define MU_BUTTON     0x0040
#define MU_M1         0x0080
#define MU_M2         0x0100

/* Macros */
#define Pterm0()      __asm__ volatile ("moveq #0,d0; trap #1")
#define Ptermret(x)   __asm__ volatile ("move.l %0,d0; trap #1" :: "r"(x))

#endif /* _TOS_H */
