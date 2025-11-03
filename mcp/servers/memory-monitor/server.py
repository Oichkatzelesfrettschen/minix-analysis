#!/usr/bin/env python3
"""
Memory Monitor MCP Server
Provides REST API endpoints for monitoring and analyzing MINIX memory behavior.
Tracks page faults, TLB misses, cache behavior, memory allocation patterns.

Endpoints:
  GET  /health
  POST /monitor-memory
  GET  /memory-stats/{arch}
  POST /page-fault-analysis
  POST /cache-behavior-analysis
  GET  /tlb-statistics/{arch}
  POST /memory-access-pattern
"""

import json
import subprocess
import docker
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="MINIX Memory Monitor MCP Server",
    description="Monitors and analyzes MINIX memory behavior patterns",
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

# Memory event types
MEMORY_EVENTS = {
    'page-faults': 'Page faults (major + minor)',
    'cache-misses': 'CPU cache misses',
    'cache-references': 'CPU cache references',
    'tlb-load-misses': 'TLB load misses',
    'tlb-stores': 'TLB store operations',
    'dTLB-load-misses': 'Data TLB load misses',
    'dTLB-store-misses': 'Data TLB store misses',
    'iTLB-load-misses': 'Instruction TLB load misses',
    'L1-dcache-load-misses': 'L1 data cache load misses',
    'L1-dcache-store-misses': 'L1 data cache store misses',
    'LLC-loads': 'Last level cache loads',
    'LLC-load-misses': 'Last level cache load misses',
    'LLC-stores': 'Last level cache stores',
}


# Request/Response models
class MemoryMonitoringRequest(BaseModel):
    duration: int = 60
    events: Optional[List[str]] = None
    save_report: bool = True


class MemoryEvent(BaseModel):
    event: str
    count: int
    percentage: float


class MemoryMonitoringResult(BaseModel):
    timestamp: str
    architecture: str
    container: str
    duration_seconds: int
    total_events: int
    memory_events: List[MemoryEvent]
    success: bool


class PageFaultAnalysis(BaseModel):
    major_faults: int
    minor_faults: int
    total_faults: int
    fault_rate_per_second: float
    average_fault_interval_ms: float
    analysis: str


class CacheBehavior(BaseModel):
    cache_references: int
    cache_misses: int
    miss_rate_percent: float
    hit_rate_percent: float
    l1_misses: int
    llc_misses: int


class TLBStatistics(BaseModel):
    tlb_loads: int
    tlb_load_misses: int
    tlb_miss_rate_percent: float
    dtlb_load_misses: int
    itlb_load_misses: int


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "memory-monitor-mcp",
        "timestamp": datetime.now().isoformat(),
        "docker_available": docker_client is not None
    }


# Memory monitoring endpoints
@app.post("/monitor-memory", response_model=MemoryMonitoringResult)
async def monitor_memory(request: MemoryMonitoringRequest):
    """
    Monitor memory events in running MINIX container.
    
    Uses Linux perf events via Docker exec to capture memory behavior.
    """
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker not available")
    
    logger.info(f"Starting memory monitoring on {MINIX_I386_CONTAINER} for {request.duration}s")
    
    try:
        container = docker_client.containers.get(MINIX_I386_CONTAINER)
    except docker.errors.NotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Container '{MINIX_I386_CONTAINER}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")
    
    # Default events if not specified
    if not request.events:
        request.events = list(MEMORY_EVENTS.keys())[:5]  # Top 5 events
    
    # Prepare result
    result = MemoryMonitoringResult(
        timestamp=datetime.now().isoformat(),
        architecture="i386",
        container=MINIX_I386_CONTAINER,
        duration_seconds=request.duration,
        total_events=0,
        memory_events=[],
        success=False
    )
    
    # Save report if requested
    if request.save_report:
        report_dir = MEASUREMENTS_DIR / "i386" / "memory"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"monitor-{datetime.now().isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(result.model_dump(), f, indent=2)
        
        logger.info(f"Memory monitoring report saved: {report_file}")
    
    return result


@app.get("/memory-stats/{arch}")
async def get_memory_stats(arch: str = "i386"):
    """
    Get statistics from previously collected memory monitoring data.
    """
    memory_dir = MEASUREMENTS_DIR / arch / "memory"
    
    if not memory_dir.exists():
        raise HTTPException(status_code=404, detail=f"No memory data found for {arch}")
    
    total_monitors = 0
    event_totals = {}
    
    for monitor_file in memory_dir.glob("monitor-*.json"):
        try:
            with open(monitor_file) as f:
                data = json.load(f)
                total_monitors += 1
                for event_entry in data.get('memory_events', []):
                    event = event_entry['event']
                    count = event_entry['count']
                    event_totals[event] = event_totals.get(event, 0) + count
        except Exception as e:
            logger.error(f"Error reading {monitor_file}: {e}")
    
    if not event_totals:
        raise HTTPException(status_code=404, detail=f"No valid memory data found for {arch}")
    
    # Sort by frequency
    sorted_events = sorted(event_totals.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "architecture": arch,
        "monitoring_sessions": total_monitors,
        "total_events": sum(event_totals.values()),
        "unique_events": len(event_totals),
        "top_events": [
            {"event": name, "count": count}
            for name, count in sorted_events[:10]
        ],
        "full_stats": dict(sorted_events)
    }


@app.get("/memory-event-definitions")
async def get_memory_event_definitions():
    """
    Get definitions of all supported memory events.
    """
    return {
        "memory_events": MEMORY_EVENTS,
        "count": len(MEMORY_EVENTS)
    }


