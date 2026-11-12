/*
 * The hub: the menu that opens in the character select scene once the
 * player has picked a character and pressed START. It lists that
 * character's course by section (Tech, Neutral, Punish, Defense) plus free
 * practice, with each drill's goal and this session's statistics, and
 * starts the chosen drill. Design: docs/ai/training-courses.md.
 *
 * A css unit ("hubCSS" in src/tmce/units.txt), loaded for the course event
 * through EventDesc.eventCSSFile like TM-CE's labCSS. It borrows that
 * unit's art (camera, panel): files/TM/hubCSS.dat is a copy of labCSS.dat.
 *
 * How it takes over START: the vanilla scene sets its exit state to "start
 * the match" (mnCharSel_804D6CF6 = 1, MexTK's stc_css_exitkind) from its
 * input proc when START is pressed with a character ready, and acts on it
 * in the next frame's scene callback. The hub's proc runs after that input
 * proc, sees the 1, turns it into 5 (the state vanilla uses while a submenu
 * is open) and opens. Confirming a drill writes the 1 back.
 */
#include "course.h"
#include "lab_common.h"
#include <stddef.h>

/* gm/gmevent.h: the event index the event mode runs. */
void gm_801BEB74(u8 event);
/* src/tmce/addcodes_bridge.c */
int tmce_ac_FindEvent(const char* file, int* page, int* event);
void tmce_ac_SetEventPage(int page);

/* stc_css_exitkind values (mnCharSel_804D6CF6 in src/melee/mn/mncharsel.c) */
#define CSS_EXIT_NONE 0
#define CSS_EXIT_START 1
#define CSS_EXIT_BACK 2
#define CSS_EXIT_SUBMENU 5

/* After every proc of the vanilla scene. */
#define HUB_PROC_PRIORITY 20

#define HUB_ROWS 8
enum { HUB_FREE = COURSE_PART_COUNT, HUB_SECTION_COUNT };
enum { FREE_LAB, FREE_EVENTS, FREE_COUNT };

static const char* section_names[HUB_SECTION_COUNT] = {
    "Tech", "Neutral", "Punish", "Defense", "Free Practice",
};
static const char* free_names[FREE_COUNT] = {
    "Training Lab",
    "Training Mode events",
};
static const char* free_goals[FREE_COUNT] = {
    "TM-CE's Lab. The CPU is the last one used there.",
    "The event list: TM-CE's general and character events.",
};

/* TM-CE CSSID bit order (events.h) -> external character id (CKIND_*). */
static const u8 cssid_ckind[25] = {
    CKIND_DRMARIO, CKIND_MARIO, CKIND_LUIGI, CKIND_BOWSER, CKIND_PEACH,
    CKIND_YOSHI, CKIND_DK, CKIND_FALCON, CKIND_GANONDORF, CKIND_FALCO,
    CKIND_FOX, CKIND_NESS, CKIND_ICECLIMBERS, CKIND_KIRBY, CKIND_SAMUS,
    CKIND_ZELDA, CKIND_LINK, CKIND_YOUNGLINK, CKIND_PICHU, CKIND_PIKACHU,
    CKIND_JIGGLYPUFF, CKIND_MEWTWO, CKIND_GAW, CKIND_MARTH, CKIND_ROY,
};

/* By external character id (CKIND_*). */
static const char* ckind_names[26] = {
    "Captain Falcon", "Donkey Kong", "Fox", "Mr. Game & Watch", "Kirby",
    "Bowser", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Ness", "Peach",
    "Pikachu", "Ice Climbers", "Jigglypuff", "Samus", "Yoshi", "Zelda",
    "Sheik", "Falco", "Young Link", "Dr. Mario", "Roy", "Pichu",
    "Ganondorf",
};

static Arch_ImportData* hub_assets;
static GXColor hub_white = { 255, 255, 255, 255 };
static GXColor hub_gold = { 255, 211, 0, 255 };
static GXColor hub_grey = { 150, 150, 150, 255 };

static struct {
    int canvas;
    GOBJ* menu;      /* NULL while closed */
    Text* title;
    Text* list;
    Text* desc;
    int ckind;       /* the player's character while open */
    int rows[HUB_ROWS]; /* drill ids (or FREE_*) of the open section */
    int row_count;
    int fresh;       /* opened this frame: its input is the opening press */
} hub;

