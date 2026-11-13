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
 *
 * Documents are written for a 1280 by 720 window in `dp` units; the scale
 * follows the window's height.
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
void host_ui_init(void);
void host_ui_frame(void);
const char* host_ui_command(const char* line);
}

static Rml::ElementDocument* document;

void host_ui_init(void)
{
    aurora_set_ui_full_window(true);
    if (aurora::rmlui::get_context() == nullptr) {
        host_log("ui: Aurora has no RmlUi context; menus will not draw");
    }
}

/// Keep a 720-high design filling the window, whatever its size.
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
        document->Show();
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
