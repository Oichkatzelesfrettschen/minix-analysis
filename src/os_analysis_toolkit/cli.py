#!/usr/bin/env python3
"""
Command-line interface for OS Analysis Toolkit
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from .parallel.executor import ParallelAnalysisPipeline
# Dashboard import moved to lazy-load (requires dash, which may not be installed)
# from .dashboard.app import run_dashboard
from shared.mcp.server import MinixAnalysisServer, MinixDataLoader


def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="OS Analysis Toolkit - Comprehensive OS source code analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  os-analyze --source /path/to/minix --output results/
  os-analyze --dashboard results/
  os-analyze --benchmark
  os-analyze --parallel --workers 8
        """
    )

    # Main commands
    parser.add_argument(
        '--source', '-s',
        help='Path to OS source code'
    )
    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory for results (default: output)'
    )

    # Analysis options
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Use parallel processing'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        help='Number of parallel workers'
    )
    parser.add_argument(
        '--cache',
        action='store_true',
        help='Enable caching'
    )

    # Dashboard
    parser.add_argument(
        '--dashboard', '-d',
        help='Launch dashboard with data directory'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Dashboard port (default: 8050)'
    )

    # Benchmarking
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        help='Run benchmark suite'
    )

    # MCP data access
    parser.add_argument(
        '--data-dir',
        default='diagrams/data',
        help='Directory containing analysis JSON outputs (default: diagrams/data)'
    )
    parser.add_argument(
        '--resource',
        choices=[
            'kernel_structure',
            'process_table',
            'memory_layout',
            'ipc_system',
            'boot_sequence',
            'statistics',
        ],
        help='Print a specific analysis resource to stdout'
    )
    parser.add_argument(
        '--boot-aspect',
        choices=['all', 'topology', 'phases', 'critical_path', 'metrics', 'infinite_loop'],
        default='all',
        help='When using --resource boot_sequence, restrict output to a specific aspect'
    )
    parser.add_argument(
        '--syscall',
        help='Lookup details for a specific syscall by name using analysis data'
    )
    parser.add_argument(
        '--list-resources',
        action='store_true',
        help='List all available analysis resources from the data directory'
    )
    parser.add_argument(
        '--kernel-summary',
        action='store_true',
        help='Print aggregated kernel summary (includes top syscalls)'
    )
    parser.add_argument(
        '--boot-critical-path',
        action='store_true',
        help='Print the boot sequence critical path'
    )
    parser.add_argument(
        '--top-syscalls',
        type=int,
        default=5,
        help='Number of top syscalls to include in kernel summary (default: 5)'
    )

    # MCP feature parity commands
    parser.add_argument(
        '--query-architecture',
        action='store_true',
        help='Query microkernel architecture overview and top syscalls'
    )
    parser.add_argument(
        '--compare-mechanisms',
        action='store_true',
        help='Compare syscall mechanisms (INT vs SYSENTER vs SYSCALL)'
    )
    parser.add_argument(
        '--explain-diagram',
        metavar='NAME',
        help='Get explanation/notes for a specific diagram'
    )
    parser.add_argument(
        '--query-boot',
        action='store_true',
        help='Query boot sequence data'
    )
    parser.add_argument(
        '--trace-boot',
        metavar='PHASE',
        help='Trace boot execution path through specific phase'
    )

    # Other options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='OS Analysis Toolkit 1.0.0'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Helper to initialise shared server interface lazily
    def _init_server() -> MinixAnalysisServer:
        loader = MinixDataLoader(Path(args.data_dir))
        return MinixAnalysisServer(loader=loader)

    # Handle different commands
    if args.dashboard:
        # Launch dashboard (lazy-import to avoid hard dependency)
        try:
            from .dashboard.app import run_dashboard
            print(f"Starting dashboard on port {args.port}...")
            run_dashboard(args.dashboard, port=args.port)
        except ImportError:
            print("Dashboard requires 'dash' module. Install with: pip install dash")
            sys.exit(1)

    elif (
        args.list_resources
        or args.resource
        or args.syscall
        or args.kernel_summary
        or args.boot_critical_path
        or args.query_architecture
        or args.compare_mechanisms
        or args.explain_diagram
        or args.query_boot
        or args.trace_boot
    ):
        server = _init_server()
        if args.kernel_summary:
            summary = server.query_architecture(top_n=args.top_syscalls)
            print(json.dumps(summary, indent=2))
            return
        if args.boot_critical_path:
            payload = server.query_boot_sequence(aspect='critical_path')
            print(json.dumps(payload, indent=2))
            return
        if args.list_resources:
            payload = server.list_resources()
            print(json.dumps(payload, indent=2))
            return
        if args.syscall:
            details = server.analyze_syscall(args.syscall)
            if not details:
                print(json.dumps({"error": f"Syscall '{args.syscall}' not found."}, indent=2))
                sys.exit(1)
            print(json.dumps(details, indent=2))
            return
        if args.resource:
            if args.resource == 'boot_sequence':
                payload = server.query_boot_sequence(aspect=args.boot_aspect)
            elif args.resource == 'kernel_structure':
                payload = server.loader.kernel_structure
            elif args.resource == 'process_table':
                payload = server.loader.process_table
            elif args.resource == 'memory_layout':
                payload = server.loader.memory_layout
            elif args.resource == 'ipc_system':
                payload = server.loader.ipc_system
            elif args.resource == 'statistics':
                payload = server.loader.statistics
            else:
                raise ValueError(f"Unhandled resource: {args.resource}")
            print(json.dumps(payload, indent=2))
            return
        if args.query_architecture:
            result = server.query_architecture(top_n=args.top_syscalls)
            print(json.dumps(result, indent=2))
            return
        if args.compare_mechanisms:
            result = server.compare_mechanisms()
            print(json.dumps(result, indent=2))
            return
        if args.explain_diagram:
            result = server.explain_diagram(args.explain_diagram)
            print(result or f"No explanation available for diagram: {args.explain_diagram}")
            return
        if args.query_boot:
            aspect = getattr(args, 'boot_aspect', 'all') or 'all'
            result = server.query_boot_sequence(aspect=aspect)
            print(json.dumps(result, indent=2))
            return
        if args.trace_boot:
            result = server.trace_boot_path(args.trace_boot)
            if not result:
                print(json.dumps({"error": f"Phase '{args.trace_boot}' not found"}, indent=2))
                sys.exit(1)
            print(json.dumps(result, indent=2))
            return

    elif args.benchmark:
        # Run benchmarks
        sys.path.append(str(Path(__file__).parent.parent.parent / "benchmarks"))
        from benchmark_suite import run_standard_benchmarks
        print("Running benchmark suite...")
        run_standard_benchmarks()

    elif args.source:
        # Run analysis
        if args.parallel:
            # Use parallel pipeline
            print(f"Running parallel analysis with {args.workers or 'auto'} workers...")
            pipeline = ParallelAnalysisPipeline(args.source, args.output)
            results = pipeline.run_complete_analysis()
        else:
            # Use sequential analysis
            print("Running sequential analysis...")
            # This would use the actual analyzer implementation
            print(f"Analyzing {args.source}")
            print(f"Output will be saved to {args.output}")

        print("Analysis complete!")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