static int Hub_SelectedCkind(void)
{
    VSMinorData* scene = *stc_css_minorscene;
    int ck = scene->vs_data.match_init.playerData[*stc_css_hmnport].c_kind;
    return ck < 26 ? ck : -1;
}

static int Hub_CssidMask(int ckind)
{
    int i;
    if (ckind == CKIND_SHEIK) {
        ckind = CKIND_ZELDA;
    }
    for (i = 0; i < 25; i++) {
        if (cssid_ckind[i] == ckind) {
            return 1 << i;
        }
    }
    return 0;
}

static void Hub_BuildRows(void)
{
    int i, mask = Hub_CssidMask(hub.ckind);
    hub.row_count = 0;
    if (Course_HubPart == HUB_FREE) {
        for (i = 0; i < FREE_COUNT; i++) {
            hub.rows[hub.row_count++] = i;
        }
    } else {
        for (i = 0; i < DRILL_COUNT && hub.row_count < HUB_ROWS; i++) {
            const CourseDrillInfo* d = &Course_Drills[i];
            if (d->part == Course_HubPart &&
                (d->characters == 0 || (d->characters & mask) != 0))
            {
                hub.rows[hub.row_count++] = i;
            }
        }
    }
    if (Course_HubCursor >= hub.row_count) {
        Course_HubCursor = hub.row_count > 0 ? hub.row_count - 1 : 0;
    }
    if (Course_HubCursor < 0) {
        Course_HubCursor = 0;
    }
}

static void Hub_Draw(void)
{
    int i;
    Text_SetText(hub.title, 0, "%s  <  %s  >",
                 hub.ckind >= 0 && hub.ckind < (int) countof(ckind_names)
                     ? ckind_names[hub.ckind]
                     : "?",
                 section_names[Course_HubPart]);

    for (i = 0; i < HUB_ROWS; i++) {
        if (i >= hub.row_count) {
            Text_SetText(hub.list, i, i == 0 ? "No drills here yet" : "");
            Text_SetColor(hub.list, i, &hub_grey);
            continue;
        }
        if (Course_HubPart == HUB_FREE) {
            Text_SetText(hub.list, i, "%s", free_names[hub.rows[i]]);
        } else {
            const CourseDrillInfo* d = &Course_Drills[hub.rows[i]];
            const CourseStats* st = &Course_Stats[hub.rows[i]];
            if (st->attempts > 0) {
                Text_SetText(hub.list, i, "%s   %d/%d (%d%%)  best streak %d",
                             d->name, st->successes, st->attempts,
                             st->successes * 100 / st->attempts,
                             st->best_streak);
            } else {
                Text_SetText(hub.list, i, "%s", d->name);
            }
        }
        Text_SetColor(hub.list, i,
                      i == Course_HubCursor ? &hub_gold : &hub_white);
    }

    if (hub.row_count == 0) {
        Text_SetText(hub.desc, 0, "L/R or left/right: section   B: back");
    } else if (Course_HubPart == HUB_FREE) {
        Text_SetText(hub.desc, 0, "%s", free_goals[hub.rows[Course_HubCursor]]);
    } else {
        Text_SetText(hub.desc, 0, "%s",
                     Course_Drills[hub.rows[Course_HubCursor]].goal);
    }
    Text_SetText(hub.desc, 1,
                 "A: start   B: back   left/right: section   up/down: drill");
}

static void Hub_Think(GOBJ* menu_gobj);

