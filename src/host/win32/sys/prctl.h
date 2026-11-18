/* Windows: prctl() does nothing; any debugger may attach to a process. */
#ifndef HOST_WIN32_SYS_PRCTL_H
#define HOST_WIN32_SYS_PRCTL_H

#define PR_SET_PTRACER 0x59616d61
#define PR_SET_PTRACER_ANY ((unsigned long) -1)

static inline int prctl(int option, ...)
{
    (void) option;
    return 0;
}

#endif
