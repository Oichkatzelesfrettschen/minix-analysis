#!/usr/bin/env sh
# Generate Graphviz DOT file from call graph for visualization
# Usage: ./generate_dot_graph.sh <call_graph.txt> <output.dot>

set -eu

INPUT="${1:-boot_trace_output/call_graph.txt}"
OUTPUT="${2:-boot_graph.dot}"

# Start DOT file
{
    printf 'digraph MinixBoot {\n'
    printf '    rankdir=TB;\n'
    printf '    node [shape=box, style=filled, fillcolor=lightblue];\n'
    printf '    edge [color=gray];\n'
    printf '\n'
    printf '    kmain [fillcolor=lightgreen, style=filled, penwidth=2];\n'
    printf '\n'
} > "$OUTPUT"

# Parse call graph
while IFS= read -r line; do
    # Extract caller and callee
    caller=$(echo "$line" | cut -d' ' -f1)
    rest=$(echo "$line" | cut -d'>' -f2-)

    # Check if EXTERNAL
    if echo "$rest" | grep -q EXTERNAL; then
        callee=$(echo "$rest" | sed 's/\[EXTERNAL\]//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        printf '    %s [fillcolor=lightgray];\n' "$callee" >> "$OUTPUT"
        printf '    %s -> %s [style=dashed];\n' "$caller" "$callee" >> "$OUTPUT"
    else
        # Internal function - extract name before [
        callee=$(echo "$rest" | sed 's/\[.*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        printf '    %s -> %s;\n' "$caller" "$callee" >> "$OUTPUT"
    fi
done < "$INPUT"

# Close DOT file
printf '}\n' >> "$OUTPUT"

printf "DOT file generated: %s\n" "$OUTPUT"
printf "To generate PNG:\n"
printf "  dot -Tpng %s -o boot_graph.png\n" "$OUTPUT"
printf "To generate SVG:\n"
printf "  dot -Tsvg %s -o boot_graph.svg\n" "$OUTPUT"
