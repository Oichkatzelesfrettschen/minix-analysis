#!/usr/bin/env python3
"""
Call Graph Generator
Converts symbol/call data into Graphviz DOT format
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class CallGraph:
    """Generate call graphs from extracted symbols and calls"""

    def __init__(self, symbols_json_path: Path = None):
        self.nodes = {}  # name -> attributes
        self.edges = []  # (caller, callee) tuples
        self.file_colors = {}  # file -> color

        if symbols_json_path:
            self.load_from_json(symbols_json_path)

    def load_from_json(self, json_path: Path):
        """Load symbols and calls from JSON"""
        data = json.loads(json_path.read_text())

        # Build nodes from symbols
        for sym in data.get('symbols', []):
            self.nodes[sym['name']] = {
                'file': sym['file'],
                'line': sym['line'],
                'kind': sym['kind']
            }

        # Build edges from calls
        for call in data.get('calls', []):
            self.edges.append((call['caller'], call['callee']))

        self._assign_colors()

    def _assign_colors(self):
        """Assign colors to files for visual distinction"""
        files = set(node['file'] for node in self.nodes.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                  '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8B739', '#52B788']

        for i, file in enumerate(sorted(files)):
            self.file_colors[file] = colors[i % len(colors)]

    def filter_by_files(self, file_patterns: List[str]):
        """Keep only nodes/edges involving specified files"""
        filtered_nodes = {
            name: attrs for name, attrs in self.nodes.items()
            if any(pattern in attrs['file'] for pattern in file_patterns)
        }

        filtered_edges = [
            (caller, callee) for caller, callee in self.edges
            if caller in filtered_nodes or callee in filtered_nodes
        ]

        self.nodes = filtered_nodes
        self.edges = filtered_edges

    def to_dot(self, title: str = "Call Graph", rankdir: str = "LR") -> str:
        """Generate Graphviz DOT format"""
        lines = []

        # Header
        lines.append(f'digraph "{title}" {{')
        lines.append(f'    rankdir={rankdir};')
        lines.append('    graph [splines=ortho, overlap=false, fontname="Latin Modern Sans"];')
        lines.append('    node [shape=box, style=filled, fontname="Latin Modern Sans", fontsize=10];')
        lines.append('    edge [fontname="Latin Modern Sans", fontsize=8];')
        lines.append('')

        # Nodes
        for name, attrs in sorted(self.nodes.items()):
            file = attrs['file']
            line = attrs['line']
            color = self.file_colors.get(file, '#CCCCCC')

            # Escape special characters
            safe_name = name.replace('"', '\\"')
            safe_file = Path(file).name  # Just filename, not full path

            label = f"{safe_name}\\n({safe_file}:{line})"

            lines.append(f'    "{safe_name}" [label="{label}", fillcolor="{color}"];')

        lines.append('')

        # Edges (deduplicate)
        edges_seen = set()
        for caller, callee in self.edges:
            edge_key = (caller, callee)
            if edge_key in edges_seen:
                continue
            edges_seen.add(edge_key)

            if caller in self.nodes and callee in self.nodes:
                safe_caller = caller.replace('"', '\\"')
                safe_callee = callee.replace('"', '\\"')
                lines.append(f'    "{safe_caller}" -> "{safe_callee}";')

        lines.append('}')

        return '\n'.join(lines)

    def save_dot(self, output_path: Path, **kwargs):
        """Save DOT format to file"""
        dot_content = self.to_dot(**kwargs)
        output_path.write_text(dot_content)
        print(f"Saved DOT to {output_path}")

    def get_statistics(self) -> Dict:
        """Compute graph statistics"""
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)

        for caller, callee in self.edges:
            out_degree[caller] += 1
            in_degree[callee] += 1

        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "top_callers": sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_callees": sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:10],
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate call graph from symbols JSON")
    parser.add_argument("symbols_json", type=Path, help="Input symbols.json from symbol_extractor")
    parser.add_argument("-o", "--output", type=Path, help="Output DOT file", required=True)
    parser.add_argument("-f", "--filter", nargs='+', help="Filter by file patterns (e.g., mpx.S klib.S)")
    parser.add_argument("-t", "--title", default="MINIX Call Graph", help="Graph title")
    parser.add_argument("-r", "--rankdir", default="LR", choices=['LR', 'TB', 'RL', 'BT'], help="Graph direction")
    parser.add_argument("-s", "--stats", action='store_true', help="Print statistics")

    args = parser.parse_args()

    graph = CallGraph(args.symbols_json)

    if args.filter:
        graph.filter_by_files(args.filter)

    graph.save_dot(args.output, title=args.title, rankdir=args.rankdir)

    if args.stats:
        stats = graph.get_statistics()
        print(f"\nGraph Statistics:")
        print(f"  Nodes: {stats['nodes']}")
        print(f"  Edges: {stats['edges']}")
        print(f"\nTop Callers:")
        for name, count in stats['top_callers']:
            print(f"  {name}: {count} calls")
        print(f"\nTop Callees:")
        for name, count in stats['top_callees']:
            print(f"  {name}: {count} calls")


if __name__ == "__main__":
    main()
