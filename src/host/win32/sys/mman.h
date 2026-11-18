/* Windows: the part of <sys/mman.h> the host layer uses, over VirtualAlloc
   (src/host/win32/compat.c). Only on the include path of a Windows build
   (tools/native_build.py). Anonymous mappings only: no file ever backs
   one. MAP_SHARED is accepted and behaves as MAP_PRIVATE, which is the same
   while nothing forks (fork() is Linux-only: see compat.h). */
#ifndef HOST_WIN32_SYS_MMAN_H
#define HOST_WIN32_SYS_MMAN_H

#include <stddef.h>
#include <sys/types.h>

#define PROT_NONE 0x0
#define PROT_READ 0x1
#define PROT_WRITE 0x2
#define PROT_EXEC 0x4

#define MAP_SHARED 0x01
#define MAP_PRIVATE 0x02
#define MAP_FIXED 0x10
#define MAP_ANONYMOUS 0x20
#define MAP_ANON MAP_ANONYMOUS
#define MAP_NORESERVE 0x4000
#define MAP_FIXED_NOREPLACE 0x100000

#define MAP_FAILED ((void*) -1)

#define MREMAP_MAYMOVE 1

void* mmap(void* addr, size_t length, int prot, int flags, int fd,
           off_t offset);
int munmap(void* addr, size_t length);
int mprotect(void* addr, size_t length, int prot);

/* rollback.c's mirrors only, and rollback does not start on Windows yet
   (it needs Linux's /proc/self/pagemap): never reached. */
static inline void* mremap(void* old, size_t old_size, size_t new_size,
                           int flags, ...)
{
    (void) old, (void) old_size, (void) new_size, (void) flags;
    return MAP_FAILED;
}

#endif
