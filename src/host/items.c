/** @file
 * Items on demand, for tests: any item put into the match through the
 * game's own spawn path, the items there, and what each fighter has of
 * them.
 *
 *   item KIND X Y [VX VY]   an item of KIND falling from (X, Y), at that
 *                           speed, as the developers' item menu spawns one
 *                           (db_CheckAndSpawnItem): its checks,
 *                           Item_80268B18, the spawn's sparkle. KIND: an
 *                           ItemKind of the common items (the Item
 *                           Switch's, the containers; below 0x23): a
 *                           Pokemon comes out of a Poke Ball (`item
 *                           pokemon`), a fighter's or a stage's items with
 *                           their owner. "ok ID" (ID as `item list` gives
 *                           it)
 *   item list               every item, in the game's item list: JSON, with
 *                           who holds it and who owns it (ports, -1: none)
 *   item fighter P          what player P has of items (held, worn, the
 *                           power-ups' marks; "star": the Starman's
 *                           frames left): JSON
 *   item pokemon KIND       what a Poke Ball lets out from now on: that
 *                           Pokemon (its ItemKind, from 0xA1), as an event
 *                           match sets it (the rules' it_kind, read by
 *                           it_8027AB64); 0: the game's own random choice
 *   item spawns 0|1         random items stop, or go on (the developers'
 *                           switch, db_DisableItemSpawns: it outlasts the
 *                           match, until switched back); what containers
 *                           let out is unchanged
 *   item remove ID          that item gone (Item_8026A8EC), unless a
 *                           fighter holds it
 *
 * Items come only in a match whose rules have them (`vsrules` with a
 * frequency, as the game's Versus): the game loads their data with it.
 */
#include "host.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <melee/db/db.h>
#include <melee/ef/efsync.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/it/forward.h>
#include <melee/it/inlines.h>
#include <melee/it/it_26B1.h>
#include <melee/it/it_3F14.h>
#include <melee/it/item.h>
#include <melee/it/itspawn.h>
#include <melee/it/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>

static char reply[32768];

/// The port whose fighter (or its second, the Ice Climbers' partner) is
/// `gobj`; -1: none.
static int port_of(HSD_GObj* gobj)
{
    if (gobj == NULL) {
        return -1;
    }
    for (int p = 0; p < 6; p++) {
        for (int sub = 0; sub < 2; sub++) {
            HSD_GObj* f = Player_GetEntityAtIndex(p, sub);
            if (f != NULL && f == gobj && host_live_fighter(f)) {
                return p;
            }
        }
    }
    return -1;
}

/// The port of the fighter holding item `gobj`; -1: nobody.
static int holder_of(HSD_GObj* gobj)
{
    for (HSD_GObj* f = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_FIGHTER]; f != NULL;
         f = f->next)
    {
        Fighter* fp = GET_FIGHTER(f);
        if (fp != NULL && fp->item_gobj == gobj) {
            return port_of(f);
        }
    }
    return -1;
}

static int is_item(HSD_GObj* gobj)
{
    for (HSD_GObj* cur = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_ITEM]; cur != NULL;
         cur = cur->next)
    {
        if (cur == gobj) {
            return 1;
        }
    }
    return 0;
}

static int kind_of(HSD_GObj* gobj)
{
    if (gobj == NULL || GET_ITEM(gobj) == NULL) {
        return -1;
    }
    return (int) GET_ITEM(gobj)->kind;
}

/// The developers' item menu (db_CheckAndSpawnItem), with the item, the
/// place and the speed given.
static const char* spawn(int kind, float x, float y, float vx, float vy)
{
    SpawnItem spawn;
    HSD_GObj* gobj;

    memset(&spawn, 0, sizeof spawn);
    spawn.kind = (ItemKind) kind;
    if (!Item_80266F3C() && spawn.kind < It_Kind_Common_End) {
        return "error the match has no items (vsrules with a frequency)";
    }
    spawn.prev_pos.x = x;
    spawn.prev_pos.y = y;
    spawn.prev_pos.z = 0.0F;
    spawn.pos = spawn.prev_pos;
    spawn.facing_dir = it_8026B684(&spawn.prev_pos);
    spawn.x3C_damage = 0;
    spawn.vel.x = vx;
    spawn.vel.y = vy;
    spawn.vel.z = 0.0F;
    spawn.x0_parent_gobj = NULL;
    spawn.x4_parent_gobj2 = spawn.x0_parent_gobj;
    spawn.x44_flag.x0.b0 = 1;
    spawn.x40 = 0;
    if (spawn.kind < It_Kind_Common_End &&
        Item_804A0C64.x0 >= (u32) it_804D6D28->x0)
    {
        return "error too many items (Item Max Over)";
    }
    if (spawn.kind < It_Kind_Monster_End &&
        Item_804A0C64.x2C >= (u32) it_804D6D28->x14)
    {
        return "error too many items (couldn't get Item struct)";
    }
    if (spawn.kind == It_Kind_M_Ball && it_8026C704()) {
        return "error no Poke Ball now (it_8026C704)";
    }
    gobj = Item_80268B18(&spawn);
    if (gobj == NULL) {
        return "error the game made no item";
    }
    efSync_Spawn(0x420, gobj, &spawn.prev_pos);
    snprintf(reply, sizeof reply, "ok %u", (unsigned) (uintptr_t) gobj);
    return reply;
}

