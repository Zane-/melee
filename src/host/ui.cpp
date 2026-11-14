/** @file
 * The client's interface: RmlUi documents (an HTML-and-CSS-like markup),
 * drawn by Aurora over the whole window, with the game's picture at the
 * left of it (tools/aurora32/aurora-0001-ui-full-window.patch).
 *
 * This file knows nothing about menus. It loads a document from a file and
 * changes it on request; what the screens are and what a button press
 * means is decided by whoever drives the game over the control pipe
 * (tools/melee_client), which also reads the pads ("pads") while the game
 * itself is kept from seeing them ("capture").
 *
 *   ui font PATH            make a font file's faces available
 *   ui load PATH            show this document instead of the current one
 *   ui hide | ui show       the current document
 *   ui class ID NAME 0|1    take a class off an element, or put it on
 *   ui text ID RML...       replace an element's content
 *   ui file ID PATH         the same, the content read from a file
 *   ui attr ID NAME VALUE   set an attribute
 *   ui look ID              how an element is now, as JSON: its classes and
 *                           its own left, top and opacity (for tests)
 *
 * Documents are written for a 1280 by 720 window in `dp` units; the scale
 * follows the window's height.
 *
 * The game fills in one thing itself, each frame: the input display over a
 * match (host_ui_pad, from inputs.c), whose markup the client puts in its
 * match screens (screens.pad_display, ids "cg0i..." and "cg1i...").
 */
#ifdef HOST_WINDOW

#include <RmlUi/Core.h>
#include <aurora/rmlui.hpp>

#include <cstdio>
#include <cstring>
#include <set>
#include <string>

extern "C" {
void host_log(const char* fmt, ...);
void aurora_set_ui_full_window(bool value);
void aurora_set_ui_frame(uint32_t width, uint32_t height);
void aurora_set_game_centered(bool value);
void host_ui_init(int width, int height);
void host_ui_frame(void);
const char* host_ui_command(const char* line);
const char* host_ui_look(const char* line);
int host_ui_pad(int slot, int shown, int port, unsigned held, float sx,
                float sy, float cx, float cy, float ltrig, float rtrig);
}

static Rml::ElementDocument* document;
/* counts the documents loaded: a new one may be where an old one was */
static unsigned document_count;

/// `width` by `height`: the shape the window was made with. The interface
/// and the game's picture keep to a frame of that shape, centred, when the
/// window gets another (fullscreen on a wider screen: black at the sides).
void host_ui_init(int width, int height)
{
    aurora_set_ui_full_window(true);
    aurora_set_ui_frame((uint32_t) width, (uint32_t) height);
    if (aurora::rmlui::get_context() == nullptr) {
        host_log("ui: Aurora has no RmlUi context; menus will not draw");
    }
}

/// Keep a 720-high design filling its frame, whatever the window's size.
void host_ui_frame(void)
{
    static float last;
    Rml::Context* context = aurora::rmlui::get_context();

    if (context != nullptr) {
        float scale = (float) context->GetDimensions().y / 720.0f;
        if (scale > 0.0f && scale != last) {
            aurora::rmlui::set_ui_scale(scale);
            last = scale;
        }
    }
}

static std::string word(const char*& line)
{
    while (*line == ' ') {
        line++;
    }
    const char* start = line;
    while (*line != '\0' && *line != ' ' && *line != '\n') {
        line++;
    }
    return std::string(start, line);
}

static std::string rest(const char* line)
{
    while (*line == ' ') {
        line++;
    }
    std::string out(line);
    while (!out.empty() && (out.back() == '\n' || out.back() == '\r')) {
        out.pop_back();
    }
    return out;
}

/* The input display's sums, as screens.pad_lines does them: a stick's cap
   moves from where it rests, at full tilt, PAD_S_X of the controller's
   box across and PAD_S_Y down (the C-stick's PAD_C_X and PAD_C_Y); a
   trigger's light shows as far as it is in, and it goes PAD_PRESS down
   (padart.TRAVEL and PRESS, in the picture's pixels on its 2072 by 1480
   box). */
