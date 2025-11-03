#!/usr/bin/env python3
"""
Boot Profiler MCP Server
Provides REST API endpoints for measuring MINIX boot timeline.
Integrates with Claude Code via HTTP for real-time boot profiling.

Endpoints:
  GET  /health
  POST /measure-boot-i386
  POST /measure-boot-arm
  POST /compare-timings
  GET  /measurements/{arch}
  GET  /whitepaper-estimates
"""

import json
import re
import time
import subprocess
import docker
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="MINIX Boot Profiler MCP Server",
    description="Measures and analyzes MINIX boot timelines",
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
MINIX_ARM_CONTAINER = os.getenv("MINIX_ARM_CONTAINER", "minix-rc6-arm")

# Boot marker definitions
BOOT_MARKERS = {
    'multiboot_detected': (r'Booting.*multiboot|MINIX.*boot', 'Multiboot detected'),
    'kernel_starts': (r'Initializing.*kernel|MINIX 3', 'Kernel initialization'),
    'pre_init_phase': (r'pre_init|Virtual memory', 'pre_init() phase'),
    'kmain_phase': (r'kmain\(|Main boot hub', 'kmain() orchestration'),
    'cstart_phase': (r'cstart\(|CPU descriptor', 'cstart() CPU setup'),
    'process_init': (r'Process table|proc_init', 'Process initialization'),
    'memory_init': (r'memory_init|Memory allocator', 'Memory system init'),
    'system_init': (r'system_init|Exception handlers', 'System init'),
    'scheduler_ready': (r'Scheduler.*ready|Scheduling|Ready to run', 'Scheduler ready'),
    'shell_prompt': (r'[$#%>]|login:', 'Shell prompt'),
}

# Whitepaper estimates (milliseconds)
WHITEPAPER_ESTIMATES = {
    'i386': {'total': 65, 'kernel': 35, 'units': 'ms'},
    'arm': {'total': 56, 'kernel': 28, 'units': 'ms'},
}


# Request/Response models
class MeasurementRequest(BaseModel):
    arch: str = "i386"
    timeout: int = 120
    save_report: bool = True


class BootMeasurement(BaseModel):
    timestamp: str
    architecture: str
    container: str
    boot_markers: Dict[str, float]
    total_time_ms: float
    marker_count: int
    success: bool


class WhitepaperComparison(BaseModel):
    architecture: str
    measured_ms: float
    estimated_ms: float
    error_percent: float
    status: str  # VERIFIED, PLAUSIBLE, NEEDS_VALIDATION


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "boot-profiler-mcp",
        "timestamp": datetime.now().isoformat(),
        "docker_available": docker_client is not None
    }


# Boot measurement endpoints
@app.post("/measure-boot-i386", response_model=BootMeasurement)
async def measure_boot_i386(request: MeasurementRequest):
    """Measure i386 MINIX boot timeline"""
    return await measure_boot(MINIX_I386_CONTAINER, "i386", request.timeout, request.save_report)


@app.post("/measure-boot-arm", response_model=BootMeasurement)
async def measure_boot_arm(request: MeasurementRequest):
    """Measure ARM MINIX boot timeline"""
    return await measure_boot(MINIX_ARM_CONTAINER, "arm", request.timeout, request.save_report)


async def measure_boot(container_name: str, arch: str, timeout: int = 120, save_report: bool = True):
    """
    Core boot measurement logic.
    
    Monitors Docker container logs for boot markers and measures elapsed time.
    """
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker not available")
    
    logger.info(f"Starting boot measurement for {arch} ({container_name})")
    
    start_time = time.time()
    boot_markers = {}
    
    try:
        # Get container
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Container '{container_name}' not found. Ensure Docker Compose infrastructure is running."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")
    
    # Monitor container logs for boot markers
    for elapsed in range(timeout):
        try:
            logs = container.logs().decode('utf-8', errors='ignore')
            
            # Check for markers
            for marker_key, (pattern, description) in BOOT_MARKERS.items():
                if marker_key not in boot_markers:
                    if re.search(pattern, logs, re.IGNORECASE | re.MULTILINE):
                        marker_time = time.time() - start_time
                        boot_markers[marker_key] = marker_time
                        logger.info(f"  ✓ {description}: {marker_time:.2f}s")
            
            # Exit if all markers found
            if len(boot_markers) >= 7:
                break
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error reading container logs: {e}")
            break
    
    # Prepare response
    total_time = boot_markers.get('scheduler_ready', time.time() - start_time)
    measurement = BootMeasurement(
        timestamp=datetime.now().isoformat(),
        architecture=arch,
        container=container_name,
        boot_markers=boot_markers,
        total_time_ms=total_time * 1000,
        marker_count=len(boot_markers),
        success=len(boot_markers) >= 5
    )
    
    # Save report if requested
    if save_report:
        report_dir = MEASUREMENTS_DIR / arch
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"boot-{datetime.now().isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(measurement.model_dump(), f, indent=2)
        
        logger.info(f"Report saved: {report_file}")
    
    return measurement


