/* Windows: backtrace() over CaptureStackBackTrace (src/host/win32/compat.c).
   backtrace_symbols_fd() prints the bare addresses; resolve them against
   the executable with addr2line. */
#ifndef HOST_WIN32_EXECINFO_H
#define HOST_WIN32_EXECINFO_H

int backtrace(void** buffer, int size);
void backtrace_symbols_fd(void* const* buffer, int size, int fd);

#endif
