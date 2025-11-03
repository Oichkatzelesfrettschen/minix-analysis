#!/usr/bin/env bash
# Wrapper for running CPU interface analysis via the main CLI.
set -Eeuo pipefail

ROOT_DIR="$(git -C "$(dirname "${BASH_SOURCE[0]}")/../../.." rev-parse --show-toplevel)"
MINIX_ROOT="${MINIX_ROOT:-/home/eirikr/Playground/minix}"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/analysis-results/cpu-interface}"
WORKERS="${WORKERS:-}"

if [[ ! -d "${MINIX_ROOT}" ]]; then
    echo "MINIX source directory not found: ${MINIX_ROOT}" >&2
    echo "Set MINIX_ROOT to the correct path before running this script." >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

CLI_ARGS=(
    --source "${MINIX_ROOT}"
    --output "${OUTPUT_DIR}"
    --parallel
)

if [[ -n "${WORKERS}" ]]; then
    CLI_ARGS+=(--workers "${WORKERS}")
fi

echo "Running CPU interface analysis..."
echo "  MINIX_ROOT = ${MINIX_ROOT}"
echo "  OUTPUT_DIR = ${OUTPUT_DIR}"
if [[ -n "${WORKERS}" ]]; then
    echo "  WORKERS    = ${WORKERS}"
fi

python -m os_analysis_toolkit.cli "${CLI_ARGS[@]}"
