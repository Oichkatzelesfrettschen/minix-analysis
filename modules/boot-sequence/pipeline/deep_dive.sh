#!/usr/bin/env sh
# POSIX-compliant deep-dive analyzer
# Shows detailed information about each function in the boot sequence

set -eu

MINIX_ROOT="${1:-/home/eirikr/Playground/minix}"
FUNCTION="${2:-kmain}"
OUTPUT_FILE="${3:-boot_analysis.md}"

# Colors
if [ -t 1 ]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_CYAN='\033[36m'
    C_GREEN='\033[32m'
    C_YELLOW='\033[33m'
else
    C_RESET=''
    C_BOLD=''
    C_CYAN=''
    C_GREEN=''
    C_YELLOW=''
fi

# Initialize output
{
    printf "# Minix Kernel Boot Sequence Deep Dive\n\n"
    printf "**Entry Point:** \`%s()\`\n\n" "$FUNCTION"
    printf "**Analysis Date:** %s\n\n" "$(date)"
    printf -- "---\n\n"
} > "$OUTPUT_FILE"

# Find function definition
find_func_def() {
    func="$1"
    find "$MINIX_ROOT/minix" -type f \( -name '*.c' -o -name '*.h' \) -exec grep -l "^[a-zA-Z_][a-zA-Z0-9_ *]*[[:space:]]\+${func}[[:space:]]*(" {} \; 2>/dev/null | head -1
}

# Extract function source with context
extract_func_source() {
    file="$1"
    func="$2"

    awk -v fname="$func" '
    BEGIN { in_function=0; brace_depth=0; line_num=0; start_line=0 }

    {
        line_num++
        if (!in_function && $0 ~ fname "\\(.*\\)") {
            in_function=1
            start_line=line_num
        }

        if (in_function) {
            print line_num ": " $0

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
        }
    }
    ' "$file"
}

# Extract function calls
extract_calls() {
    file="$1"
    func="$2"

    awk -v fname="$func" '
    BEGIN { in_function=0; brace_depth=0 }

    $0 ~ fname "\\(.*\\)" {
        in_function=1
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
    ' "$file" | \
    grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(' | \
    sed 's/[[:space:]]*(//' | \
    sort -u | \
    grep -vE '^(if|for|while|switch|sizeof|typeof|return)$'
}

# Extract comments above function
extract_func_comment() {
    file="$1"
    func="$2"

    awk -v fname="$func" '
    {
        # Look for comment blocks
        if ($0 ~ /\/\*/) {
            in_comment=1
            comment=""
        }

        if (in_comment) {
            comment = comment "\n" $0
        }

        if ($0 ~ /\*\//) {
            in_comment=0
        }

        # Check if next non-comment line is our function
        if (!in_comment && $0 ~ fname "\\(.*\\)") {
            print comment
            exit
        }

        # Reset comment if we hit code
        if (!in_comment && $0 !~ /^[[:space:]]*$/ && $0 !~ /^[[:space:]]*\//) {
            comment=""
        }
    }
    ' "$file"
}

# Analyze function
analyze_function() {
    func="$1"
    depth="$2"

    printf "${C_BOLD}${C_CYAN}Analyzing: %s (depth %d)${C_RESET}\n" "$func" "$depth"

    def_file=$(find_func_def "$func")

    if [ -z "$def_file" ]; then
        printf "${C_YELLOW}  Not found (external or macro)${C_RESET}\n\n"
        {
            printf "### \`%s()\` - EXTERNAL\n\n" "$func"
            printf "Function not found in source tree (likely stdlib, macro, or inline).\n\n"
        } >> "$OUTPUT_FILE"
        return
    fi

    rel_path=$(echo "$def_file" | sed "s|$MINIX_ROOT/||")
    printf "${C_GREEN}  Found: %s${C_RESET}\n" "$rel_path"

    # Extract comment
    comment=$(extract_func_comment "$def_file" "$func")

    # Extract source
    source=$(extract_func_source "$def_file" "$func")

    # Extract calls
    calls=$(extract_calls "$def_file" "$func")

    # Write to markdown
    {
        printf "## %s \`%s()\`\n\n" "$(printf '%*s' "$depth" '' | tr ' ' '#')" "$func"
        printf "**Location:** \`%s\`\n\n" "$rel_path"

        if [ -n "$comment" ]; then
            printf "**Documentation:**\n\`\`\`c\n%s\n\`\`\`\n\n" "$comment"
        fi

        if [ -n "$calls" ]; then
            printf "**Function Calls:** %d unique functions\n\n" "$(echo "$calls" | wc -l)"
            printf "\`\`\`\n%s\n\`\`\`\n\n" "$calls"
        fi

        printf "**Source Code:**\n\`\`\`c\n%s\n\`\`\`\n\n" "$source"
        printf -- "---\n\n"
    } >> "$OUTPUT_FILE"

    # Process direct calls if depth < 2
    if [ "$depth" -lt 2 ] && [ -n "$calls" ]; then
        echo "$calls" | while IFS= read -r called_func; do
            analyze_function "$called_func" $((depth + 1))
        done
    fi

    printf "\n"
}

# Main
main() {
    printf "${C_BOLD}Minix Kernel Deep Dive Analyzer${C_RESET}\n"
    printf "================================\n\n"

    analyze_function "$FUNCTION" 0

    printf "${C_GREEN}${C_BOLD}Analysis complete!${C_RESET}\n"
    printf "Output: %s\n" "$OUTPUT_FILE"
}

main
