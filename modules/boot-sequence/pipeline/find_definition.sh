#!/usr/bin/env sh
# POSIX-compliant function definition finder
# Searches for function definition across the source tree

set -eu

usage() {
    printf 'Usage: %s <source_root> <function_name>\n' "$0" >&2
    printf '  Finds the definition of a function in the source tree\n' >&2
    exit 1
}

[ $# -eq 2 ] || usage

SOURCE_ROOT="$1"
FUNCTION_NAME="$2"

# Search for function definitions
# Pattern: return_type function_name(
# We look for the function name followed by ( with possible whitespace
# and ensure it is not a macro call (no semicolon on same line before opening brace)

find "$SOURCE_ROOT" -type f \( -name '*.c' -o -name '*.h' \) -print0 | \
xargs -0 grep -nH "^[a-zA-Z_][a-zA-Z0-9_ *]*[[:space:]]\+${FUNCTION_NAME}[[:space:]]*(" | \
head -20
