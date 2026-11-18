/* Windows: the POSIX functions the host layer uses that MinGW lacks, over
   the Win32 API. Built only on Windows (tools/native_build.py).

   The arena at the console's addresses (0x80000000 and up, os.c) is above
   2 GB: a 32-bit process gets that address space only when linked
   --large-address-aware and run on 64-bit Windows. */

#include <sys/mman.h>
#include <execinfo.h>
#include <ucontext.h>

#include <errno.h>
#include <fcntl.h>
#include <io.h>
#include <stdint.h>
#include <stdio.h>
#include <windows.h>

static DWORD protection(int prot)
{
    if (prot & PROT_EXEC) {
        return (prot & PROT_WRITE) ? PAGE_EXECUTE_READWRITE
                                   : PAGE_EXECUTE_READ;
    }
    if (prot & PROT_WRITE) {
        return PAGE_READWRITE;
    }
    if (prot & PROT_READ) {
        return PAGE_READONLY;
    }
    return PAGE_NOACCESS;
}

void* mmap(void* addr, size_t length, int prot, int flags, int fd,
           off_t offset)
{
    void* p;

    (void) offset;
    if (fd != -1 || !(flags & MAP_ANONYMOUS) || length == 0) {
        errno = EINVAL;
        return MAP_FAILED;
    }
    /* A fixed address is taken only if free (MAP_FIXED_NOREPLACE; the
       host never asks to replace a mapping). Committed pages are not
       backed by memory until touched, as with MAP_NORESERVE. The mappings
       at fixed addresses are the game's (low memory, the arena, the game
       heap, audio RAM): their written pages are watched, for rollback.c,
       as Linux's soft-dirty bits are. */
    int fixed = (flags & (MAP_FIXED | MAP_FIXED_NOREPLACE)) != 0;
    p = VirtualAlloc(fixed ? addr : NULL, length,
                     MEM_RESERVE | MEM_COMMIT | (fixed ? MEM_WRITE_WATCH : 0),
                     protection(prot));
    if (p == NULL) {
        errno = ENOMEM;
        return MAP_FAILED;
    }
    return p;
}

int munmap(void* addr, size_t length)
{
    MEMORY_BASIC_INFORMATION info;

    if (VirtualQuery(addr, &info, sizeof info) == 0) {
        errno = EINVAL;
        return -1;
    }
    /* A whole mapping is released; part of one is decommitted, which
       frees its memory and keeps the address range reserved. */
    if (info.AllocationBase == addr && info.RegionSize >= length) {
        return VirtualFree(addr, 0, MEM_RELEASE) ? 0 : -1;
    }
    return VirtualFree(addr, length, MEM_DECOMMIT) ? 0 : -1;
}

int mprotect(void* addr, size_t length, int prot)
{
    DWORD old;

    if (!VirtualProtect(addr, length, protection(prot), &old)) {
        errno = EACCES;
        return -1;
    }
    return 0;
}

/* --- the game's statics (state.c, rollback.c) --------------------------- */

/* On Linux a linker script gathers the game's statics into one section
   between these two symbols, which a snapshot copies. On Windows the game's
   objects have their .data and .bss renamed .data$gs1 and .data$gs2
   (tools/native_build.py, gather_win32); the PE linker sorts .data$ sections
   by name, so these two, in .data$gs0 and .data$gs9, bound them. Page
   aligned, as on Linux (rollback.c follows whole pages). */
__attribute__((section(".data$gs0"), aligned(4096))) char
    __game_state_start[4] = { 1 };
__attribute__((section(".data$gs9"), aligned(4096))) char
    __game_state_end[4] = { 1 };

/* --- crashes: main.c's report, in place of its sigaction handler ------- */

static void (*fault_report)(unsigned code, void* addr);