#define PAD_S_X (66.0f / 2072 * 100)
#define PAD_S_Y (66.0f / 1480 * 100)
#define PAD_C_X (56.0f / 2072 * 100)
#define PAD_C_Y (56.0f / 1480 * 100)
#define PAD_PRESS 0.0f

/// What a controller of the input display was last given, so that only
/// what changes is set (a part per field: the buttons, the sticks'
/// places, the triggers' in hundredths).
struct PadShown {
    unsigned document; /* document_count when it was set */
    Rml::Element* box; /* "gp0" or "gp1"; NULL: the document has none */
    int shown;
    int port;
    unsigned held;
    int place[6];
};
static PadShown pads_shown[2];

static void pad_set(int slot, const char* part, const char* name,
                    const std::string& value)
{
    char id[32];
    snprintf(id, sizeof id, "cg%di%s", slot, part);
    Rml::Element* e = document->GetElementById(id);
    if (e != nullptr) {
        e->SetProperty(name, value);
    }
}

static std::string percent(float v)
{
    char text[32];
    snprintf(text, sizeof text, "%.2f%%", v);
    return text;
}

static float clamp(float v, float lo, float hi)
{
    return v < lo ? lo : v > hi ? hi : v;
}

/// Controller `slot` (0 or 1) of the input display over a match: shown or
/// not, whose (the port, from 0: its label above START), the buttons held
/// (the pad's bits), the sticks from -1 to 1, the triggers from 0 to 1.
/// Whether the document shown has it (nothing is done if not).
int host_ui_pad(int slot, int shown, int port, unsigned held, float sx,
                float sy, float cx, float cy, float ltrig, float rtrig)
{
    static const struct {
        const char* part;
        unsigned bit;
    } bits[] = {
        { "A", 0x100 }, { "B", 0x200 },  { "X", 0x400 },
        { "Y", 0x800 }, { "Z", 0x10 },   { "ST", 0x1000 },
        { "DU", 0x8 },  { "DD", 0x4 },   { "DL", 0x1 },
        { "DR", 0x2 },
    };
    PadShown* was;
    char id[32];
    int place[6];

    if (document == nullptr || slot < 0 || slot > 1) {
        return 0;
    }
    was = &pads_shown[slot];
    if (was->document != document_count) {
        /* another document: all of it is set again */
        memset(was, 0, sizeof *was);
        was->document = document_count;
        snprintf(id, sizeof id, "gp%d", slot);
        was->box = document->GetElementById(id);
        was->shown = -1;
        was->port = slot; /* the markup's: screens.over_game */
        was->held = ~0u;
        for (int& p : was->place) {
            p = -100000;
        }
    }
    if (was->box == nullptr) {
        return 0; /* no input display in this document */
    }
    if (shown != was->shown) {
        was->box->SetClass("on", shown != 0);
        was->shown = shown;
    }
    if (!shown) {
        return 1;
    }
    if (port != was->port) {
        snprintf(id, sizeof id, "cg%diP", slot);
        Rml::Element* e = document->GetElementById(id);
        if (e != nullptr) {
            char text[16];
            snprintf(text, sizeof text, "pvp p%d", port + 1);
            e->SetClassNames(text);
            snprintf(text, sizeof text, "P%d", port + 1);
            e->SetInnerRML(text);
        }
        was->port = port;
    }
    if (held != was->held) {
        for (const auto& b : bits) {
            if (((held ^ was->held) & b.bit) != 0) {
                snprintf(id, sizeof id, "cg%di%s", slot, b.part);
                Rml::Element* e = document->GetElementById(id);
                if (e != nullptr) {
                    e->SetClass("on", (held & b.bit) != 0);
                }
            }
        }
        was->held = held;
    }
    /* in hundredths of a percent of the box; the triggers in hundredths */
    place[0] = (int) (100.0f * clamp(sx, -1, 1) * PAD_S_X);
    place[1] = (int) (-100.0f * clamp(sy, -1, 1) * PAD_S_Y);
    place[2] = (int) (100.0f * clamp(cx, -1, 1) * PAD_C_X);
    place[3] = (int) (-100.0f * clamp(cy, -1, 1) * PAD_C_Y);
    place[4] = (int) (100.0f * clamp(ltrig, 0, 1));
    place[5] = (int) (100.0f * clamp(rtrig, 0, 1));
    for (int i = 0; i < 2; i++) {
        const char* part = i == 0 ? "S" : "C";
        if (place[2 * i] != was->place[2 * i] ||
            place[2 * i + 1] != was->place[2 * i + 1])
        {
            pad_set(slot, part, "left", percent(place[2 * i] / 100.0f));
            pad_set(slot, part, "top", percent(place[2 * i + 1] / 100.0f));
        }
    }
    for (int i = 0; i < 2; i++) {
        const char* part = i == 0 ? "L" : "R";
        const char* lit = i == 0 ? "Ll" : "Rl";
        int t = place[4 + i];
        if (t != was->place[4 + i]) {
            char op[16];
            pad_set(slot, part, "top", percent(t / 100.0f * PAD_PRESS));
            snprintf(op, sizeof op, "%.2f", t / 100.0f);
            pad_set(slot, lit, "opacity", op);
        }
    }
    memcpy(was->place, place, sizeof place);
    return 1;
}

