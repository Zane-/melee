/** @file
 * Forced into code that allocates for the game (tools/native_build.py): its
 * malloc, calloc, realloc and free are the game heap's (gameheap.c), whose
 * memory a rollback snapshot covers.
 */
#ifndef HOST_GAMEHEAP_H
#define HOST_GAMEHEAP_H

#include <stdlib.h>
#include <string.h>

void* game_malloc(size_t n);
void* game_calloc(size_t count, size_t each);
void* game_realloc(void* p, size_t n);
void game_free(void* p);

#define malloc game_malloc
#define calloc game_calloc
#define realloc game_realloc
#define free game_free

#endif
