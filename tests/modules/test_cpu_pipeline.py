import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path("modules/cpu-interface/pipeline")
RUN_SCRIPT = SCRIPT_DIR / "run_cpu_analysis.sh"
SUMMARY_SCRIPT = SCRIPT_DIR / "render_syscall_summary.py"


@pytest.mark.unit
def test_run_cpu_analysis_script_exists_and_executable(benchmark):
    def check_script():
        if not RUN_SCRIPT.exists():
            raise AssertionError("run_cpu_analysis.sh is missing")
        mode = RUN_SCRIPT.stat().st_mode
        if not (mode & stat.S_IXUSR):
            raise AssertionError("run_cpu_analysis.sh must be executable")

    benchmark(check_script)


@pytest.mark.unit
def test_render_syscall_summary_produces_expected_output(tmp_path, benchmark):
    sample_catalog = {
        "system_calls": [
            {"name": "do_example_a", "file": "a.c", "line_count": 10},
            {"name": "do_example_b", "file": "b.c", "line_count": 25},
            {"name": "do_example_c", "file": "c.c", "line_count": 5},
        ]
    }
    input_path = tmp_path / "kernel_structure.json"
    input_path.write_text(json.dumps(sample_catalog), encoding="utf-8")

    def render():
        proc = subprocess.run(
            [
                sys.executable,
                str(SUMMARY_SCRIPT),
                "--kernel-structure",
                str(input_path),
                "--limit",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )
        return json.loads(proc.stdout)

    output = benchmark(render)
    assert output["syscall_count"] == 3
    assert len(output["top_syscalls"]) == 2
    # Ensure ordering by line_count descending
    assert output["top_syscalls"][0]["name"] == "do_example_b"
