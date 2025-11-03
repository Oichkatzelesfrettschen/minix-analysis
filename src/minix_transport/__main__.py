"""
MINIX Analysis MCP Server
Wraps MinixAnalysisServer and exposes tools via MCP stdio transport
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Configure path to find shared.mcp.server
MINIX_ANALYSIS_ROOT = Path("/home/eirikr/Playground/minix-analysis")
if str(MINIX_ANALYSIS_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(MINIX_ANALYSIS_ROOT / "src"))

# Change to minix-analysis directory for relative paths
os.chdir(str(MINIX_ANALYSIS_ROOT))

from mcp.server import Server, stdio_server
from shared.mcp.server import MinixAnalysisServer

# Configure logging to stderr (stdout reserved for MCP)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("minix-mcp-transport")

# Initialize shared analysis server
logger.info(f"Initializing MinixAnalysisServer from {MINIX_ANALYSIS_ROOT / 'diagrams/data'}")
minix_server = MinixAnalysisServer.from_default_data_dir()
logger.info(f"✓ Microkernel: {minix_server.query_architecture()['microkernel']}")

# Create MCP server instance
mcp = Server("minix-analysis")
logger.info("✓ MCP server instance created")


# CPU-Centric Tools

@mcp.tool()
async def query_architecture(top_n: int = 5) -> str:
    """Query MINIX microkernel architecture overview and top syscalls."""
    result = minix_server.query_architecture(top_n=top_n)
    return json.dumps(result, indent=2)


@mcp.tool()
async def analyze_syscall(name: str) -> str:
    """Analyze a specific syscall by name."""
    result = minix_server.analyze_syscall(name)
    if not result:
        return json.dumps({"error": f"Syscall '{name}' not found"}, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
async def query_performance() -> str:
    """Get performance statistics from analysis."""
    result = minix_server.query_performance()
    return json.dumps(result, indent=2)


@mcp.tool()
async def compare_mechanisms() -> str:
    """Compare syscall mechanisms (INT vs SYSENTER vs SYSCALL)."""
    result = minix_server.compare_mechanisms()
    return json.dumps(result, indent=2)


@mcp.tool()
async def explain_diagram(diagram_name: str) -> str:
    """Get explanation/notes for a specific diagram."""
    result = minix_server.explain_diagram(diagram_name)
    return result or f"No explanation available for diagram: {diagram_name}"


# Boot-Centric Tools

@mcp.tool()
async def query_boot_sequence(aspect: str = "all") -> str:
    """Query boot sequence data by aspect."""
    result = minix_server.query_boot_sequence(aspect=aspect)
    return json.dumps(result, indent=2)


@mcp.tool()
async def trace_boot_path(phase_name: str = "all") -> str:
    """Trace boot execution path through specific phase(s)."""
    result = minix_server.trace_boot_path(phase_name)
    if not result:
        return json.dumps({"error": f"Phase '{phase_name}' not found"}, indent=2)
    return json.dumps(result, indent=2)


# Resources

@mcp.resource("minix://kernel/structure")
async def get_kernel_structure() -> str:
    """Access kernel structure data."""
    return json.dumps(minix_server.loader.kernel_structure, indent=2)


@mcp.resource("minix://boot/sequence")
async def get_boot_sequence() -> str:
    """Access boot sequence data."""
    return json.dumps(minix_server.loader.boot_sequence, indent=2)


# Main

async def main():
    """Run MCP transport server."""
    logger.info("Starting MINIX Analysis MCP server...")
    async with stdio_server(mcp) as streams:
        logger.info("✓ Ready for MCP requests")
        await streams.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
