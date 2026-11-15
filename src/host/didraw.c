/** @file
 * TM-CE's DI display, for the DI drill (the owner, 2026-11-14: "Let's add
 * full trajectory tracing for the DI drill; training mode has this so we
 * should be able to leverage that code"): src/lab.c's DIDraw_Init,
 * DIDraw_Update, DIDraw_Reset and DIDraw_GX (the Lab's "DI Display"),
 * rewritten against the decomp.
 *
 * For a traced fighter in hitstun, a blue line in the game's world: the
 * launch simulated frame by frame from where the fighter is, ASDI and DI
 * applied as ftCo_Damage_OnExitHitlag would apply them for the stick it
 * holds now, with gravity, the knockback's decay and the stage's floors,
 * walls and ceilings (the game's own collision, mpColl_8004B21C and
 * mpColl_800475F4, on a copy). While the fighter is in hitlag the line is
 * made again every frame for the current stick; when hitlag ends it is kept
 * as it was made on the last frozen frame, the frame whose stick the game
 * read, so the flight can be seen against it; it goes when hitstun ends,
 * on the next hit (made again), or when the trace is turned off. TM-CE
 * makes it again every frame of the flight too, from where the fighter has
 * got to; a line kept whole shows the prediction the stick made.
 *
 * Also TM-CE's SDI display: the fighter's positions through hitlag, a
 * segment for each move, yellow and orange in turn, kept until hitstun
 * ends.
 *
 *   didraw P on|off    trace port P (from 0), or stop
 *   didraw P line      the line drawn now: "line N x y ... sdi N x y ..."
 *
 * The display is a GObj of the match, as the input display's (inputs.c):
 * made at the first frame boundary that has a match and a traced port,
 * found again each frame among the match's GObjs (a state loaded from
 * before it was made leaves nothing dangling), its lines in its user
 * data. It runs after every fighter's procs (priority 23), so it reads the
 * frame's stick, hitlag and knockback, and it draws on GX link 6 as TM-CE's
 * (the match camera's world pass). Its collision copies only read the
 * stage, but they move the game's own collision counters as TM-CE's do: a
 * traced match is not the same game, frame for frame, as an untraced one.
 */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "host.h"
#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <melee/ft/fighter.h>
#include <melee/ft/forward.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/forward.h>
#include <melee/ft/kinds/ftCommon/types.h>
#include <melee/ft/types.h>
#include <melee/lb/lbvector.h>
#include <melee/lb/types.h>
#include <melee/mp/forward.h>
#include <melee/mp/mpcoll.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/cobj.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/pobj.h>
#include <sysdolphin/baselib/state.h>

#define DIDRAW_PORTS 4
#define DIDRAW_GXLINK 6     ///< TM-CE's: drawn by the match camera
#define DIDRAW_GXPRI 0
#define DIDRAW_PROC_PRI 23  ///< after every fighter proc (the last is 22)
/// Frames of the launch simulated at most (TM-CE: as many as the hitstun,
/// allocated each frame; here a fixed line, enough for 640 knockback).
#define DIDRAW_FRAMES 256
/// Frames run through the stage's collision (DI_MaxColl): after them the
/// line goes on without it, as TM-CE's.
#define DIDRAW_MAX_COLL 50
#define DIDRAW_SDI 64       ///< SDI positions kept at most
#define DIDRAW_LINE_WIDTH 31 ///< GFX_Params.size: in sixths of a pixel
#define DIDRAW_RENDER_MODE 0x68000002 ///< GFX_Start's

/// What a traced port's lines are.
typedef struct Trace {
    int num;                         ///< DI line's vertices (0: none)
    Vec2 v[DIDRAW_FRAMES + 2];       ///< ASDI's two, then a frame each
    int sdi_num;                     ///< SDI positions recorded
    Vec2 sdi[DIDRAW_SDI];
} Trace;

typedef struct Display {
    Trace t[DIDRAW_PORTS];
} Display;

/// The ports traced (bit 0 port 1): the player's choice, kept here.
static unsigned mask;

