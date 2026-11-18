/* Windows: the part of <ucontext.h> engine.c uses to run its search as a
   coroutine beside the game, over Win32 fibers (src/host/win32/compat.c).

   Covered: getcontext() on a context about to be made, makecontext() with
   no arguments, swapcontext() between the game and that coroutine, and
   uc_link (where a coroutine goes when its function returns). The stack in
   uc_stack is not used; a fiber of uc_stack.ss_size gets its own. */
#ifndef HOST_WIN32_UCONTEXT_H
#define HOST_WIN32_UCONTEXT_H

#include <stddef.h>

typedef struct host_ucontext {
    struct {
        void* ss_sp;
        size_t ss_size;
        int ss_flags;
    } uc_stack;
    struct host_ucontext* uc_link;
    void* fiber;          ///< the fiber this context runs on (or ran on)
    void (*entry)(void);  ///< makecontext's function
} ucontext_t;

int getcontext(ucontext_t* ucp);
void makecontext(ucontext_t* ucp, void (*func)(void), int argc, ...);
int swapcontext(ucontext_t* oucp, const ucontext_t* ucp);

#endif
