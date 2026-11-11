/**
 * @file
 * Forced prefix for every overlay (mod) translation unit.
 *
 * Routes all code and constants out of the vanilla section names so the
 * overlay can be linked above the vanilla image without moving it. Compile
 * overlay files with:
 *
 *     -prefix overlay_prefix.h -i src/melee/tm
 *     -sdata 0 -sdata2 0 -str reuse,readonly
 *
 * With those flags a file may only produce .tmtext and .tmrodata. Writable
 * statics land in .tmdata / .tmbss and are rejected by tools/overlay_link.py:
 * mutable state must be heap-allocated so Slippi's rollback saves it.
 * See docs/ai/overlay-build.md.
 */
#pragma section code_type ".tmtext"
#pragma section const_type ".tmrodata"
#pragma section data_type ".tmdata" ".tmbss"
