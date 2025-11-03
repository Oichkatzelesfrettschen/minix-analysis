#!/usr/bin/env sh
# POSIX-compliant Minix kernel boot sequence tracer
# Traces the complete boot sequence starting from kmain()

set -eu

# Configuration
MINIX_ROOT="${1:-/home/eirikr/Playground/minix}"
OUTPUT_DIR="$(pwd)/boot_trace_output"
MAX_DEPTH="${2:-3}"

# Function to trace
ENTRY_POINT="kmain"
MAIN_FILE="$MINIX_ROOT/minix/kernel/main.c"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Color codes for output (fallback to empty if not terminal)
if [ -t 1 ]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_RED='\033[31m'
    C_GREEN='\033[32m'
    C_YELLOW='\033[33m'
    C_BLUE='\033[34m'
    C_CYAN='\033[36m'
else
    C_RESET=''
    C_BOLD=''
    C_RED=''
    C_GREEN=''
    C_YELLOW=''
    C_BLUE=''
    C_CYAN=''
fi

log() {
    printf "${C_BLUE}[INFO]${C_RESET} %s\n" "$*"
}

error() {
    printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" >&2
}

success() {
    printf "${C_GREEN}[SUCCESS]${C_RESET} %s\n" "$*"
}

# Extract functions called by a specific function
extract_function_calls() {
    source_file="$1"
    function_name="$2"

    if [ ! -f "$source_file" ]; then
        error "Source file not found: $source_file"
        return 1
    fi

    # Use awk to extract function body and find calls
    awk -v fname="$function_name" '
    BEGIN { in_function=0; brace_depth=0; found=0 }

    $0 ~ fname "\\(.*\\)" {
        in_function=1
        found=1
    }

    in_function {
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
        if (brace_depth > 0) print
    }

    END {
        if (!found) exit 1
    }
    ' "$source_file" 2>/dev/null | \
    grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(' | \
    sed 's/[[:space:]]*(//' | \
    sort -u | \
    # Filter out common stdlib and macro-like functions
    grep -vE '^(if|for|while|switch|sizeof|typeof|printf|memcpy|memset|assert|static_assert)$'
}

# Find function definition in source tree
find_function_definition() {
    func_name="$1"

    find "$MINIX_ROOT/minix" -type f \( -name '*.c' -o -name '*.h' \) -print0 2>/dev/null | \
    xargs -0 grep -l "^[a-zA-Z_][a-zA-Z0-9_ *]*[[:space:]]\+${func_name}[[:space:]]*(" 2>/dev/null | \
    head -1
}

# Main tracing logic
trace_function() {
    func_name="$1"
    depth="$2"
    source_file="$3"
    indent="$4"

    # Check depth limit
    if [ "$depth" -gt "$MAX_DEPTH" ]; then
        return
    fi

    # Print current function
    printf "%s${C_CYAN}%s${C_RESET} [depth=%d]\n" "$indent" "$func_name" "$depth"

    # Extract calls from this function
    calls=$(extract_function_calls "$source_file" "$func_name" 2>/dev/null || true)

    if [ -n "$calls" ]; then
        printf "%s  ${C_YELLOW}Calls:${C_RESET}\n" "$indent"

        # Process each called function
        echo "$calls" | while IFS= read -r called_func; do
            printf "%s    -> %s\n" "$indent" "$called_func"

            # Try to find definition
            def_file=$(find_function_definition "$called_func" || true)
            if [ -n "$def_file" ]; then
                printf "%s       ${C_GREEN}Found in:${C_RESET} %s\n" "$indent" "$def_file"

                # Save to output
                printf "%s -> %s [%s]\n" "$func_name" "$called_func" "$def_file" >> "$OUTPUT_DIR/call_graph.txt"

                # Recursive trace (only if definition found and not too deep)
                next_depth=$((depth + 1))
                next_indent="$indent    "
                # Uncomment to enable recursive tracing:
                # trace_function "$called_func" "$next_depth" "$def_file" "$next_indent"
            else
                printf "%s       ${C_RED}Not found${C_RESET} (stdlib or macro)\n" "$indent"
                printf "%s -> %s [EXTERNAL]\n" "$func_name" "$called_func" >> "$OUTPUT_DIR/call_graph.txt"
            fi
        done
    fi
}

# Main execution
main() {
    log "Minix Kernel Boot Sequence Tracer"
    log "================================="
    log "Minix root: $MINIX_ROOT"
    log "Entry point: $ENTRY_POINT"
    log "Max depth: $MAX_DEPTH"
    log ""

    # Initialize output files
    : > "$OUTPUT_DIR/call_graph.txt"
    : > "$OUTPUT_DIR/functions_summary.txt"

    # Start tracing from kmain
    log "Tracing from $ENTRY_POINT()..."
    trace_function "$ENTRY_POINT" 0 "$MAIN_FILE" ""

    log ""
    success "Trace complete!"
    log "Output saved to: $OUTPUT_DIR/"
    log "  - call_graph.txt: Complete call graph"
    log ""

    # Generate summary
    log "Generating summary..."
    {
        printf "MINIX KERNEL BOOT SEQUENCE ANALYSIS\n"
        printf "===================================\n\n"
        printf "Entry Point: %s\n" "$ENTRY_POINT"
        printf "Source File: %s\n\n" "$MAIN_FILE"
        printf "Total unique functions discovered: %d\n\n" \
            "$(cut -d' ' -f3 "$OUTPUT_DIR/call_graph.txt" | sort -u | wc -l)"
        printf "Call Graph:\n"
        cat "$OUTPUT_DIR/call_graph.txt"
    } > "$OUTPUT_DIR/functions_summary.txt"

    success "Summary saved to: $OUTPUT_DIR/functions_summary.txt"
}

main
