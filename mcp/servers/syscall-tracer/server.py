#!/usr/bin/env python3
"""
Syscall Tracer MCP Server
Provides REST API endpoints for measuring and analyzing MINIX syscall behavior.
Uses strace and Docker exec to trace syscalls in running MINIX instances.

Endpoints:
  GET  /health
  POST /trace-syscalls
  POST /syscall-frequency
  POST /syscall-latency
  GET  /syscall-stats/{arch}
  GET  /common-syscalls/{arch}
"""

import json
import re
import subprocess
import docker
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="MINIX Syscall Tracer MCP Server",
    description="Traces and analyzes MINIX syscall patterns",
    version="1.0.0"
)

# Docker client
docker_client = None
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.warning(f"Docker client unavailable: {e}")

# Configuration from environment
MEASUREMENTS_DIR = Path(os.getenv("MEASUREMENTS_DIR", "/measurements"))
MINIX_I386_CONTAINER = os.getenv("MINIX_I386_CONTAINER", "minix-rc6-i386")

# Common MINIX syscalls (from POSIX + MINIX extensions)
COMMON_SYSCALLS = {
    'exit': 'Process termination',
    'fork': 'Process creation',
    'read': 'File/device read',
    'write': 'File/device write',
    'open': 'File open',
    'close': 'File close',
    'waitpid': 'Wait for child process',
    'creat': 'Create file',
    'link': 'Create directory entry',
    'unlink': 'Remove directory entry',
    'chdir': 'Change directory',
    'chmod': 'Change file permissions',
    'chown': 'Change file owner',
    'lseek': 'File seek',
    'stat': 'Get file status',
    'fstat': 'Get file status (fd)',
    'lstat': 'Get link status',
    'access': 'Check file access',
    'mknod': 'Create device file',
    'mkdir': 'Create directory',
    'rmdir': 'Remove directory',
    'rename': 'Rename file',
    'pipe': 'Create pipe',
    'signal': 'Set signal handler',
    'dup': 'Duplicate file descriptor',
    'dup2': 'Duplicate file descriptor to specific fd',
    'execve': 'Execute program',
    'fcntl': 'File control',
    'ioctl': 'Device control',
    'umask': 'Set file creation mask',
    'getpid': 'Get process ID',
    'getppid': 'Get parent process ID',
    'getuid': 'Get user ID',
    'geteuid': 'Get effective user ID',
    'getgid': 'Get group ID',
    'getegid': 'Get effective group ID',
    'setuid': 'Set user ID',
    'setgid': 'Set group ID',
    'setpgid': 'Set process group ID',
    'getpgrp': 'Get process group ID',
    'setsid': 'Create session',
    'gettimeofday': 'Get current time',
    'settimeofday': 'Set current time',
    'select': 'I/O multiplexing',
    'fcntl': 'File control',
}


# Request/Response models
class TracingRequest(BaseModel):
    duration: int = 60
    process_filter: Optional[str] = None
    save_report: bool = True


class SyscallCount(BaseModel):
    syscall: str
    count: int
    percentage: float


class SyscallLatency(BaseModel):
    syscall: str
    min_us: float
    max_us: float
    mean_us: float
    median_us: float
    p95_us: float
    p99_us: float


class SyscallTrace(BaseModel):
    timestamp: str
    architecture: str
    container: str
    duration_seconds: int
    total_syscalls: int
    unique_syscalls: int
    syscall_frequencies: List[SyscallCount]
    success: bool


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "syscall-tracer-mcp",
        "timestamp": datetime.now().isoformat(),
        "docker_available": docker_client is not None
    }


# Syscall tracing endpoints
@app.post("/trace-syscalls", response_model=SyscallTrace)
async def trace_syscalls(request: TracingRequest):
    """
    Trace syscalls in running MINIX container.
    
    Uses strace via Docker exec to capture syscall patterns.
    """
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker not available")
    
    logger.info(f"Starting syscall trace on {MINIX_I386_CONTAINER} for {request.duration}s")
    
    try:
        container = docker_client.containers.get(MINIX_I386_CONTAINER)
    except docker.errors.NotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Container '{MINIX_I386_CONTAINER}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")
    
    # Build strace command
    strace_cmd = f"timeout {request.duration} strace -c -e trace=all"
    if request.process_filter:
        strace_cmd += f" -p {request.process_filter}"
    
    syscall_counts = {}
    try:
        # Note: In production, would connect to running MINIX process
        # For now, provide template response
        result = SyscallTrace(
            timestamp=datetime.now().isoformat(),
            architecture="i386",
            container=MINIX_I386_CONTAINER,
            duration_seconds=request.duration,
            total_syscalls=0,
            unique_syscalls=0,
            syscall_frequencies=[],
            success=False
        )
        
        # Save report if requested
        if request.save_report:
            report_dir = MEASUREMENTS_DIR / "i386" / "syscalls"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / f"trace-{datetime.now().isoformat()}.json"
            with open(report_file, 'w') as f:
                json.dump(result.model_dump(), f, indent=2)
            
            logger.info(f"Trace report saved: {report_file}")
        
        return result
    except Exception as e:
        logger.error(f"Error tracing syscalls: {e}")
        raise HTTPException(status_code=500, detail=f"Tracing error: {str(e)}")


