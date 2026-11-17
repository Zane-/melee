/* Windows: the GameCube controller adapter (USB 057e:0337, "Wii U mode")
   over WinUSB, for gcadapter.c's reader. The same device Dolphin reads, and
   the same setup: Zadig gives the adapter the WinUSB driver once. While
   another program (Dolphin) has it open, this cannot, and the other way
   round.

   The adapter is found as libusb finds it: among the devices that offer
   the generic USB device interface (GUID_DEVINTERFACE_USB_DEVICE), by
   vendor and product in its path. It has one interface, so WinUSB is the
   device's own driver and that path can be opened directly.

   Kept apart from gcadapter.c so that windows.h (its macros) stays out of
   the files that include the game's headers. */

#include <initguid.h>

#include <windows.h>
#include <setupapi.h>
#include <usbiodef.h>
#include <winusb.h>

#include <stdint.h>
#include <stdio.h>
#include <wchar.h>

static HANDLE device = INVALID_HANDLE_VALUE;
static WINUSB_INTERFACE_HANDLE usb;

/* The adapter's endpoints: reports come in on 0x81, commands go out on
   0x02 (gcadapter.c's header says what they hold). */
#define EP_IN 0x81
#define EP_OUT 0x02
#define TIMEOUT_MS 100

/// The adapter's device path, or 0 if none is plugged in.
static int find(wchar_t* path, size_t size)
{
    HDEVINFO set = SetupDiGetClassDevsW(&GUID_DEVINTERFACE_USB_DEVICE, NULL,
                                        NULL,
                                        DIGCF_PRESENT | DIGCF_DEVICEINTERFACE);
    SP_DEVICE_INTERFACE_DATA iface;
    int found = 0;

    if (set == INVALID_HANDLE_VALUE) {
        return 0;
    }
    iface.cbSize = sizeof iface;
    for (DWORD i = 0; !found && SetupDiEnumDeviceInterfaces(
                                    set, NULL, &GUID_DEVINTERFACE_USB_DEVICE,
                                    i, &iface);
         i++)
    {
        union {
            SP_DEVICE_INTERFACE_DETAIL_DATA_W detail;
            char room[sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W) + 1024];
        } u;
        wchar_t lower[512];

        u.detail.cbSize = sizeof u.detail;
        if (!SetupDiGetDeviceInterfaceDetailW(set, &iface, &u.detail,
                                              sizeof u, NULL, NULL))
        {
            continue;
        }
        wcsncpy(lower, u.detail.DevicePath, 511);
        lower[511] = L'\0';
        _wcslwr(lower);
        if (wcsstr(lower, L"vid_057e&pid_0337") != NULL) {
            wcsncpy(path, u.detail.DevicePath, size - 1);
            path[size - 1] = L'\0';
            found = 1;
        }
    }
    SetupDiDestroyDeviceInfoList(set);
    return found;
}

/// Open the adapter. 1 if open; else 0, with why in `why`: 'n' none
/// plugged in, 'b' busy (another program has it), 'd' not on WinUSB (Zadig
/// has not been run for it), 'o' another failure.
int host_win32_gcc_open(char* why)
{
    wchar_t path[1024];
    ULONG ms = TIMEOUT_MS;
    DWORD err;

    *why = 'o';
    if (!find(path, sizeof path / sizeof path[0])) {
        *why = 'n';
        return 0;
    }
    device = CreateFileW(path, GENERIC_READ | GENERIC_WRITE,
                         FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                         OPEN_EXISTING,
                         FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED, NULL);
    if (device == INVALID_HANDLE_VALUE) {
        err = GetLastError();
        *why = err == ERROR_ACCESS_DENIED || err == ERROR_SHARING_VIOLATION
                   ? 'b'
                   : 'd';
        return 0;
    }
    if (!WinUsb_Initialize(device, &usb)) {
        err = GetLastError();
        CloseHandle(device);
        device = INVALID_HANDLE_VALUE;
        *why = err == ERROR_ACCESS_DENIED ? 'b' : 'd';
        return 0;
    }
    WinUsb_SetPipePolicy(usb, EP_IN, PIPE_TRANSFER_TIMEOUT, sizeof ms, &ms);
    WinUsb_SetPipePolicy(usb, EP_OUT, PIPE_TRANSFER_TIMEOUT, sizeof ms, &ms);
    return 1;
}

/// A command to the adapter: bytes sent, or -1.
int host_win32_gcc_write(const uint8_t* data, unsigned len)
{
    ULONG sent = 0;

    if (usb == NULL ||
        !WinUsb_WritePipe(usb, EP_OUT, (PUCHAR) data, len, &sent, NULL))
    {
        return -1;
    }
    return (int) sent;
}

/// A report from the adapter: bytes read; 0 if none came in time; -1 if
/// the adapter is gone.
int host_win32_gcc_read(uint8_t* data, unsigned len)
{
    ULONG got = 0;

    if (usb == NULL) {
        return -1;
    }
    if (!WinUsb_ReadPipe(usb, EP_IN, data, len, &got, NULL)) {
        return GetLastError() == ERROR_SEM_TIMEOUT ? 0 : -1;
    }
    return (int) got;
}

void host_win32_sleep_ms(unsigned ms)
{
    Sleep(ms);
}

void host_win32_gcc_close(void)
{
    if (usb != NULL) {
        WinUsb_Free(usb);
        usb = NULL;
    }
    if (device != INVALID_HANDLE_VALUE) {
        CloseHandle(device);
        device = INVALID_HANDLE_VALUE;
    }
}