static void Hub_Open(void)
{
    GOBJ* menu_gobj = GObj_Create(4, 5, 0);
    JOBJ* menu_jobj = JOBJ_LoadJoint(hub_assets->import_menu);
    JOBJ* child;
    int i;
    static const int hidden_children[] = { 2, 4, 6, 7 };

    GObj_AddGXLink(menu_gobj, GXLink_Common, MENUCAM_GXLINK, 128);
    GObj_AddProc(menu_gobj, Hub_Think, HUB_PROC_PRIORITY);
    GObj_AddObject(menu_gobj, R13_U8(-0x3E55), menu_jobj);
    /* The panel's memory card, screenshot and scroll bar parts (lab_css.c
     * Menu_Create) are not used here. */
    for (i = 0; i < (int) countof(hidden_children); i++) {
        JOBJ_GetChild(menu_jobj, &child, hidden_children[i], -1);
        JOBJ_SetFlagsAll(child, JOBJ_HIDDEN);
    }

    hub.title = Text_CreateText(SIS_ID, hub.canvas);
    hub.title->kerning = 1;
    hub.title->use_aspect = 1;
    hub.title->aspect.X = 600;
    hub.title->trans.X = -28;
    hub.title->trans.Y = -21;
    hub.title->trans.Z = menu_jobj->trans.Z;
    hub.title->viewport_scale.X = (menu_jobj->scale.X * 0.01) * 9;
    hub.title->viewport_scale.Y = (menu_jobj->scale.Y * 0.01) * 9;
    Text_AddSubtext(hub.title, 0, 0, "-");

    hub.list = Text_CreateText(SIS_ID, hub.canvas);
    hub.list->kerning = 1;
    hub.list->use_aspect = 1;
    hub.list->aspect.X = 1100;
    hub.list->trans.X = -27.8;
    hub.list->trans.Y = -13.6;
    hub.list->trans.Z = menu_jobj->trans.Z;
    hub.list->viewport_scale.X = (menu_jobj->scale.X * 0.01) * 5;
    hub.list->viewport_scale.Y = (menu_jobj->scale.Y * 0.01) * 5;
    for (i = 0; i < HUB_ROWS; i++) {
        Text_AddSubtext(hub.list, 0, i * 40, "");
    }

    hub.desc = Text_CreateText(SIS_ID, hub.canvas);
    hub.desc->kerning = 1;
    hub.desc->use_aspect = 1;
    hub.desc->aspect.X = 930;
    hub.desc->trans.X = -28;
    hub.desc->trans.Y = 14.5;
    hub.desc->trans.Z = menu_jobj->trans.Z;
    hub.desc->viewport_scale.X = (menu_jobj->scale.X * 0.01) * 5;
    hub.desc->viewport_scale.Y = (menu_jobj->scale.Y * 0.01) * 5;
    Text_AddSubtext(hub.desc, 0, 0, "-");
    Text_AddSubtext(hub.desc, 0, 80, "");

    hub.menu = menu_gobj;
    hub.fresh = 1;
    if (Hub_SelectedCkind() >= 0) {
        VSMinorData* scene = *stc_css_minorscene;
        Course_HubCkind = Hub_SelectedCkind();
        Course_HubColor =
            scene->vs_data.match_init.playerData[*stc_css_hmnport].costume;
    }
    hub.ckind = Course_HubCkind;
    *stc_css_exitkind = CSS_EXIT_SUBMENU;
    Hub_BuildRows();
    Hub_Draw();
}

/* Close the hub and leave the scene in `exitkind` (CSS_EXIT_NONE: back to
 * picking a character). */
static void Hub_Close(int exitkind)
{
    Text_Destroy(hub.title);
    Text_Destroy(hub.list);
    Text_Destroy(hub.desc);
    hub.title = hub.list = hub.desc = NULL;
    GObj_Destroy(hub.menu);
    hub.menu = NULL;
    *stc_css_exitkind = exitkind;
    *stc_css_delay = exitkind == CSS_EXIT_NONE ? 10 : 0;
    if (exitkind == CSS_EXIT_START) {
        /* Start the match ourselves, with the hub's character. The scene's
         * own check (mnCharSel's exit state 1) refuses while no puck is
         * placed, which is the case when the hub reopened after a drill:
         * this character select does not restore the pick. The scene's
         * exit code only passes the exit state on. */
        VSMinorData* scene = *stc_css_minorscene;
        int port = *stc_css_hmnport;
        Preload* preload = Preload_GetTable();
        scene->vs_data.match_init.playerData[port].c_kind = Course_HubCkind;
        scene->vs_data.match_init.playerData[port].costume = Course_HubColor;
        /* TM-CE's EventInit takes the player's character from the preload
         * request, which the scene only fills when a puck is placed. */
        preload->queued.fighters[0].kind = Course_HubCkind;
        preload->queued.fighters[0].costume = Course_HubColor;
        Scene_ExitMinor();
    }
}

static void Hub_SwitchEvent(const char* file)
{
    int page, event;
    if (tmce_ac_FindEvent(file, &page, &event)) {
        tmce_ac_SetEventPage(page);
        gm_801BEB74(event);
    }
}

