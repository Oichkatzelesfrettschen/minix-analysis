# CPU Interface Pipeline Helpers

These utilities streamline CPU-interface specific analysis workflows without duplicating the global CLI.

## Scripts

- `run_cpu_analysis.sh` — Wrapper that invokes the project CLI against the configured MINIX checkout and stores outputs in a predictable location.
- `render_syscall_summary.py` — Reads the generated `kernel_structure.json` dataset and prints a concise summary (total syscalls, top-N by line count) for quick inspection or dashboards.

## Usage

```bash
# Run full CPU analysis (parallel by default)
modules/cpu-interface/pipeline/run_cpu_analysis.sh

# Summarise syscall catalog (defaults to diagrams/data/kernel_structure.json)
python modules/cpu-interface/pipeline/render_syscall_summary.py --limit 5
```

Both scripts respect the following environment variables:

- `MINIX_ROOT` — Path to the MINIX source tree (`/home/eirikr/Playground/minix` by default).
- `OUTPUT_DIR` — Destination for CLI outputs (defaults to `analysis-results/cpu-interface`).
- `WORKERS` — Overrides the worker count passed to the parallel pipeline wrapper.
