/** @file
 * A GameCube controller adapter (Nintendo's for the Wii U and Switch, and
 * the ones that speak its protocol), read straight from the USB device.
 *
 * SDL has a driver for it, but that driver goes through a USB library the
 * 32-bit game process does not have here, and it rescales the sticks. This
 * reads the adapter the way Dolphin does, without a library (the kernel's
 * usbfs), and gives the game the controller's own numbers.
 *
 * The adapter is USB device 057e:0337. A byte 0x13 on its out endpoint
 * starts it reporting; each report is 37 bytes: 0x21, then nine for each
 * of its four ports: a status (0x10 or 0x20: a controller is there), two
 * of buttons, the stick, the C stick and the two triggers as the
 * controller measures them (about 128 at rest, 0 to 255). The console
 * takes what a controller reads when it is first seen as its rest
 * position; so does this.
 *
 * A thread reads reports as they come (the adapter sends up to a thousand
 * a second) and keeps the newest; the game takes that one at each frame
 * boundary. Opening needs the device node to be writable by the user: the
 * udev rule Dolphin asks for. While another program has the adapter
 * (Dolphin), this one cannot, and the other way round.
 */
#ifdef HOST_WINDOW

#include "host.h"

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/usbdevice_fs.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <dolphin/pad.h>

#define REPORT 37

static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static uint8_t latest[REPORT];
static int have; ///< a report has been read since the adapter was opened
static char status[200] = "not looked for";
static int started;

/// What each port's controller read when it was first seen.
static struct Origin {
    int set;
    uint8_t lx, ly, cx, cy, lt, rt;
} origin[4];

static void say(const char* fmt, const char* detail)
{
    pthread_mutex_lock(&lock);
    snprintf(status, sizeof status, fmt, detail);
    pthread_mutex_unlock(&lock);
}

static int read_number(const char* dir, const char* name, int base)
{
    char path[320], text[32] = "";
    FILE* f;

    snprintf(path, sizeof path, "/sys/bus/usb/devices/%s/%s", dir, name);
    f = fopen(path, "r");
    if (f == NULL) {
        return -1;
    }
    if (fgets(text, sizeof text, f) == NULL) {
        text[0] = '\0';
    }
    fclose(f);
    return text[0] != '\0' ? (int) strtol(text, NULL, base) : -1;
}

/// The adapter's device node, if one is plugged in.
static int find(char* path, size_t size)
{
    DIR* d = opendir("/sys/bus/usb/devices");
    struct dirent* e;
    int found = 0;

    if (d == NULL) {
        return 0;
    }
    while (!found && (e = readdir(d)) != NULL) {
        if (read_number(e->d_name, "idVendor", 16) == 0x057e &&
            read_number(e->d_name, "idProduct", 16) == 0x0337)
        {
            snprintf(path, size, "/dev/bus/usb/%03d/%03d",
                     read_number(e->d_name, "busnum", 10),
                     read_number(e->d_name, "devnum", 10));
            found = 1;
        }
    }
    closedir(d);
    return found;
}

static int transfer(int fd, unsigned endpoint, uint8_t* data, unsigned len)
{
    struct usbdevfs_bulktransfer t = { endpoint, len, 100, data };
    return ioctl(fd, USBDEVFS_BULK, &t);
}

static void* reader(void* arg)
{
    (void) arg;
    for (;;) {
        char path[64];
        unsigned interface = 0;
        uint8_t go = 0x13;
        int fd;

        if (!find(path, sizeof path)) {
            say("no adapter is plugged in%s", "");
            sleep(1);
            continue;
        }
        fd = open(path, O_RDWR);
        if (fd < 0) {
            say("the adapter is there but cannot be opened (%s): it needs "
                "the udev rule Dolphin asks for",
                strerror(errno));
            sleep(1);
            continue;
        }
        if (ioctl(fd, USBDEVFS_CLAIMINTERFACE, &interface) < 0) {
            /* a kernel driver may hold it: ask it to let go, once */
            struct usbdevfs_ioctl let_go = { 0, USBDEVFS_DISCONNECT, NULL };
            ioctl(fd, USBDEVFS_IOCTL, &let_go);
            if (ioctl(fd, USBDEVFS_CLAIMINTERFACE, &interface) < 0) {
                say("the adapter is in use by another program (%s)",
                    strerror(errno));
                close(fd);
                sleep(1);
                continue;
            }
        }
        transfer(fd, 0x02, &go, 1);
        say("open%s", "");
        for (;;) {
            uint8_t report[REPORT];
            int n = transfer(fd, 0x81, report, sizeof report);
            if (n == REPORT && report[0] == 0x21) {
                pthread_mutex_lock(&lock);
                memcpy(latest, report, sizeof latest);
                have = 1;
                pthread_mutex_unlock(&lock);
            } else if (n < 0 && errno != ETIMEDOUT) {
                break; /* unplugged */
            }
        }
        pthread_mutex_lock(&lock);
        have = 0;
        pthread_mutex_unlock(&lock);
        ioctl(fd, USBDEVFS_RELEASEINTERFACE, &interface);
        close(fd);
    }
    return NULL;
}

