#!/usr/bin/env sh
# POSIX-compliant function call extractor
# Extracts function calls from a given function in C source

set -eu

usage() {
    printf 'Usage: %s <source_file> <function_name>\n' "$0" >&2
    printf '  Extracts all function calls from the specified function\n' >&2
    exit 1
}

[ $# -eq 2 ] || usage

SOURCE_FILE="$1"
FUNCTION_NAME="$2"

# Extract the function body (between opening brace and matching closing brace)
# This is a simplified extractor that works for most C functions
awk -v fname="$FUNCTION_NAME" '
BEGIN { in_function=0; brace_depth=0; found=0 }

# Look for function definition
$0 ~ fname "\\(.*\\)" {
    in_function=1
    found=1
}

# Track braces when in function
in_function {
    # Count opening braces
    for(i=1; i<=length($0); i++) {
        c = substr($0, i, 1)
        if (c == "{") brace_depth++
        else if (c == "}") {
            brace_depth--
            if (brace_depth == 0) {
                in_function=0
                exit
            }
        }
    }
    # Print the line if we are inside the function body
    if (brace_depth > 0) print
}

END {
    if (!found) {
        print "ERROR: Function " fname " not found" > "/dev/stderr"
        exit 1
    }
}
' "$SOURCE_FILE" | \
# Now extract function calls (word followed by opening paren)
grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(' | \
# Remove the opening paren and whitespace
sed 's/[[:space:]]*(//' | \
# Remove duplicates and sort
sort -u