static LONG WINAPI on_exception(EXCEPTION_POINTERS* info)
{
    EXCEPTION_RECORD* rec = info->ExceptionRecord;
    void* addr = rec->ExceptionAddress;

    /* An access violation reports the address it touched, as si_addr. */
    if (rec->ExceptionCode == EXCEPTION_ACCESS_VIOLATION &&
        rec->NumberParameters >= 2)
    {
        addr = (void*) rec->ExceptionInformation[1];
    }
    /* The faulting instruction: the backtrace host_fatal prints is the
       filter's own stack, not the crash's. addr2line -e melee_headless.exe
       takes this address. */
    fprintf(stderr, "[host] faulting instruction %p (ebp %p, esp %p)\n",
            rec->ExceptionAddress, (void*) info->ContextRecord->Ebp,
            (void*) info->ContextRecord->Esp);
    {
        /* the callers, by the frame pointers (-fno-omit-frame-pointer) */
        void** fp = (void**) info->ContextRecord->Ebp;
        for (int i = 0; i < 16 && fp != NULL; i++) {
            MEMORY_BASIC_INFORMATION mbi;
            if (VirtualQuery(fp, &mbi, sizeof mbi) == 0 ||
                mbi.State != MEM_COMMIT)
            {
                break;
            }
            fprintf(stderr, "  caller %p\n", fp[1]);
            fp = (void**) fp[0];
        }
    }
    if (fault_report != NULL) {
        fault_report((unsigned) rec->ExceptionCode, addr);
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

void host_win32_on_fault(void (*report)(unsigned code, void* addr))
{
    fault_report = report;
    SetUnhandledExceptionFilter(on_exception);
}

/* --- coroutines (engine.c's search): ucontext over fibers --------------- */

static void to_fiber(void)
{
    if (!IsThreadAFiber()) {
        ConvertThreadToFiber(NULL);
    }
}

static void WINAPI fiber_start(void* arg)
{
    ucontext_t* ucp = arg;

    ucp->entry();
    /* Returning from a fiber's function ends the thread: go where uc_link
       says instead, and never come back (a finished coroutine's fiber is
       deleted when its context is made again). */
    for (;;) {
        SwitchToFiber(ucp->uc_link->fiber);
    }
}

int getcontext(ucontext_t* ucp)
{
    to_fiber();
    ucp->uc_link = NULL;
    ucp->entry = NULL;
    return 0;
}

void makecontext(ucontext_t* ucp, void (*func)(void), int argc, ...)
{
    (void) argc;
    to_fiber();
    if (ucp->fiber != NULL && ucp->fiber != GetCurrentFiber()) {
        DeleteFiber(ucp->fiber); /* the last coroutine made from it */
    }
    ucp->entry = func;
    ucp->fiber = CreateFiber(ucp->uc_stack.ss_size, fiber_start, ucp);
}

int swapcontext(ucontext_t* oucp, const ucontext_t* ucp)
{
    to_fiber();
    oucp->fiber = GetCurrentFiber();
    if (ucp->fiber == NULL) {
        errno = EINVAL;
        return -1;
    }
    SwitchToFiber(ucp->fiber);
    return 0;
}

/* --- memory outside the address space (control.c's snapshots) --------- */

/* A snapshot is the game's whole state, some 70 MB; a 32-bit process has
   room for few of them. Each is kept in a section of its own backed by the
   page file, mapped only while it is written or read. */

void* host_win32_blob_new(size_t size)
{
    return CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0,
                              (DWORD) size, NULL);
}

void* host_win32_blob_map(void* blob, size_t size)
{
    return MapViewOfFile((HANDLE) blob, FILE_MAP_ALL_ACCESS, 0, 0, size);
}

void host_win32_blob_unmap(void* view)
{
    UnmapViewOfFile(view);
}

void host_win32_blob_free(void* blob)
{
    CloseHandle((HANDLE) blob);
}

/// The same with a name another process can open it by (a forked game's
/// state, engine.c): NULL if it cannot be made.
void* host_win32_blob_new_named(const char* name, size_t size)
{
    return CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0,
                              (DWORD) size, name);
}

void* host_win32_blob_open(const char* name)
{
    return OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, name);
}

/* --- written pages (rollback.c, in place of /proc/self/pagemap) --------- */

/// The pages written in [base, base + length) since the last reset, into
/// `pages` (room for `max`): how many, or -1 if the range is not watched.
long host_win32_written(void* base, size_t length, void** pages,
                        unsigned long max)
{
    ULONG_PTR count = max;
    ULONG granularity;

    if (GetWriteWatch(0, base, length, pages, &count, &granularity) != 0) {
        return -1;
    }
    return (long) count;
}