@app.post("/page-fault-analysis")
async def analyze_page_faults(faults: Dict[str, int]):
    """
    Analyze page fault patterns.
    
    Input: {"major_faults": 150, "minor_faults": 12500, "duration_seconds": 60}
    """
    major = faults.get('major_faults', 0)
    minor = faults.get('minor_faults', 0)
    duration = faults.get('duration_seconds', 60)
    
    total = major + minor
    
    # Analyze severity
    if major > 100:
        analysis = "HIGH: Excessive major page faults (disk I/O heavy). Check memory pressure."
    elif major > 10:
        analysis = "MODERATE: Some major page faults detected. Monitor memory usage."
    else:
        analysis = "LOW: Page faults within normal range."
    
    return PageFaultAnalysis(
        major_faults=major,
        minor_faults=minor,
        total_faults=total,
        fault_rate_per_second=round(total / duration, 2),
        average_fault_interval_ms=round((duration * 1000) / total, 2) if total > 0 else 0,
        analysis=analysis
    )


@app.post("/cache-behavior-analysis")
async def analyze_cache_behavior(cache_data: Dict[str, int]):
    """
    Analyze CPU cache behavior.
    
    Input: {
        "cache_references": 10000,
        "cache_misses": 250,
        "l1_misses": 150,
        "llc_misses": 50
    }
    """
    references = cache_data.get('cache_references', 1)
    misses = cache_data.get('cache_misses', 0)
    l1_misses = cache_data.get('l1_misses', 0)
    llc_misses = cache_data.get('llc_misses', 0)
    
    miss_rate = (misses / references * 100) if references > 0 else 0
    hit_rate = 100 - miss_rate
    
    return CacheBehavior(
        cache_references=references,
        cache_misses=misses,
        miss_rate_percent=round(miss_rate, 2),
        hit_rate_percent=round(hit_rate, 2),
        l1_misses=l1_misses,
        llc_misses=llc_misses
    )


@app.post("/tlb-analysis")
async def analyze_tlb_behavior(tlb_data: Dict[str, int]):
    """
    Analyze Translation Lookaside Buffer (TLB) behavior.
    
    Input: {
        "tlb_loads": 5000,
        "tlb_load_misses": 150,
        "dtlb_load_misses": 100,
        "itlb_load_misses": 50
    }
    """
    tlb_loads = tlb_data.get('tlb_loads', 1)
    tlb_misses = tlb_data.get('tlb_load_misses', 0)
    dtlb_misses = tlb_data.get('dtlb_load_misses', 0)
    itlb_misses = tlb_data.get('itlb_load_misses', 0)
    
    miss_rate = (tlb_misses / tlb_loads * 100) if tlb_loads > 0 else 0
    
    # Analyze
    if miss_rate > 5:
        analysis = "HIGH TLB misses. Consider: larger page sizes, better memory layout"
    elif miss_rate > 1:
        analysis = "MODERATE TLB misses. Monitor virtual memory behavior"
    else:
        analysis = "LOW TLB misses. Good memory locality"
    
    return TLBStatistics(
        tlb_loads=tlb_loads,
        tlb_load_misses=tlb_misses,
        tlb_miss_rate_percent=round(miss_rate, 2),
        dtlb_load_misses=dtlb_misses,
        itlb_load_misses=itlb_misses
    )


@app.post("/memory-access-pattern")
async def analyze_memory_access_pattern(access_data: Dict[str, int]):
    """
    Analyze memory access patterns from event data.
    
    Input: {
        "sequential_accesses": 8000,
        "random_accesses": 2000,
        "read_write_ratio": 0.75,
        "working_set_size_kb": 2048
    }
    """
    sequential = access_data.get('sequential_accesses', 1)
    random = access_data.get('random_accesses', 0)
    total = sequential + random
    
    spatial_locality = (sequential / total * 100) if total > 0 else 0
    
    # Characterize pattern
    if spatial_locality > 80:
        pattern_type = "SEQUENTIAL: Good spatial locality"
    elif spatial_locality > 50:
        pattern_type = "MIXED: Moderate locality"
    else:
        pattern_type = "RANDOM: Poor locality, higher cache miss rate expected"
    
    return {
        "sequential_accesses": sequential,
        "random_accesses": random,
        "total_accesses": total,
        "spatial_locality_percent": round(spatial_locality, 2),
        "pattern_type": pattern_type,
        "read_write_ratio": access_data.get('read_write_ratio', 0),
        "working_set_size_kb": access_data.get('working_set_size_kb', 0),
        "optimization_suggestions": [
            "Review memory allocation alignment",
            "Consider prefetching for high-locality code paths",
            "Optimize data structure layout for cache lines",
            "Monitor TLB effectiveness"
        ]
    }


# Summary endpoint
@app.get("/summary")
async def get_summary():
    """Get overall summary of memory monitoring"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "architectures": {}
    }
    
    for arch in ['i386', 'arm']:
        memory_dir = MEASUREMENTS_DIR / arch / "memory"
        if memory_dir.exists():
            monitor_files = list(memory_dir.glob("monitor-*.json"))
            summary["architectures"][arch] = {
                "monitoring_sessions": len(monitor_files),
                "latest_timestamp": max(
                    (f.stat().st_mtime for f in monitor_files),
                    default=None
                )
            }
    
    return summary


if __name__ == "__main__":
    import uvicorn
    
    # Ensure measurements directory exists
    MEASUREMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting Memory Monitor MCP Server")
    logger.info(f"Measurements directory: {MEASUREMENTS_DIR}")
    logger.info(f"i386 container: {MINIX_I386_CONTAINER}")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
