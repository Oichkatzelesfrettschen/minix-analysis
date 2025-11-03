#!/usr/bin/env sh
# Analyze call graph structure and calculate metrics
# Generates comprehensive geometric and structural analysis

set -eu

GRAPH="${1:-boot_trace_output/call_graph.txt}"
OUTPUT="${2:-graph_analysis.txt}"

# Calculate various metrics
{
    printf "MINIX KERNEL BOOT SEQUENCE - STRUCTURAL ANALYSIS\n"
    printf "================================================\n\n"
    printf "Analysis Date: %s\n\n" "$(date)"

    # Total functions
    total_funcs=$(cut -d' ' -f1 "$GRAPH" | sort -u | wc -l)
    total_edges=$(wc -l < "$GRAPH")

    printf "GRAPH METRICS:\n"
    printf "==============\n"
    printf "Total Unique Functions: %d\n" "$total_funcs"
    printf "Total Call Edges: %d\n" "$total_edges"
    printf "Average Fan-out: %.2f\n" "$(echo "scale=2; $total_edges / $total_funcs" | bc)"
    printf "\n"

    # Function with most calls
    printf "FUNCTION COMPLEXITY (Top 10 by outgoing calls):\n"
    printf "================================================\n"
    cut -d' ' -f1 "$GRAPH" | sort | uniq -c | sort -rn | head -10 | \
        awk '{printf "%-30s calls %3d functions\n", $2, $1}'
    printf "\n"

    # Most called functions
    printf "MOST CALLED FUNCTIONS (Top 10):\n"
    printf "================================\n"
    awk '{print $3}' "$GRAPH" | sort | uniq -c | sort -rn | head -10 | \
        awk '{printf "%-30s called by %3d functions\n", $2, $1}'
    printf "\n"

    # External vs Internal
    external=$(grep -c EXTERNAL "$GRAPH" || echo 0)
    internal=$((total_edges - external))

    printf "FUNCTION CLASSIFICATION:\n"
    printf "========================\n"
    printf "Internal (Minix) Functions: %d (%.1f%%)\n" "$internal" \
        "$(echo "scale=1; $internal * 100 / $total_edges" | bc)"
    printf "External/Macro Functions: %d (%.1f%%)\n" "$external" \
        "$(echo "scale=1; $external * 100 / $total_edges" | bc)"
    printf "\n"

    # Critical path (functions called directly by kmain)
    printf "CRITICAL PATH (Direct kmain calls):\n"
    printf "====================================\n"
    grep "^kmain -> " "$GRAPH" | wc -l | \
        xargs printf "kmain directly calls %d functions:\n"
    grep "^kmain -> " "$GRAPH" | \
        sed 's/kmain -> //' | \
        awk -F'[' '{printf "  • %s\n", $1}' | \
        sed 's/[[:space:]]*$//' | \
        sort
    printf "\n"

    # Subsystem breakdown
    printf "SUBSYSTEM ANALYSIS (by file location):\n"
    printf "=======================================\n"
    grep -v EXTERNAL "$GRAPH" | \
        awk -F'[\\[\\]]' '{print $2}' | \
        awk -F'/' '{
            if ($(NF-1) == "arch")
                print "Architecture-specific"
            else if ($(NF-1) == "kernel")
                print "Core Kernel"
            else if ($(NF-1) == "include")
                print "Headers/Interfaces"
            else
                print "Other"
        }' | \
        sort | uniq -c | sort -rn | \
        awk '{printf "%-25s : %3d functions\n", $2, $1}'
    printf "\n"

    # Depth analysis
    printf "CALL DEPTH DISTRIBUTION:\n"
    printf "========================\n"
    printf "Layer 0 (Entry): kmain\n"
    printf "Layer 1: %d functions\n" "$(grep "^kmain -> " "$GRAPH" | wc -l)"
    printf "Layer 2+: Distributed across subsystems\n"
    printf "\n"

    # Key files
    printf "KEY SOURCE FILES (Top 10):\n"
    printf "==========================\n"
    grep -v EXTERNAL "$GRAPH" | \
        awk -F'[\\[\\]]' '{print $2}' | \
        sort | uniq -c | sort -rn | head -10 | \
        awk '{printf "%3d functions in %s\n", $1, $2}'
    printf "\n"

    # Bottleneck analysis
    printf "BOTTLENECK ANALYSIS:\n"
    printf "====================\n"
    printf "Functions with high fan-out (complexity hotspots):\n"
    cut -d' ' -f1 "$GRAPH" | sort | uniq -c | sort -rn | head -5 | \
        awk '{if ($1 > 5) printf "  • %s: %d outgoing calls (HIGH COMPLEXITY)\n", $2, $1}'
    printf "\n"

    # Modularity score (simplified)
    unique_files=$(grep -v EXTERNAL "$GRAPH" | awk -F'[\\[\\]]' '{print $2}' | sort -u | wc -l)
    printf "MODULARITY METRICS:\n"
    printf "===================\n"
    printf "Unique source files: %d\n" "$unique_files"
    printf "Functions per file (avg): %.2f\n" \
        "$(echo "scale=2; $total_funcs / $unique_files" | bc)"
    printf "Modularity score: %s\n" \
        "$(if [ "$unique_files" -gt 10 ]; then echo "HIGH (good separation)"; else echo "MEDIUM"; fi)"
    printf "\n"

} > "$OUTPUT"

printf "Analysis complete: %s\n" "$OUTPUT"
cat "$OUTPUT"
