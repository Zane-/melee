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
       backed by memory until touched, as with MAP_NORESERVE. */
    p = VirtualAlloc((flags & (MAP_FIXED | MAP_FIXED_NOREPLACE)) ? addr
                                                                 : NULL,
                     length, MEM_RESERVE | MEM_COMMIT, protection(prot));
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

/* On Linux the linker script tools/native_build.py writes gathers the
   game's statics into one section between these two symbols, which a
   snapshot copies. The Windows linker gets no such script yet, so the
   region is empty: snapshots there hold the arena and the game heap only,
   and rollback (netplay) is not to be trusted on Windows until the statics
   are gathered too. */
char __game_state_start[16] __attribute__((aligned(4096)));
extern char __game_state_end[] __attribute__((alias("__game_state_start")));

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