void host_win32_unwrite(void* base, size_t length)
{
    ResetWriteWatch(base, length);
}

unsigned long host_win32_pid(void)
{
    return GetCurrentProcessId();
}

/* --- the executable's own path (window.c, in place of /proc/self/exe) -- */

int host_win32_exe_path(char* out, int size)
{
    DWORD n = GetModuleFileNameA(NULL, out, (DWORD) size);
    return n == 0 || n >= (DWORD) size ? -1 : (int) n;
}

/* --- stdout and stderr in binary mode (main.c) -------------------------- */

void host_win32_binary_output(void)
{
    _setmode(_fileno(stdout), _O_BINARY);
    _setmode(_fileno(stderr), _O_BINARY);
}

/* --- a write watch, for finding what overwrites memory (dvd.c) ---------- */

/* MELEE_WATCH_FILE=NAME (dvd.c): once that disc file has been read, its
   first word's page is made read-only. A write to the page faults; one to
   the word itself is reported, with the writing instruction and its
   callers, then every write is let through by a single step and the page
   protected again. */
static uint8_t* watch_page;
static uintptr_t watch_lo, watch_hi;
static int watch_rearm;

static void watch_report(CONTEXT* c, uintptr_t addr)
{
    void** fp = (void**) c->Ebp;
    fprintf(stderr, "[host] watch: %p written by %p (now %08x)\n",
            (void*) addr, (void*) c->Eip, *(unsigned*) watch_lo);
    for (int i = 0; i < 16 && fp != NULL; i++) {
        MEMORY_BASIC_INFORMATION mbi;
        if (VirtualQuery(fp, &mbi, sizeof mbi) == 0 ||
            mbi.State != MEM_COMMIT)
        {
            break;
        }
        fprintf(stderr, "  caller %p\n", fp[1]);
        fp = (void**) fp[0];
    }
    fflush(stderr);
}

static LONG WINAPI watch_handler(EXCEPTION_POINTERS* info)
{
    EXCEPTION_RECORD* rec = info->ExceptionRecord;
    DWORD old;

    if (rec->ExceptionCode == EXCEPTION_ACCESS_VIOLATION &&
        rec->NumberParameters >= 2 && rec->ExceptionInformation[0] == 1 &&
        watch_page != NULL)
    {
        uintptr_t addr = rec->ExceptionInformation[1];
        if (addr >= (uintptr_t) watch_page &&
            addr < (uintptr_t) watch_page + 4096)
        {
            if (addr + 4 > watch_lo && addr < watch_hi) {
                watch_report(info->ContextRecord, addr);
            }
            VirtualProtect(watch_page, 4096, PAGE_READWRITE, &old);
            info->ContextRecord->EFlags |= 0x100; /* one instruction */
            watch_rearm = 1;
            return EXCEPTION_CONTINUE_EXECUTION;
        }
    }
    if (rec->ExceptionCode == EXCEPTION_SINGLE_STEP && watch_rearm) {
        watch_rearm = 0;
        VirtualProtect(watch_page, 4096, PAGE_READONLY, &old);
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

void host_win32_watch(void* addr, unsigned length)
{
    static int installed;
    DWORD old;

    if (!installed) {
        AddVectoredExceptionHandler(1, watch_handler);
        installed = 1;
    }
    if (watch_page != NULL) {
        VirtualProtect(watch_page, 4096, PAGE_READWRITE, &old);
    }
    watch_lo = (uintptr_t) addr;
    watch_hi = watch_lo + length;
    watch_page = (uint8_t*) (watch_lo & ~(uintptr_t) 4095);
    fprintf(stderr, "[host] watch: %p, now %08x\n", addr, *(unsigned*) addr);
    VirtualProtect(watch_page, 4096, PAGE_READONLY, &old);
}

/* --- backtraces --------------------------------------------------------- */

int backtrace(void** buffer, int size)
{
    return CaptureStackBackTrace(1, (DWORD) size, buffer, NULL);
}

void backtrace_symbols_fd(void* const* buffer, int size, int fd)
{
    FILE* out = fd == 1 ? stdout : stderr;

    for (int i = 0; i < size; i++) {
        fprintf(out, "  [%2d] %p\n", i, buffer[i]);
    }
    fflush(out);
}
