/* Windows, window build: operator new and delete with 16-byte alignment.

   32-bit MinGW takes operator new from msvcrt's malloc, which aligns to 8
   bytes, while gcc, for types it may move with SSE, takes heap memory to
   be aligned to 16 (__STDCPP_DEFAULT_NEW_ALIGNMENT__). Aurora's
   std::deque<RenderPass> was zeroed with movaps into 8-aligned memory, and
   Windows reports that as an access violation at 0xFFFFFFFF (the game's
   third frame, 2026-11-17). Linux's malloc aligns to 16, so the problem is
   Windows-only.

   This replaces the global operators for everything linked into the
   executable (the host, Aurora, RmlUi). Dawn and SDL are DLLs with their
   own; nothing allocated on one side is freed on the other (they are used
   through C interfaces). Over-aligned new (std::align_val_t) is libstdc++'s,
   which already uses _aligned_malloc and _aligned_free: the same pair. */

#include <cstddef>
#include <malloc.h>
#include <new>

namespace {

constexpr std::size_t Alignment = 16;

void* allocate(std::size_t size)
{
    void* p = _aligned_malloc(size != 0 ? size : 1, Alignment);
    if (p == nullptr) {
        throw std::bad_alloc();
    }
    return p;
}

void* allocate_nothrow(std::size_t size) noexcept
{
    return _aligned_malloc(size != 0 ? size : 1, Alignment);
}

} // namespace

void* operator new(std::size_t size)
{
    return allocate(size);
}

void* operator new[](std::size_t size)
{
    return allocate(size);
}

void* operator new(std::size_t size, const std::nothrow_t&) noexcept
{
    return allocate_nothrow(size);
}

void* operator new[](std::size_t size, const std::nothrow_t&) noexcept
{
    return allocate_nothrow(size);
}

void operator delete(void* p) noexcept
{
    _aligned_free(p);
}

void operator delete[](void* p) noexcept
{
    _aligned_free(p);
}

void operator delete(void* p, std::size_t) noexcept
{
    _aligned_free(p);
}

void operator delete[](void* p, std::size_t) noexcept
{
    _aligned_free(p);
}

void operator delete(void* p, const std::nothrow_t&) noexcept
{
    _aligned_free(p);
}

void operator delete[](void* p, const std::nothrow_t&) noexcept
{
    _aligned_free(p);
}
