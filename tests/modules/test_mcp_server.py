import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from shared.mcp.server import MinixAnalysisServer, MinixDataLoader  # noqa: E402


@pytest.fixture()
def sample_payload():
    return {
        "kernel_structure": {
            "microkernel": True,
            "components": ["kernel", "servers", "drivers"],
            "ipc_mechanism": "message_passing",
            "system_calls": [
                {"name": "do_example_b", "file": "b.c", "line_count": 25},
                {"name": "do_example_a", "file": "a.c", "line_count": 10},
            ],
        },
        "process_table": {"processes": []},
        "memory_layout": {"segments": ["text"]},
        "ipc_system": {"mechanism": "message_passing"},
        "boot_sequence": {
            "topology": "hub-spoke",
            "graph_type": "dag",
            "central_hub": "kmain()",
            "boot_phases": [{"id": "phase1", "name": "Phase 1"}],
            "critical_path": {"length": 5},
            "metrics": {"functions": 34},
            "infinite_loop_myth": {"status": "busted"},
        },
        "statistics": {
            "total_functions": 100,
            "total_lines": 1000,
            "diagram_notes": {"syscall-table": "Syscall overview"},
        },
    }


@pytest.fixture()
def sample_data_dir(tmp_path, sample_payload):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for key, payload in sample_payload.items():
        (data_dir / f"{key}.json").write_text(json.dumps(payload), encoding="utf-8")
    return data_dir


def test_data_loader_loads_json(sample_data_dir, benchmark):
    loader = MinixDataLoader(data_dir=sample_data_dir)

    def run():
        return (
            loader.kernel_structure["microkernel"],
            loader.boot_sequence["topology"],
        )

    microkernel, topology = benchmark(run)
    assert microkernel is True
    assert topology == "hub-spoke"


def test_server_queries(sample_data_dir, benchmark):
    server = MinixAnalysisServer(loader=MinixDataLoader(sample_data_dir))

    def run():
        arch = server.query_architecture()
        syscall = server.analyze_syscall("do_example_a")
        perf = server.query_performance()
        boot = server.query_boot_sequence(aspect="topology")
        phase = server.trace_boot_path("phase1")
        resources = server.list_resources()
        return arch, syscall, perf, boot, phase, resources

    arch, syscall, perf, boot, phase, resources = benchmark(run)

    assert arch["microkernel"] is True
    assert arch["summary"]["syscall_count"] == 2
    assert arch["summary"]["top_syscalls"][0]["name"] == "do_example_b"
    assert syscall and syscall["file"] == "a.c"
    assert perf["total_lines"] == 1000
    assert boot["topology"] == "hub-spoke"
    assert phase["name"] == "Phase 1"
    assert "kernel_structure" in resources


def test_cli_resource_dump(sample_data_dir, benchmark):
    cmd = [
        sys.executable,
        "-m",
        "os_analysis_toolkit.cli",
        "--resource",
        "kernel_structure",
        "--data-dir",
        str(sample_data_dir),
    ]
    env = os.environ.copy()
    src_path = ROOT / "src"
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}"

    def run():
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout)

    payload = benchmark(run)
    assert payload["microkernel"] is True
    assert payload["components"] == ["kernel", "servers", "drivers"]


def test_cli_syscall_lookup(sample_data_dir, benchmark):
    cmd = [
        sys.executable,
        "-m",
        "os_analysis_toolkit.cli",
        "--syscall",
        "do_example_b",
        "--data-dir",
        str(sample_data_dir),
    ]
    env = os.environ.copy()
    src_path = ROOT / "src"
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}"

    def run():
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout)

    payload = benchmark(run)
    assert payload["file"] == "b.c"


def test_cli_kernel_summary(sample_data_dir, benchmark):
    cmd = [
        sys.executable,
        "-m",
        "os_analysis_toolkit.cli",
        "--kernel-summary",
        "--top-syscalls",
        "1",
        "--data-dir",
        str(sample_data_dir),
    ]
    env = os.environ.copy()
    src_path = ROOT / "src"
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}"
    def run():
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout)

    payload = benchmark(run)
    assert payload["summary"]["syscall_count"] == 2
    assert payload["summary"]["top_syscalls"][0]["name"] == "do_example_b"


def test_cli_boot_critical_path(sample_data_dir, benchmark):
    cmd = [
        sys.executable,
        "-m",
        "os_analysis_toolkit.cli",
        "--boot-critical-path",
        "--data-dir",
        str(sample_data_dir),
    ]
    env = os.environ.copy()
    src_path = ROOT / "src"
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}"
    def run():
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout)

    payload = benchmark(run)
    assert payload["critical_path"]["length"] == 5
