#ifndef SHIM_STDDEF_H
#define SHIM_STDDEF_H
#define NULL ((void*)0)
typedef unsigned long size_t;
typedef int ptrdiff_t;
#define offsetof(type, member) ((size_t) &(((type*) 0)->member))
#endif
