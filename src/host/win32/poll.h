/* Windows: <poll.h>, for control.c's snapshot sleeper, which never runs
   there (fork() fails: see posix.h). */
#ifndef HOST_WIN32_POLL_H
#define HOST_WIN32_POLL_H

#include <errno.h>

#define POLLIN 0x001
#define POLLOUT 0x004
#define POLLERR 0x008
#define POLLHUP 0x010
#define POLLNVAL 0x020

struct pollfd {
    int fd;
    short events;
    short revents;
};

static inline int poll(struct pollfd* fds, unsigned long n, int timeout)
{
    (void) fds, (void) n, (void) timeout;
    errno = ENOSYS;
    return -1;
}

static inline int ppoll(struct pollfd* fds, unsigned long n,
                        const void* timeout, const void* sigmask)
{
    (void) timeout, (void) sigmask;
    return poll(fds, n, -1);
}

#endif
