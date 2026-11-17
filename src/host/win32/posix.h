/* Windows: the POSIX process and signal calls the host layer names, as
   stand-ins that fail. Included before every host file on Windows
   (tools/native_build.py, -include).

   What depends on them is Linux-only for now: snapshots and restores
   (control.c: a sleeping fork per snapshot) and the engine's forked games
   (engine.c). On Windows fork() fails with ENOSYS, so "snap" answers
   "@ error no snapshot taken" and "engine fork" reports its error; the
   game itself runs as on Linux. Replacing them with copies of the game's
   state inside the process (state.c) is the way to bring them back. */
#ifndef HOST_WIN32_POSIX_H
#define HOST_WIN32_POSIX_H

#ifdef _WIN32

#include <errno.h>
#include <signal.h>
#include <sys/types.h>

#ifndef SIGUSR1
#define SIGUSR1 30
#endif
#ifndef SIGUSR2
#define SIGUSR2 31
#endif
#ifndef SIGBUS
#define SIGBUS 10
#endif
#ifndef SIGCHLD
#define SIGCHLD 17
#endif
#ifndef SIGKILL
#define SIGKILL 9
#endif
#ifndef SIGPIPE
#define SIGPIPE 13
#endif
#define SA_SIGINFO 0x4
#define SA_RESETHAND 0x80000000
#define SA_RESTART 0x10000000
#define SIG_BLOCK 0
#define SIG_UNBLOCK 1
#define SIG_SETMASK 2
#define WNOHANG 1

typedef struct {
    void* si_addr;
    int si_signo;
} siginfo_t;

typedef unsigned long host_sigset_t;
#define sigset_t host_sigset_t

struct sigaction {
    void (*sa_handler)(int);
    void (*sa_sigaction)(int, siginfo_t*, void*);
    sigset_t sa_mask;
    int sa_flags;
};

static inline int sigaction(int sig, const struct sigaction* act,
                            struct sigaction* old)
{
    (void) sig, (void) act, (void) old;
    return 0;
}

static inline int sigemptyset(sigset_t* set)
{
    *set = 0;
    return 0;
}

static inline int sigaddset(sigset_t* set, int sig)
{
    *set |= 1ul << (sig & 31);
    return 0;
}

static inline int sigprocmask(int how, const sigset_t* set, sigset_t* old)
{
    (void) how, (void) set;
    if (old != NULL) {
        *old = 0;
    }
    return 0;
}

static inline pid_t fork(void)
{
    errno = ENOSYS;
    return -1;
}

static inline int kill(pid_t pid, int sig)
{
    (void) pid, (void) sig;
    errno = ESRCH;
    return -1;
}

static inline pid_t waitpid(pid_t pid, int* status, int options)
{
    (void) pid, (void) status, (void) options;
    errno = ECHILD;
    return -1;
}

static inline pid_t getppid(void)
{
    return 0;
}

#define WIFEXITED(s) 1
#define WEXITSTATUS(s) (s)

/* archive.c's page size: Windows' pages are 4 KB too (its 64 KB
   allocation granularity matters only to VirtualAlloc, in compat.c). */
#ifndef _SC_PAGESIZE
#define _SC_PAGESIZE 30
#endif
static inline long sysconf(int name)
{
    return name == _SC_PAGESIZE ? 4096 : -1;
}

/* rollback.c reads /proc/self/pagemap with these; opening it fails on
   Windows first, so they are never reached. */
static inline long pread(int fd, void* buf, size_t n, long long offset)
{
    (void) fd, (void) buf, (void) n, (void) offset;
    errno = ENOSYS;
    return -1;
}

static inline long pwrite(int fd, const void* buf, size_t n,
                          long long offset)
{
    (void) fd, (void) buf, (void) n, (void) offset;
    errno = ENOSYS;
    return -1;
}

#endif /* _WIN32 */
#endif
