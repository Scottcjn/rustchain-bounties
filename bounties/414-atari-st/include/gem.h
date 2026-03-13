/*
 * gem.h - GEM (Graphics Environment Manager) Bindings
 * 
 * Atari ST GEM AES and VDI function bindings
 * Reference: http://dev-docs.org/atari/
 */

#ifndef _GEM_H
#define _GEM_H

#include <stdint.h>

/* GEM AES Global Array (at $0048A) */
typedef struct {
    int *gl_apid;      /* Application ID array */
    int gl_sysid;      /* System application ID */
    int gl_rlen;       /* Record length */
    int gl_wlen;       /* Word length */
    int *gl_radr;      /* Record address */
    int *gl_wadr;      /* Word address */
    int gl_bcdes;      /* Buffer control descriptor */
    int *gl_bvadr;     /* Buffer virtual address */
    int *gl_bpadr;     /* Buffer physical address */
    int gl_bsize;      /* Buffer size */
} AES_GLOBAL;

/* GEM OBJECT structure */
typedef struct object {
    int16_t ob_next;      /* Next object index */
    int16_t ob_head;      /* Head of sibling list */
    int16_t ob_tail;      /* Tail of sibling list */
    uint16_t ob_type;     /* Object type */
    uint16_t ob_flags;    /* Object flags */
    uint16_t ob_state;    /* Object state */
    void *ob_spec;        /* Object specification */
    int16_t ob_x;         /* X position */
    int16_t ob_y;         /* Y position */
    int16_t ob_width;     /* Width */
    int16_t ob_height;    /* Height */
} OBJECT;

/* Object types */
#define G_BOX       0
#define G_TEXT      1
#define G_BOXTEXT   2
#define G_IMAGE     3
#define G_USERDEF   4
#define G_IBOX      5
#define G_BUTTON    6
#define G_BOXCHAR   7
#define G_STRING    8
#define G_FTEXT     9
#define G_FBOXTEXT  10
#define G_ICON      11
#define G_TITLE     12
#define G_CICON     13

/* Object flags */
#define OF_NONE         0x0000
#define OF_SELECTABLE   0x0001
#define OF_DEFAULT      0x0002
#define OF_EXIT         0x0004
#define OF_EDITABLE     0x0008
#define OF_RBUTTON      0x0010
#define OF_LASTOB       0x0020
#define OF_TOUCHEXIT    0x0040
#define OF_HIDETREE     0x0080
#define OF_INDIRECT     0x0100

/* Object states */
#define OS_NORMAL       0x0000
#define OS_SELECTED     0x0001
#define OS_CROSSED      0x0002
#define OS_CHECKED      0x0004
#define OS_DISABLED     0x0008
#define OS_OUTLINED     0x0010
#define OS_SHADOWED     0x0020
#define OS_WHITEOUT     0x0040

/* Global AES variable pointer */
extern AES_GLOBAL *aes_global;

/* Application ID */
extern int _app_id;

/* Message buffer (16 words) */
extern int msg_buf[16];

/* Function prototypes */

/* AES Functions */
int appl_init(void);
int appl_exit(void);
int appl_find(const char *name);
int appl_tplay(void *addr, int num, int scale);
int appl_trecord(void *addr, int count);

int evnt_keybd(void);
int evnt_button(int clicks, int mask, int state, int *mx, int *my, int *mb, int *ks);
int evnt_mouse(int flags, int x, int y, int width, int height,
               int *mx, int *my, int *mb, int *ks);
int evnt_mesag(int *msg);
int evnt_timer(int tlow, int thigh);
int evnt_multi(int flags, int bclick, int bmask, int bstate,
               int mclick, int mmask, int mstate,
               int tlow, int thigh,
               int *msg, int *mx, int *my);

int form_center(OBJECT *tree, int *x, int *y);
int form_dial(int flag, int x, int y, int w, int h,
              int x2, int y2, int w2, int h2);
int form_alert(int default_button, const char *alert_string);
int form_do(OBJECT *tree, int start_obj);
int form_error(int error_code);

int menu_bar(OBJECT *tree, int show);
int menu_icheck(OBJECT *tree, int item, int check);
int menu_ienable(OBJECT *tree, int item, int enable);
int menu_tnormal(OBJECT *tree, int title, int normal);
int menu_text(OBJECT *tree, int item, const char *text);

int objc_add(OBJECT *tree, int parent, int child);
int objc_change(OBJECT *tree, int obj, int reserved,
                int x, int y, int w, int h, int new_state, int redraw);
int objc_delete(OBJECT *tree, int obj);
int objc_draw(OBJECT *tree, int start_obj, int depth,
              int xclip, int yclip, int wclip, int hclip);