static const char* list(void)
{
    int len = snprintf(reply, sizeof reply, "ok [");
    int first = 1;

    for (HSD_GObj* gobj = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_ITEM];
         gobj != NULL && len < (int) sizeof reply - 300; gobj = gobj->next)
    {
        Item* ip = GET_ITEM(gobj);
        if (ip == NULL) {
            continue;
        }
        len += snprintf(
            reply + len, sizeof reply - len,
            "%s{\"id\":%u,\"kind\":%d,\"state\":%d,\"x\":%.6g,\"y\":%.6g,"
            "\"vx\":%.6g,\"vy\":%.6g,\"air\":%d,\"holder\":%d,"
            "\"owner\":%d}",
            first ? "" : ",", (unsigned) (uintptr_t) gobj, (int) ip->kind,
            (int) ip->msid, ip->pos.x, ip->pos.y, ip->x40_vel.x,
            ip->x40_vel.y, ip->ground_or_air == GA_Air ? 1 : 0,
            holder_of(gobj), port_of(ip->owner));
        first = 0;
    }
    snprintf(reply + len, sizeof reply - len, "]");
    return reply;
}

static const char* fighter(int port)
{
    HSD_GObj* gobj = Player_GetEntity(port);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "ok null";
    }
    snprintf(reply, sizeof reply,
             "ok {\"held\":%d,\"hat\":%d,\"metal\":%d,\"cloak\":%d,"
             "\"scale\":%.6g,\"grow\":%d,\"shrink\":%d,\"percent\":%.6g,"
             "\"star\":%d,\"motion\":%d,\"air\":%d,\"x\":%.6g,"
             "\"y\":%.6g}",
             kind_of(fp->item_gobj), kind_of(fp->x197C), (int) fp->is_metal,
             (int) fp->x2226_b4, fp->x34_scale.y, (int) fp->x200C,
             (int) fp->x2010, fp->dmg.x1830_percent,
             fp->x221D_b6 ? (int) fp->x2004 : 0, (int) fp->motion_id,
             (int) fp->ground_or_air, fp->cur_pos.x, fp->cur_pos.y);
    return reply;
}

/// The reply's text after "@ ": "ok ..." or "error ...".
const char* host_item_command(const char* line)
{
    char what[16] = "";
    int n = 0;

    sscanf(line, "%15s%n", what, &n);
    if (strcmp(what, "list") == 0) {
        return list();
    }
    if (strcmp(what, "fighter") == 0) {
        int p = -1;
        if (sscanf(line + n, "%d", &p) != 1 || p < 0 || p >= 6) {
            return "error item fighter P";
        }
        return fighter(p);
    }
    if (strcmp(what, "pokemon") == 0) {
        int kind = -1;
        if (sscanf(line + n, "%i", &kind) != 1 ||
            (kind != 0 && (kind <= It_PKind_Random ||
                           kind >= It_PKind_Terminate)))
        {
            return "error item pokemon KIND (0xA1 on, 0: random)";
        }
        gm_GetStartMeleeRules()->it_kind = (ItemKind) kind;
        return "ok";
    }
    if (strcmp(what, "spawns") == 0) {
        int on = 1;
        sscanf(line + n, "%d", &on);
        if (on) {
            db_EnableItemSpawns();
        } else {
            db_DisableItemSpawns();
        }
        return "ok";
    }
    if (strcmp(what, "remove") == 0) {
        unsigned id = 0;
        HSD_GObj* gobj;
        if (sscanf(line + n, "%u", &id) != 1) {
            return "error item remove ID";
        }
        gobj = (HSD_GObj*) (uintptr_t) id;
        if (!is_item(gobj)) {
            return "error no such item";
        }
        if (holder_of(gobj) >= 0) {
            return "error a fighter holds it";
        }
        Item_8026A8EC(gobj);
        return "ok";
    }
    {
        int kind = -1;
        float x = 0.0F, y = 0.0F, vx = 0.0F, vy = 0.0F;
        int got = sscanf(line, "%i %f %f %f %f", &kind, &x, &y, &vx, &vy);
        if (got != 3 && got != 5) {
            return "error item KIND X Y [VX VY] | list | fighter P | "
                   "pokemon KIND | spawns 0|1 | remove ID";
        }
        if (kind < 0 || kind >= It_Kind_Common_End) {
            return "error not a common item (0 to 0x22)";
        }
        return spawn(kind, x, y, vx, vy);
    }
}