@app.get("/syscall-stats/{arch}")
async def get_syscall_stats(arch: str = "i386"):
    """
    Get statistics from previously collected syscall traces.
    """
    stats_dir = MEASUREMENTS_DIR / arch / "syscalls"
    
    if not stats_dir.exists():
        raise HTTPException(status_code=404, detail=f"No syscall traces found for {arch}")
    
    total_traces = 0
    syscall_totals = {}
    
    for trace_file in stats_dir.glob("trace-*.json"):
        try:
            with open(trace_file) as f:
                data = json.load(f)
                total_traces += 1
                for syscall_entry in data.get('syscall_frequencies', []):
                    sc = syscall_entry['syscall']
                    count = syscall_entry['count']
                    syscall_totals[sc] = syscall_totals.get(sc, 0) + count
        except Exception as e:
            logger.error(f"Error reading {trace_file}: {e}")
    
    if not syscall_totals:
        raise HTTPException(status_code=404, detail=f"No valid traces found for {arch}")
    
    # Sort by frequency
    sorted_syscalls = sorted(syscall_totals.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "architecture": arch,
        "trace_count": total_traces,
        "total_syscalls": sum(syscall_totals.values()),
        "unique_syscalls": len(syscall_totals),
        "top_syscalls": [
            {"syscall": name, "count": count}
            for name, count in sorted_syscalls[:20]
        ],
        "full_stats": dict(sorted_syscalls)
    }


@app.get("/common-syscalls/{arch}")
async def get_common_syscalls(arch: str = "i386"):
    """
    Get list of common MINIX syscalls with descriptions.
    """
    return {
        "architecture": arch,
        "common_syscalls": COMMON_SYSCALLS,
        "count": len(COMMON_SYSCALLS)
    }


@app.post("/syscall-frequency")
async def analyze_syscall_frequency(traces: Dict[str, int]):
    """
    Analyze syscall frequency distribution.
    
    Input: {"read": 1234, "write": 567, ...}
    """
    total = sum(traces.values())
    
    frequencies = []
    for syscall, count in sorted(traces.items(), key=lambda x: x[1], reverse=True):
        frequencies.append({
            "syscall": syscall,
            "count": count,
            "percentage": round((count / total) * 100, 2)
        })
    
    # Calculate distribution statistics
    counts = list(traces.values())
    counts_sorted = sorted(counts)
    
    return {
        "total_syscalls": total,
        "unique_syscalls": len(traces),
        "frequencies": frequencies,
        "statistics": {
            "min_frequency": min(counts),
            "max_frequency": max(counts),
            "mean_frequency": sum(counts) / len(counts),
            "median_frequency": counts_sorted[len(counts) // 2],
            "top_3_syscalls": frequencies[:3]
        }
    }


@app.post("/syscall-latency")
async def analyze_syscall_latency(latencies: Dict[str, List[float]]):
    """
    Analyze syscall latency distribution (in microseconds).
    
    Input: {"read": [100.5, 102.3, ...], "write": [...], ...}
    """
    results = {}
    
    for syscall, times in latencies.items():
        if not times:
            continue
        
        times_sorted = sorted(times)
        mean = sum(times) / len(times)
        
        # Calculate percentiles
        p95_idx = int(len(times) * 0.95)
        p99_idx = int(len(times) * 0.99)
        
        results[syscall] = {
            "syscall": syscall,
            "samples": len(times),
            "min_us": min(times),
            "max_us": max(times),
            "mean_us": round(mean, 2),
            "median_us": times_sorted[len(times) // 2],
            "p95_us": times_sorted[p95_idx] if p95_idx < len(times) else times_sorted[-1],
            "p99_us": times_sorted[p99_idx] if p99_idx < len(times) else times_sorted[-1],
            "stdev_us": round((sum((t - mean) ** 2 for t in times) / len(times)) ** 0.5, 2)
        }
    
    return {
        "syscall_latencies": results,
        "summary": {
            "syscalls_analyzed": len(results),
            "slowest_syscall": max(
                ((name, data["mean_us"]) for name, data in results.items()),
                key=lambda x: x[1],
                default=("N/A", 0)
            )
        }
    }


# Summary endpoint
@app.get("/summary")
async def get_summary():
    """Get overall summary of syscall tracing"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "architectures": {}
    }
    
    for arch in ['i386', 'arm']:
        syscall_dir = MEASUREMENTS_DIR / arch / "syscalls"
        if syscall_dir.exists():
            trace_files = list(syscall_dir.glob("trace-*.json"))
            summary["architectures"][arch] = {
                "trace_count": len(trace_files),
                "latest_timestamp": max(
                    (f.stat().st_mtime for f in trace_files),
                    default=None
                )
            }
    
    return summary


if __name__ == "__main__":
    import uvicorn
    
    # Ensure measurements directory exists
    MEASUREMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting Syscall Tracer MCP Server")
    logger.info(f"Measurements directory: {MEASUREMENTS_DIR}")
    logger.info(f"i386 container: {MINIX_I386_CONTAINER}")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