int objc_edit(OBJECT *tree, int obj, int in_char,
              int *idx, int kind);
int objc_offset(OBJECT *tree, int obj, int *x, int *y);
int objc_order(OBJECT *tree, int obj, int new_pos);

int rsrc_free(void);
int rsrc_gaddr(int type, int index, void *addr);
int rsrc_load(const char *filename);
int rsrc_read(void *addr);
int rsrc_write(void *addr);

int shel_envrn(void **value, const char *key);
int shel_find(void *path);
int shel_get(void *addr, int len);
int shel_help(int key, const char *file, const char *title);
int shel_put(void *addr, int len);
int shel_read(char *cmdline, char *ladr);
int shel_write(int mode, int wisgr, int wiscr, char *cmd, char *ladr);
int shel_write0(int mode, int wisgr, int wiscr, const char *cmd, const char *ladr);

/* VDI Constants */
#define HANDLE_SCREEN   0

/* VDI Work In Array */
#define CONTRAST        0
#define BRIGHTNESS      1
#define HORIZONTAL_SIZE 2
#define VERTICAL_SIZE   3
#define HORIZONTAL_HOLD 4
#define VERTICAL_HOLD   5

/* Colors */
#define WHITE           0
#define BLACK           1
#define RED             2
#define GREEN           3
#define BLUE            4
#define CYAN            5
#define YELLOW          6
#define MAGENTA         7

/* Writing modes */
#define MD_REPLACE      1
#define MD_TRANS        2
#define MD_XOR          3
#define MD_ERASE        4

/* Line types */
#define LT_SOLID        1
#define LT_LONGDASH     2
#define LT_DOTTED       3
#define LT_DASHDOT      4
#define LT_DASHDOTDOT   5

/* Marker types */
#define MT_DOT          1
#define MT_PLUS         2
#define MT_ASTERISK     3
#define MT_SQUARE       4
#define MT_DIAMOND      5

/* Interior styles */
#define IS_HOLLOW       0
#define IS_SOLID        1
#define IS_PATTERN      2
#define IS_HATCH        3
#define IS_USER         4

/* Font types */
#define FT_DEFAULT      0
#define FT_BITMAP       1
#define FT_OUTLINE      2
#define FT_DEVICE       3

/* Text alignment */
#define TA_LEFT         0
#define TA_RIGHT        1
#define TA_CENTER       2
#define TA_BASELINE     0
#define TA_TOP          1
#define TA_HALF         2
#define TA_BOTTOM       3

/* Graphics primitives */
void v_pline(int handle, int count, int *xyarray);
void v_pmarker(int handle, int x, int y, int symbol);
void v_gtext(int handle, int x, int y, const char *text);
void v_fillarea(int handle, int count, int *xyarray);
void v_ellarc(int handle, int x, int y, int xradius, int yradius,
              int begang, int endang);
void v_ellpie(int handle, int x, int y, int xradius, int yradius,
              int begang, int endang);
void v_rbox(int handle, int x1, int y1, int x2, int y2);
void v_rfbox(int handle, int x1, int y1, int x2, int y2);
void v_bar(int handle, int x1, int y1, int x2, int y2);

/* Attribute setters */
void vsl_type(int handle, int type);
void vsl_udsty(int handle, int pattern);
void vsl_width(int handle, int width);
void vsl_color(int handle, int color);
void vsm_type(int handle, int type);
void vsm_height(int handle, int height);
void vsm_color(int handle, int color);
void vsf_interior(int handle, int style);
void vsf_style(int handle, int style_index);
void vsf_color(int handle, int color);
void vst_height(int handle, int height, int *char_width, int *char_height,
                int *cell_width, int *cell_height);
void vst_point(int handle, int point, int *char_width, int *char_height,
               int *cell_width, int *cell_height);
void vst_font(int handle, int font);
void vst_color(int handle, int color);
void vst_rotation(int handle, int angle);
void vst_alignment(int handle, int hor_in, int vert_in,
                   int *hor_out, int *vert_out);

/* Inquiry functions */
void vq_color(int handle, int color_index, int set_flag, int *rgb);
void vq_extnd(int handle, int owner, int *work_out);
void vqin_mode(int handle, int *mode);
void vql_attributes(int handle, int *attrib);
void vqm_attributes(int handle, int *attrib);
void vqf_attributes(int handle, int *attrib);
void vqt_attributes(int handle, int *attrib);
void vqf_cell(int handle, int row, int col, int *value);
void vqf_rows(int handle, int *rows, int *columns);

/* Initialization */
void v_opnwk(int *work_in, int *handle, int *work_out);
void v_clswk(int handle);
void v_opnvwk(int *work_in, int *handle, int *work_out);
void v_clsvwk(int handle);

#endif /* _GEM_H */