/// The ECB TM-CE simulates with once the fighter's own is no longer locked
/// (DIDraw_Update's ecb_size_def).
static const ftCollisionBox ecb_default = {
    9.0F, 2.5F, { -3.3F, 5.7F }, { 3.3F, 5.7F }
};

static void clear(Trace* t)
{
    t->num = 0;
    t->sdi_num = 0;
}

/// IsHitlagVictim: frozen by a hit taken (allow_sdi is MexTK's
/// flags.hitlag, 0x221A 0x20), in a damage state or shield stun.
static int hitlag_victim(Fighter* fp)
{
    int st = fp->motion_id;
    return fp->allow_sdi &&
           ((ftCo_MS_DamageHi1 <= st && st <= ftCo_MS_DamageFlyRoll) ||
            st == ftCo_MS_GuardSetOff);
}

/// DIDraw_Update's SDI display: the position on each frame of hitlag, a
/// new vertex when it moved; cleared when hitstun ends.
static void sdi_update(Trace* t, Fighter* fp)
{
    if (hitlag_victim(fp)) {
        int n = t->sdi_num;
        Vec2 at;
        if (n >= DIDRAW_SDI) {
            return;
        }
        at.x = fp->cur_pos.x;
        at.y = fp->cur_pos.y;
        t->sdi[n] = at;
        if (n == 0 || at.x != t->sdi[n - 1].x || at.y != t->sdi[n - 1].y) {
            t->sdi_num++;
        }
    } else if (!fp->x221C_b6) {
        t->sdi_num = 0;
    }
}