/// Start looking for the adapter (once; it may be plugged in later).
void host_gcc_start(void)
{
    pthread_t thread;

    if (!started) {
        started = 1;
        say("looking%s", "");
        if (pthread_create(&thread, NULL, reader, NULL) == 0) {
            pthread_detach(thread);
        } else {
            say("the reader could not be started%s", "");
        }
    }
}

void host_gcc_forget(void)
{
    memset(origin, 0, sizeof origin);
}

static int8_t from_rest(int value, int rest)
{
    int v = value - rest;
    return (int8_t) (v > 127 ? 127 : v < -128 ? -128 : v);
}

/// One port of a report as the game's pad. 0 if no controller is there.
int host_gcc_decode(const uint8_t* report, int port, HostPad* pad)
{
    static const struct {
        int byte;
        uint8_t from;
        uint16_t to;
    } buttons[] = {
        { 1, 0x01, PAD_BUTTON_A },    { 1, 0x02, PAD_BUTTON_B },
        { 1, 0x04, PAD_BUTTON_X },    { 1, 0x08, PAD_BUTTON_Y },
        { 1, 0x10, PAD_BUTTON_LEFT }, { 1, 0x20, PAD_BUTTON_RIGHT },
        { 1, 0x40, PAD_BUTTON_DOWN }, { 1, 0x80, PAD_BUTTON_UP },
        { 2, 0x01, PAD_BUTTON_START }, { 2, 0x02, PAD_TRIGGER_Z },
        { 2, 0x04, PAD_TRIGGER_R },   { 2, 0x08, PAD_TRIGGER_L },
    };
    const uint8_t* p = report + 1 + (port & 3) * 9;
    struct Origin* o = &origin[port & 3];

    memset(pad, 0, sizeof *pad);
    if (report[0] != 0x21 || !(p[0] & 0x30)) {
        o->set = 0;
        return 0;
    }
    if (!o->set) {
        o->set = 1;
        o->lx = p[3];
        o->ly = p[4];
        o->cx = p[5];
        o->cy = p[6];
        o->lt = p[7];
        o->rt = p[8];
    }
    for (size_t i = 0; i < sizeof buttons / sizeof buttons[0]; i++) {
        if (p[buttons[i].byte] & buttons[i].from) {
            pad->buttons |= buttons[i].to;
        }
    }
    pad->lx = from_rest(p[3], o->lx);
    pad->ly = from_rest(p[4], o->ly);
    pad->cx = from_rest(p[5], o->cx);
    pad->cy = from_rest(p[6], o->cy);
    pad->lt = (uint8_t) (p[7] > o->lt ? p[7] - o->lt : 0);
    pad->rt = (uint8_t) (p[8] > o->rt ? p[8] - o->rt : 0);
    pad->connected = 1;
    return 1;
}

/// The controller on one of the adapter's ports (0 to 3), now. 0 if the
/// adapter is not open or nothing is plugged into that port.
int host_gcc_pad(int port, HostPad* pad)
{
    uint8_t report[REPORT];
    int ok;

    pthread_mutex_lock(&lock);
    ok = have;
    memcpy(report, latest, sizeof report);
    pthread_mutex_unlock(&lock);
    if (!ok) {
        memset(pad, 0, sizeof *pad);
        return 0;
    }
    return host_gcc_decode(report, port, pad);
}

/// The first of the adapter's ports with a controller, or -1.
int host_gcc_first(void)
{
    HostPad pad;

    for (int port = 0; port < 4; port++) {
        if (host_gcc_pad(port, &pad)) {
            return port;
        }
    }
    return -1;
}

/// The adapter's state in words, and which of its ports have controllers.
void host_gcc_status(char* out, size_t size)
{
    char ports[32] = "";
    HostPad pad;

    for (int port = 0; port < 4; port++) {
        if (host_gcc_pad(port, &pad)) {
            snprintf(ports + strlen(ports), sizeof ports - strlen(ports),
                     " %d", port + 1);
        }
    }
    pthread_mutex_lock(&lock);
    snprintf(out, size, "%s%s%s", status,
             ports[0] != '\0' ? ", controllers on its ports" : "", ports);
    pthread_mutex_unlock(&lock);
}

#endif