static void Hub_Confirm(void)
{
    int row;
    if (hub.row_count == 0) {
        SFX_PlayCommon(3);
        return;
    }
    row = hub.rows[Course_HubCursor];
    SFX_PlayCommon(1);
    if (Course_HubPart != HUB_FREE) {
        Course_Select(row);
        Hub_Close(CSS_EXIT_START);
    } else if (row == FREE_LAB) {
        Hub_SwitchEvent("lab");
        Hub_Close(CSS_EXIT_START);
    } else {
        /* The main menu opens on the event list (boot codes). */
        Hub_Close(CSS_EXIT_BACK);
    }
}

static void Hub_Think(GOBJ* menu_gobj)
{
    int port = *stc_css_hmnport;
    int rapid = Pad_GetRapidHeld(port);
    int down = Pad_GetDown(port);
    int moved = 0;

    *stc_css_delay = 2; /* the scene ignores input while this is not 0 */

    /* A proc added during the proc pass still runs in that pass: the
     * START that opened the hub must not also confirm its first row. */
    if (hub.fresh) {
        hub.fresh = 0;
        return;
    }

    if (down & HSD_BUTTON_B) {
        SFX_PlayCommon(0);
        Hub_Close(CSS_EXIT_NONE);
        return;
    }
    if (down & (HSD_BUTTON_A | HSD_BUTTON_START)) {
        Hub_Confirm();
        return;
    }
    if (rapid & (HSD_BUTTON_LEFT | HSD_BUTTON_DPAD_LEFT | HSD_TRIGGER_L)) {
        Course_HubPart = (Course_HubPart + HUB_SECTION_COUNT - 1) %
                         HUB_SECTION_COUNT;
        Course_HubCursor = 0;
        moved = 1;
    } else if (rapid &
               (HSD_BUTTON_RIGHT | HSD_BUTTON_DPAD_RIGHT | HSD_TRIGGER_R))
    {
        Course_HubPart = (Course_HubPart + 1) % HUB_SECTION_COUNT;
        Course_HubCursor = 0;
        moved = 1;
    } else if (rapid & (HSD_BUTTON_UP | HSD_BUTTON_DPAD_UP)) {
        if (hub.row_count > 0) {
            Course_HubCursor = (Course_HubCursor + hub.row_count - 1) %
                               hub.row_count;
            moved = 1;
        }
    } else if (rapid & (HSD_BUTTON_DOWN | HSD_BUTTON_DPAD_DOWN)) {
        if (hub.row_count > 0) {
            Course_HubCursor = (Course_HubCursor + 1) % hub.row_count;
            moved = 1;
        }
    }
    if (moved) {
        SFX_PlayCommon(2);
        Hub_BuildRows();
        Hub_Draw();
    }
}

/* Runs every frame of the scene, after the scene's own procs. */
static void Hub_Watch(GOBJ* gobj)
{
    if (hub.menu != NULL) {
        return;
    }
    if (*stc_css_exitkind == CSS_EXIT_START && Hub_SelectedCkind() >= 0) {
        /* START with a character ready: the hub instead of the match. */
        Course_HubReturn = 0;
        Hub_Open();
    } else if (Course_HubReturn && *stc_css_exitkind == CSS_EXIT_NONE &&
               *stc_css_delay == 0 && Course_HubCkind >= 0)
    {
        /* Back from a drill: reopen where the player left. */
        Course_HubReturn = 0;
        Hub_Open();
    }
}

void OnCSSLoad(HSD_Archive* archive)
{
    COBJ* cam_cobj;
    GOBJ* cam_gobj;
    GOBJ* watch;

    memset(&hub, 0, sizeof(hub));
    hub_assets = Archive_GetPublicAddress(archive, "labCSS");

    /* Camera and text canvas for the panel, as lab_css.c sets them up. */
    cam_cobj = COBJ_LoadDesc(hub_assets->import_cam);
    cam_gobj = GObj_Create(2, 3, 128);
    GObj_AddObject(cam_gobj, R13_U8(-0x3E55), cam_cobj);
    GOBJ_InitCamera(cam_gobj, CObjThink_Common, 1);
    GObj_AddProc(cam_gobj, MainMenu_CamRotateThink, 5);
    cam_gobj->cobj_links = 1 << MENUCAM_GXLINK;
    hub.canvas = Text_CreateCanvas(SIS_ID, 0, 2, 3, 128, MENUCAM_GXLINK, 129,
                                   0);

    watch = GObj_Create(4, 5, 0);
    GObj_AddProc(watch, Hub_Watch, HUB_PROC_PRIORITY);
}