/// DIDraw_Update's DI display: the launch from here, for the stick held
/// now (the fighter's own, read this frame: what ftCo_Damage_OnExitHitlag
/// would read were this the last frame of hitlag).
static void simulate(Trace* t, Fighter* fp)
{
    ftCommonData* co = p_ftCommonData;
    float lx = fp->input.lstick[0].x;
    float ly = fp->input.lstick[0].y;
    float cx = fp->input.cstick[0].x;
    float cy = fp->input.cstick[0].y;
    Vec3 kb = fp->x8c_kb_vel;
    Vec3 asdi = { 0.0F, 0.0F, 0.0F };
    Vec3 asdi_orig = { 0.0F, 0.0F, 0.0F };
    Vec3 pos;
    float y_vel, decay, frames, terminal;
    int air, n = 0, override = 0;
    CollData ecb;
    ftCollisionBox size;
    Vec2 at[DIDRAW_FRAMES];
    float mid[DIDRAW_FRAMES];

    if (fp->allow_sdi) {
        /* ASDI: the C-stick past sdi_min_stick_mag, else the control
           stick, x4BC units */
        float mag = co->sdi_min_stick_mag * co->sdi_min_stick_mag;
        if (cx * cx + cy * cy >= mag) {
            asdi.x = cx * co->x4BC;
            asdi.y = cy * co->x4BC;
        } else if (lx * lx + ly * ly >= mag) {
            asdi.x = lx * co->x4BC;
            asdi.y = ly * co->x4BC;
        }
        asdi_orig = asdi;
        /* DI (ftCo_8008E5A4): the angle turned toward the stick by x1A8
           degrees times the square of its component perpendicular to the
           launch */
        if (lx != 0.0F || ly != 0.0F) {
            float kb_mult = kb.y * kb.y + kb.x * kb.x;
            if (kb_mult >= 0.00001F) {
                float di = (-kb.x * ly + lx * kb.y);
                float kb_mag = sqrtf(kb_mult);
                float angle = atan2f(kb.y, kb.x);
                Vec3 stick = { lx, ly, 0.0F };
                Vec3 cross;
                di = di * di / kb_mult;
                PSVECCrossProduct(&kb, &stick, &cross);
                if (cross.z < 0.0F) {
                    di = -di;
                }
                angle += MTXDegToRad(co->x1A8) * di;
                kb.x = cosf(angle) * kb_mag;
                kb.y = sinf(angle) * kb_mag;
            }
        }
    }

    air = fp->ground_or_air;
    y_vel = fp->self_vel.y;
    pos = fp->cur_pos;
    decay = co->x204_knockbackFrameDecay;
    frames = fp->mv.co.damage.x0; /* the hitstun left (state var 1) */
    if (!(frames > 0.0F)) {
        frames = 0.0F;
    } else if (frames > DIDRAW_FRAMES) {
        frames = DIDRAW_FRAMES;
    }
    terminal = -fp->co_attrs.terminal_velocity;

    /* Coll_InitECB on a cleared copy (TM-CE's is uninitialised stack,
       which the console tolerates), the fighter's floor contact copied
       when grounded */
    memset(&ecb, 0, sizeof ecb);
    ecb.cur_pos = pos;
    mpColl_80041EE4(&ecb);
    if (air == GA_Ground) {
        memcpy(&ecb.env_flags, &fp->coll_data.env_flags, 0x28);
    }

    for (int i = 0; i < frames; i++) {
        /* the fighter's ECB while its bottom stays locked, else TM-CE's */
        if (n < fp->ecb_lock - fp->dmg.x195c_hitlag_frames) {
            size.top = fp->coll_data.desired_ecb.top.y;
            size.bottom = fp->coll_data.desired_ecb.bottom.y;
            size.left = fp->coll_data.desired_ecb.left;
            size.right = fp->coll_data.desired_ecb.right;
            if (air == GA_Ground) {
                size.bottom = 0.0F;
            }
        } else {
            size = ecb_default;
        }
        ecb.cur_pos = pos;
        ecb.prev_pos = pos;

        /* ASDI on the first frame (its height only in the air) */
        pos.x += asdi.x;
        if (air != GA_Ground) {
            pos.y += asdi.y;
        }
        asdi.x = asdi.y = 0.0F;

        y_vel -= fp->co_attrs.gravity;
        if (y_vel < terminal) {
            y_vel = terminal;
        }
        {
            float angle = atan2f(kb.y, kb.x);
            kb.x -= cosf(angle) * decay;
            kb.y -= sinf(angle) * decay;
        }
        pos.x += kb.x;
        pos.y += kb.y;
        pos.z += kb.z;
        pos.y += y_vel;

        ecb.last_pos = ecb.cur_pos;
        ecb.cur_pos = pos;

        if (n < DIDRAW_MAX_COLL) {
            int env;
            if (air == GA_Ground) {
                if (!mpColl_8004B21C(&ecb, &size)) {
                    air = GA_Air;
                }
            } else {
                mpColl_800475F4(&ecb, &size);
            }
            pos = ecb.cur_pos;
            ecb.x38 += 1; /* the next collision test's ID */
            env = ecb.env_flags;

            if (env & Collide_FloorMask) {
                if (air == GA_Air) {
                    /* landed: the speed along the floor, capped */
                    air = GA_Ground;
                    if (kb.x > co->max_grounded_kb_on_landing) {
                        kb.x = co->max_grounded_kb_on_landing;
                    }
                    if (kb.x < -co->max_grounded_kb_on_landing) {
                        kb.x = -co->max_grounded_kb_on_landing;
                    }
                    kb.x *= ecb.floor.normal.y;
                    kb.y *= ecb.floor.normal.x;
                    y_vel = 0.0F;
                    kb.y = 0.0F;
                }
            } else if (env & Collide_CeilingMask) {
                if (air == GA_Air) {
                    /* bounced off the ceiling, x1BC of it kept */
                    Vec3 vel = { kb.x, kb.y + y_vel, kb.z };
                    lbVector_Mirror(&vel, &ecb.ceiling.normal);
                    kb.x = vel.x * co->x1BC;
                    kb.y = vel.y * co->x1BC;
                }
            } else if (env & Collide_WallMask) {
                if (air == GA_Air) {
                    /* bounced off a wall (the wall on the fighter's left
                       is the one facing right) */
                    Vec3* normal = (env & Collide_RightWallMask)
                                       ? &ecb.right_facing_wall.normal
                                       : &ecb.left_facing_wall.normal;
                    Vec3 vel = { kb.x, kb.y + y_vel, kb.z };
                    lbVector_Mirror(&vel, normal);
                    kb.x = vel.x * co->x1BC;
                    kb.y = vel.y * co->x1BC;
                    y_vel = 0.0F;
                }
            }
            /* slid off an edge: 5 frames more, then the line stops */
            if (!(env & Collide_FloorMask) &&
                (ecb.prev_env_flags & Collide_FloorMask))
            {
                if (override == 0) {
                    override = 5;
                }
            }
        }

        at[n].x = pos.x;
        at[n].y = pos.y;
        mid[n] = (size.left.y + size.top) / 2.0F;
        n++;
        if (override > 0 && --override == 0) {
            break;
        }
    }

    /* ASDI's two vertices first, at the ECB's side height, then the
       middle of the body on each frame */
    t->v[0].x = fp->coll_data.cur_pos.x;
    t->v[0].y = fp->coll_data.cur_pos.y + fp->coll_data.desired_ecb.left.y;
    t->v[1].x = t->v[0].x + asdi_orig.x;
    t->v[1].y = t->v[0].y + asdi_orig.y;
    for (int i = 0; i < n; i++) {
        t->v[i + 2].x = at[i].x;
        t->v[i + 2].y = at[i].y + mid[i];
    }
    t->num = n + 2;
}