# Comparison endpoints
@app.get("/whitepaper-estimates")
async def get_whitepaper_estimates():
    """Get whitepaper boot time estimates"""
    return {
        "estimates": WHITEPAPER_ESTIMATES,
        "units": "milliseconds",
        "source": "MINIX 3.4 Technical Whitepaper"
    }


@app.post("/compare-timings")
async def compare_timings(measurements: Dict[str, float]):
    """
    Compare measured boot times against whitepaper estimates.
    
    Input: {"i386": 67.5, "arm": 54.2}  (in ms)
    """
    results = {}
    
    for arch, measured_ms in measurements.items():
        if arch not in WHITEPAPER_ESTIMATES:
            continue
        
        estimate = WHITEPAPER_ESTIMATES[arch]['total']
        error_percent = abs(measured_ms - estimate) / estimate * 100
        
        # Determine status
        if error_percent < 10:
            status = "VERIFIED"
        elif error_percent < 20:
            status = "PLAUSIBLE"
        else:
            status = "NEEDS_VALIDATION"
        
        results[arch] = WhitepaperComparison(
            architecture=arch,
            measured_ms=measured_ms,
            estimated_ms=estimate,
            error_percent=round(error_percent, 1),
            status=status
        )
    
    return results


# Data retrieval endpoints
@app.get("/measurements/{arch}")
async def get_measurements(arch: str):
    """Retrieve all measurements for a given architecture"""
    arch_dir = MEASUREMENTS_DIR / arch
    
    if not arch_dir.exists():
        raise HTTPException(status_code=404, detail=f"No measurements found for {arch}")
    
    measurements = []
    for measurement_file in sorted(arch_dir.glob("boot-*.json"), reverse=True)[:10]:
        try:
            with open(measurement_file) as f:
                measurements.append(json.load(f))
        except Exception as e:
            logger.error(f"Error reading {measurement_file}: {e}")
    
    return {
        "architecture": arch,
        "measurement_count": len(measurements),
        "measurements": measurements
    }


@app.get("/statistics/{arch}")
async def get_statistics(arch: str):
    """Calculate statistics from measurements"""
    arch_dir = MEASUREMENTS_DIR / arch
    
    if not arch_dir.exists():
        raise HTTPException(status_code=404, detail=f"No measurements found for {arch}")
    
    times = []
    for measurement_file in arch_dir.glob("boot-*.json"):
        try:
            with open(measurement_file) as f:
                data = json.load(f)
                if 'total_time_ms' in data:
                    times.append(data['total_time_ms'])
        except Exception as e:
            logger.error(f"Error reading {measurement_file}: {e}")
    
    if not times:
        raise HTTPException(status_code=404, detail=f"No valid measurements found for {arch}")
    
    times_sorted = sorted(times)
    return {
        "architecture": arch,
        "sample_count": len(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": sum(times) / len(times),
        "median_ms": times_sorted[len(times) // 2],
        "stdev_ms": (sum((t - sum(times) / len(times)) ** 2 for t in times) / len(times)) ** 0.5,
        "whitepaper_estimate_ms": WHITEPAPER_ESTIMATES[arch]['total'],
        "whitepaper_error_percent": round(
            abs((sum(times) / len(times)) - WHITEPAPER_ESTIMATES[arch]['total']) /
            WHITEPAPER_ESTIMATES[arch]['total'] * 100, 1
        )
    }


# Summary endpoint
@app.get("/summary")
async def get_summary():
    """Get overall summary of all measurements"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "architectures": {},
        "whitepaper_estimates": WHITEPAPER_ESTIMATES
    }
    
    for arch in ['i386', 'arm']:
        arch_dir = MEASUREMENTS_DIR / arch
        if arch_dir.exists():
            measurement_files = list(arch_dir.glob("boot-*.json"))
            summary["architectures"][arch] = {
                "measurement_count": len(measurement_files),
                "latest_timestamp": max(
                    (f.stat().st_mtime for f in measurement_files),
                    default=None
                )
            }
    
    return summary


if __name__ == "__main__":
    import uvicorn
    
    # Ensure measurements directory exists
    MEASUREMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting Boot Profiler MCP Server")
    logger.info(f"Measurements directory: {MEASUREMENTS_DIR}")
    logger.info(f"i386 container: {MINIX_I386_CONTAINER}")
    logger.info(f"ARM container: {MINIX_ARM_CONTAINER}")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
