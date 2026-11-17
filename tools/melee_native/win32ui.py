"""Windows: what window.py does on X's virtual display, done to the game's
own window: a picture of it (shot), a key pressed in it (key), a request
to close it (close). There is no virtual display on Windows; the window is
an ordinary one on the desktop (docs/ai/windows.md).

The window is found by the game's process id. Pictures are taken from the
screen where the window's client area is, with the window brought to the
top for that moment: what the compositor shows is what the GPU drew.
(PrintWindow, even with PW_RENDERFULLCONTENT, waited about two minutes and
returned black for a window Vulkan presents to, through Dawn.) This
process is made DPI aware, so that sizes and positions are the screen's
pixels on a scaled display (at 300%, a 640x480 window measured 213x160).
Keys are posted to the window as WM_KEYDOWN and
WM_KEYUP with their scan codes, which is how SDL reads the keyboard there;
their names are X's, as the tests use them ("Right", "x", "Return").
"""
import ctypes
import time
from ctypes import wintypes
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

try:
    # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2: the screen's own pixels
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except (AttributeError, OSError):
    pass

WM_KEYDOWN, WM_KEYUP, WM_CLOSE = 0x0100, 0x0101, 0x0010
HWND_TOPMOST, HWND_NOTOPMOST = wintypes.HWND(-1), wintypes.HWND(-2)
# NOSIZE | NOMOVE | NOACTIVATE | ASYNCWINDOWPOS: posted, never waited on.
# Between frames the game waits for its next command and does not answer
# its window's messages; a sent SetWindowPos (or PrintWindow) waited some
# two minutes for it.
SWP_KEEP = 0x0001 | 0x0002 | 0x0010 | 0x4000
SRCCOPY = 0x00CC0020

# X key names -> Windows virtual-key codes (letters and digits are their
# own upper-case character)
VK = {"Return": 0x0D, "Escape": 0x1B, "space": 0x20, "BackSpace": 0x08,
      "Tab": 0x09, "Left": 0x25, "Up": 0x26, "Right": 0x27, "Down": 0x28,
      "Shift_L": 0xA0, "Shift_R": 0xA1, "Control_L": 0xA2,
      "Control_R": 0xA3, "Alt_L": 0xA4, "Home": 0x24, "End": 0x23,
      "Prior": 0x21, "Next": 0x22, "Delete": 0x2E, "Insert": 0x2D,
      **{"F%d" % n: 0x6F + n for n in range(1, 13)}}
# X key names -> SDL's names for them (the game's "vkey" command); a letter
# or digit is its upper-case self, others the same in both
SDL_NAMES = {"Shift_L": "Left Shift", "Shift_R": "Right Shift",
             "Control_L": "Left Ctrl", "Control_R": "Right Ctrl",
             "Alt_L": "Left Alt", "space": "Space", "BackSpace": "Backspace",
             "Prior": "PageUp", "Next": "PageDown"}
# keys Windows marks "extended" (bit 24 of lParam)
EXTENDED = {0x25, 0x26, 0x27, 0x28, 0x24, 0x23, 0x21, 0x22, 0x2E, 0x2D,
            0xA3}

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                     wintypes.LPARAM)
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND,
                                            ctypes.POINTER(wintypes.DWORD)]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                wintypes.WPARAM, wintypes.LPARAM]
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ClientToScreen.argtypes = [wintypes.HWND,
                                  ctypes.POINTER(wintypes.POINT)]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                wintypes.UINT]
gdi32.BitBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int,
                         ctypes.c_int, ctypes.c_int, wintypes.HDC,
                         ctypes.c_int, ctypes.c_int, wintypes.DWORD]
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int,
                                         ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT,
                            wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p,
                            wintypes.UINT]
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteDC.argtypes = [wintypes.HDC]


def window_of(pid):
    """The visible top-level window of process `pid`, or None."""
    found = []

    def each(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(EnumWindowsProc(each), 0)
    return found[0] if found else None


def shot(pid, path, size=None):
    """The window's picture (its client area; `size`: the top-left part of
    it, in pixels) into `path` (.ppm, .png, ... by its suffix)."""
    from PIL import Image

    hwnd = window_of(pid)
    if hwnd is None:
        raise RuntimeError("the game has no window to take a picture of")
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    origin = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(origin))
    # on top for the moment the picture is taken, then as it was
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_KEEP)
    time.sleep(0.15)  # the compositor shows it over the rest
    screen = user32.GetDC(None)
    dc = gdi32.CreateCompatibleDC(screen)
    bmp = gdi32.CreateCompatibleBitmap(screen, w, h)
    old = gdi32.SelectObject(dc, bmp)
    try:
        if not gdi32.BitBlt(dc, 0, 0, w, h, screen, origin.x, origin.y,
                            SRCCOPY):
            raise RuntimeError("BitBlt from the screen failed")

        class BitmapInfo(ctypes.Structure):
            _fields_ = [("biSize", wintypes.DWORD), ("biWidth", ctypes.c_long),
                        ("biHeight", ctypes.c_long),
                        ("biPlanes", wintypes.WORD),
                        ("biBitCount", wintypes.WORD),
                        ("biCompression", wintypes.DWORD),
                        ("biSizeImage", wintypes.DWORD),
                        ("biXPelsPerMeter", ctypes.c_long),
                        ("biYPelsPerMeter", ctypes.c_long),
                        ("biClrUsed", wintypes.DWORD),
                        ("biClrImportant", wintypes.DWORD)]

        info = BitmapInfo(ctypes.sizeof(BitmapInfo), w, -h, 1, 32, 0, 0, 0,
                          0, 0, 0)  # top-down, 32-bit BGRX
        buf = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(dc, bmp, 0, h, buf, ctypes.byref(info), 0)
    finally:
        gdi32.SelectObject(dc, old)
        gdi32.DeleteObject(bmp)
        gdi32.DeleteDC(dc)
        user32.ReleaseDC(None, screen)
        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_KEEP)
    img = Image.frombuffer("RGB", (w, h), buf.raw, "raw", "BGRX", 0, 1)
    if size is not None and (w, h) != tuple(size):
        if abs(w * size[1] - h * size[0]) <= max(w, h) // 50:
            # the same picture at the display's scale (a 1280x720 window is
            # 3840x2160 screen pixels at 300%): brought to the size asked,
            # as a test measures it (on Linux the virtual screen is
            # unscaled and the window is cut from its corner)
            img = img.resize(tuple(size), Image.LANCZOS)
        else:
            img = img.crop((0, 0, min(size[0], w), min(size[1], h)))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def key(pid, name, down=True):
    """Press (or release) a key in the game's window, by its X name."""
    hwnd = window_of(pid)
    if hwnd is None:
        raise RuntimeError("the game has no window to press a key in")
    vk = VK.get(name)
    if vk is None and len(name) == 1 and name.isalnum():
        vk = ord(name.upper())
    if vk is None:
        raise ValueError("no such key: " + name)
    scan = user32.MapVirtualKeyW(vk, 0)  # MAPVK_VK_TO_VSC
    lparam = 1 | (scan << 16) | ((1 << 24) if vk in EXTENDED else 0)
    if not down:
        lparam |= (1 << 30) | (1 << 31)  # was down; is being released
    user32.PostMessageW(hwnd, WM_KEYDOWN if down else WM_KEYUP, vk, lparam)


def close(pid):
    """Ask the game's window to close, as its close button does. Returns
    the number of windows asked (0 or 1)."""
    hwnd = window_of(pid)
    if hwnd is None:
        return 0
    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return 1