static void di_update(Trace* t, Fighter* fp)
{
    if (!fp->x221C_b6) {
        /* not in hitstun (MexTK flags.hitstun, 0x221C 0x02): no line */
        t->num = 0;
    } else if (fp->allow_sdi || t->num == 0) {
        /* in hitlag (or the first frame of a hitstun without it: a
           throw): made again for the stick held now */
        simulate(t, fp);
    }
    /* else: the flight, the line kept as the last frame of hitlag made it */
}

static void think(HSD_GObj* gobj)
{
    Display* d = gobj->user_data;
    for (int port = 0; port < DIDRAW_PORTS; port++) {
        Trace* t = &d->t[port];
        HSD_GObj* g = Player_GetEntity(port);
        Fighter* fp;
        if (!(mask & (1U << port)) || g == NULL || !host_live_fighter(g) ||
            (fp = GET_FIGHTER(g)) == NULL)
        {
            clear(t);
            continue;
        }
        sdi_update(t, fp);
        di_update(t, fp);
    }
}

/// GFX_Start (TM-CE's events.c, after the game's 80391A04): position and
/// colour given directly, in the world through the current camera.
static void gfx_start(u8 shape, u16 count)
{
    Mtx mtx;
    HSD_ClearVtxDesc();
    GXSetCurrentMtx(0);
    HSD_CObjGetViewingMtx(HSD_CObjGetCurrent(), mtx);
    GXLoadPosMtxImm(mtx, 0);
    HSD_StateSetLineWidth(DIDRAW_LINE_WIDTH, 5);
    HSD_StateSetPointSize(DIDRAW_LINE_WIDTH, 5);
    HSD_SetupRenderMode(DIDRAW_RENDER_MODE);
    GXSetVtxAttrFmt(GX_VTXFMT0, GX_VA_POS, GX_POS_XYZ, GX_F32, 0);
    GXSetVtxAttrFmt(GX_VTXFMT0, GX_VA_CLR0, GX_CLR_RGBA, GX_RGBA8, 0);
    GXSetVtxDesc(GX_VA_POS, GX_DIRECT);
    GXSetVtxDesc(GX_VA_CLR0, GX_DIRECT);
    HSD_StateSetCullMode(GX_CULL_NONE);
    GXBegin(shape, GX_VTXFMT0, count);
}

static void vtx(Vec2 p, u8 r, u8 g, u8 b)
{
    GXPosition3f32(p.x, p.y, 0.0F);
    GXColor4u8(r, g, b, 0xFF);
}

/// DIDraw_GX: the SDI path, its segments yellow and orange in turn, and
/// the DI line in blue.
static void draw(HSD_GObj* gobj, intptr_t code)
{
    Display* d = gobj->user_data;
    (void) code; /* every pass, as TM-CE's */
    for (int port = 0; port < DIDRAW_PORTS; port++) {
        Trace* t = &d->t[port];
        if (!(mask & (1U << port))) {
            continue;
        }
        if (t->sdi_num > 1) {
            int n = t->sdi_num;
            gfx_start(GX_LINESTRIP, (u16) (n + n - 2));
            for (int k = 1; k < n; k++) {
                int orange = !(k & 1);
                u8 g = orange ? 0xA5 : 0xFF;
                vtx(t->sdi[k - 1], 0xFF, g, 0x00);
                vtx(t->sdi[k], 0xFF, g, 0x00);
            }
            GXEnd();
        }
        if (t->num > 0) {
            gfx_start(GX_LINESTRIP, (u16) t->num);
            for (int k = 0; k < t->num; k++) {
                vtx(t->v[k], 0x00, 0x8A, 0xFF);
            }
            GXEnd();
        }
    }
}

