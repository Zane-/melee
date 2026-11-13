#!/bin/sh
# Run the native headless game and turn the addresses of a crash backtrace
# into function names and source lines.
#   tools/native_run.sh [melee_headless options]
exe="$(dirname "$0")/../build/native/melee_headless"
"$exe" "$@" 2>&1 | while IFS= read -r line; do
    case "$line" in
    *melee_headless*"["0x*)
        addr=$(printf '%s' "$line" | sed 's/.*\[\(0x[0-9a-f]*\)\].*/\1/')
        printf '  %s\n' "$(addr2line -f -p -e "$exe" "$addr" | sed "s|$(cd "$(dirname "$0")/.." && pwd)/||g")"
        ;;
    *) printf '%s\n' "$line" ;;
    esac
done