/// "look ID": the reply (JSON, or "error ..."); NULL for any other command.
const char* host_ui_look(const char* line)
{
    static std::string out;
    std::string verb = word(line);

    if (verb != "look") {
        return nullptr;
    }
    if (document == nullptr) {
        return "error no document is loaded";
    }
    Rml::Element* e = document->GetElementById(word(line));
    if (e == nullptr) {
        return "error no element has that id";
    }
    out = "{\"class\": \"" + e->GetClassNames() + "\"";
    for (const char* name : { "left", "top", "opacity" }) {
        const Rml::Property* p = e->GetLocalProperty(name);
        out += std::string(", \"") + name + "\": \"" +
               (p != nullptr ? p->ToString() : std::string()) + "\"";
    }
    out += "}";
    return out.c_str();
}

/// NULL, or what went wrong.
const char* host_ui_command(const char* line)
{
    Rml::Context* context = aurora::rmlui::get_context();
    std::string verb = word(line);

    if (context == nullptr) {
        return "no interface: Aurora has no RmlUi context";
    }
    if (verb == "font") {
        /* once each: a second client on the same game asks again */
        static std::set<std::string> loaded;
        std::string path = rest(line);
        if (loaded.count(path) != 0) {
            return nullptr;
        }
        if (!Rml::LoadFontFace(path)) {
            return "that font did not load";
        }
        loaded.insert(path);
        return nullptr;
    }
    if (verb == "load") {
        Rml::ElementDocument* next = context->LoadDocument(rest(line));
        if (next == nullptr) {
            return "that document did not load";
        }
        if (document != nullptr) {
            document->Close();
        }
        document = next;
        document_count++;
        document->Show();
        return nullptr;
    }
    if (verb == "center") {
        /* "center 1": the game's picture in the middle of the window's
           frame (the column put away); "center 0": at its left */
        aurora_set_game_centered(word(line) == "1");
        return nullptr;
    }
    if (document == nullptr) {
        return "no document is loaded";
    }
    if (verb == "hide") {
        document->Hide();
        return nullptr;
    }
    if (verb == "show") {
        document->Show();
        return nullptr;
    }
    std::string id = word(line);
    Rml::Element* element = document->GetElementById(id);
    if (element == nullptr) {
        return "no element has that id";
    }
    if (verb == "class") {
        std::string name = word(line);
        element->SetClass(name, rest(line) != "0");
        return nullptr;
    }
    if (verb == "text") {
        element->SetInnerRML(rest(line));
        return nullptr;
    }
    if (verb == "file") {
        /* as "text", from a file: a control line is too short for a list */
        std::string path = rest(line);
        std::string text;
        char buffer[4096];
        size_t n;
        FILE* f = fopen(path.c_str(), "rb");
        if (f == nullptr) {
            return "that file did not open";
        }
        while ((n = fread(buffer, 1, sizeof buffer, f)) > 0) {
            text.append(buffer, n);
        }
        fclose(f);
        element->SetInnerRML(text);
        return nullptr;
    }
    if (verb == "attr") {
        std::string name = word(line);
        element->SetAttribute(name, rest(line));
        return nullptr;
    }
    return "ui: font, load, hide, show, class, text, file or attr";
}

#endif