/// Its user data's remove function, which also marks it as the display.
static void gone(void* data)
{
    HSD_Free(data);
}

/// The display among the match's GObjs, the first if a load brought back
/// more than one (the others are freed); NULL if there is none.
static HSD_GObj* find(void)
{
    HSD_GObj* found = NULL;
    HSD_GObj* g = HSD_GObjPLinkHead[0];
    while (g != NULL) {
        HSD_GObj* next = g->next;
        if (g->user_data_remove_func == gone) {
            if (found == NULL) {
                found = g;
            } else {
                HSD_GObjFree(g);
            }
        }
        g = next;
    }
    return found;
}

/// DIDraw_Init: the display's GObj, its lines empty.
static void make(void)
{
    Display* d = HSD_MemAlloc(sizeof *d);
    HSD_GObj* gobj;
    memset(d, 0, sizeof *d);
    gobj = GObj_Create(0, 0, 0);
    GObj_InitUserData(gobj, 4, gone, d);
    HSD_GObj_SetupProc(gobj, (HSD_GObjEvent) think, DIDRAW_PROC_PRI);
    GObj_SetupGXLink(gobj, draw, DIDRAW_GXLINK, DIDRAW_GXPRI);
}

/// At each frame boundary: the display made if a port is traced, the match
/// is on and it is not there yet.
void host_didraw_frame(void)
{
    if (mask != 0 && Player_GetEntity(0) != NULL && find() == NULL) {
        make();
    }
}

/// "didraw P line": the DI line drawn now for port P, "line N x y x y ...",
/// then "sdi N x y ..." (for tests: the drawing itself is only seen).
static const char* reply_line(int port)
{
    static char out[8192];
    HSD_GObj* gobj = Player_GetEntity(0) != NULL ? find() : NULL;
    Trace* t;
    size_t len;
    if (gobj == NULL) {
        return "line 0 sdi 0";
    }
    t = &((Display*) gobj->user_data)->t[port];
    len = (size_t) snprintf(out, sizeof out, "line %d", t->num);
    for (int k = 0; k < t->num && len + 32 < sizeof out; k++) {
        len += (size_t) snprintf(out + len, sizeof out - len, " %.3f %.3f",
                                 t->v[k].x, t->v[k].y);
    }
    len += (size_t) snprintf(out + len, sizeof out - len, " sdi %d",
                             t->sdi_num);
    for (int k = 0; k < t->sdi_num && len + 32 < sizeof out; k++) {
        len += (size_t) snprintf(out + len, sizeof out - len, " %.3f %.3f",
                                 t->sdi[k].x, t->sdi[k].y);
    }
    return out;
}

const char* host_didraw_command(const char* line)
{
    int port = -1;
    char how[8] = "";
    HSD_GObj* gobj;
    if (sscanf(line, "%d %7s", &port, how) != 2 || port < 0 ||
        port >= DIDRAW_PORTS ||
        (strcmp(how, "on") != 0 && strcmp(how, "off") != 0 &&
         strcmp(how, "line") != 0))
    {
        return "error didraw P on|off|line: P from 0 to 3";
    }
    if (strcmp(how, "line") == 0) {
        return reply_line(port);
    }
    if (strcmp(how, "on") == 0) {
        mask |= 1U << port;
    } else {
        mask &= ~(1U << port);
    }
    /* DIDraw_Reset: what the port had drawn goes either way */
    gobj = Player_GetEntity(0) != NULL ? find() : NULL;
    if (gobj != NULL) {
        clear(&((Display*) gobj->user_data)->t[port]);
    }
    host_didraw_frame();
    return "ok";
}
