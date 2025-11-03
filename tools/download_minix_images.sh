#!/bin/bash
################################################################################
# MINIX 3 ISO and Image Download Workflow
# Purpose: Download official MINIX 3 releases from source instead of storing
#          large binary files in git repository
# Supported versions: MINIX 3.3.0, MINIX 3.4.0, MINIX 3.4.0rc6
# Usage: ./tools/download_minix_images.sh [version] [destination]
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOWNLOAD_DIR="${2:-.}/${1:-3.4.0}"
MINIX_VERSION="${1:-3.4.0}"

# MINIX Release Information
# Official sources: https://minix3.org/download/
declare -A MINIX_RELEASES=(
    [3.2.1]="minix3.2.1"
    [3.3.0]="minix-3.3.0"
    [3.4.0]="minix-3.4.0"
    [3.4.0rc6]="minix_R3.4.0rc6-d5e4fc0"
)

declare -A MINIX_CHECKSUMS=(
    # Format: [version]="sha256sum"
    [3.2.1]="SKIP"  # Not available
    [3.3.0]="SKIP"  # Not available
    [3.4.0]="SKIP"  # Verify from official source
    [3.4.0rc6]="SKIP"  # Release candidate
)

# Official download URLs
MINIX_DOWNLOAD_BASE="https://minix3.org/download/"
MINIX_MIRROR_1="https://github.com/Minix3/minix/releases/download/"
MINIX_MIRROR_2="http://ftp.minix3.org/"

################################################################################
# Utility Functions
################################################################################

log_info() {
    echo "[INFO] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
    return 1
}

log_success() {
    echo "[SUCCESS] $*" >&2
}

verify_prerequisites() {
    local missing=0

    # Check required commands
    for cmd in curl wget tar bzip2 sha256sum; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Required command not found: $cmd"
            missing=1
        fi
    done

    if [ $missing -eq 1 ]; then
        log_error "Please install missing dependencies"
        return 1
    fi

    log_success "All prerequisites available"
}

################################################################################
# Download Functions
################################################################################

download_file() {
    local url="$1"
    local dest="$2"
    local max_retries=3
    local retry=0

    log_info "Downloading: $url"
    log_info "Destination: $dest"

    while [ $retry -lt $max_retries ]; do
        if curl -f -L -o "$dest" --progress-bar "$url"; then
            log_success "Downloaded: $(basename "$dest")"
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_info "Download failed, retry $retry/$max_retries..."
            sleep $((retry * 5))
        fi
    done

    log_error "Failed to download after $max_retries attempts"
    return 1
}

verify_checksum() {
    local file="$1"
    local expected="$2"

    if [ "$expected" = "SKIP" ]; then
        log_info "Checksum verification skipped for $file"
        return 0
    fi

    log_info "Verifying checksum: $file"

    local actual
    actual=$(sha256sum "$file" | awk '{print $1}')

    if [ "$actual" != "$expected" ]; then
        log_error "Checksum mismatch!"
        log_error "  Expected: $expected"
        log_error "  Actual:   $actual"
        return 1
    fi

    log_success "Checksum verified"
    return 0
}

################################################################################
# MINIX Version Specific Downloaders
################################################################################

download_minix_3_4_0() {
    local version="3.4.0"
    local base_name="${MINIX_RELEASES[$version]}"
    local iso_name="${base_name}.iso"
    local iso_path="$DOWNLOAD_DIR/$iso_name"

    log_info "Downloading MINIX $version..."

    # Try official source first
    local url="${MINIX_MIRROR_1}v${version}/${iso_name}"

    mkdir -p "$DOWNLOAD_DIR"

    if ! download_file "$url" "$iso_path"; then
        # Fallback to mirror
        url="${MINIX_MIRROR_2}releases/${version}/${iso_name}"
        download_file "$url" "$iso_path" || return 1
    fi

    verify_checksum "$iso_path" "${MINIX_CHECKSUMS[$version]}"

    log_success "MINIX $version downloaded to: $iso_path"
}

download_minix_3_4_0rc6() {
    local version="3.4.0rc6"
    local base_name="${MINIX_RELEASES[$version]}"
    local iso_name="${base_name}.iso"
    local iso_bz2_name="${iso_name}.bz2"
    local iso_path="$DOWNLOAD_DIR/$iso_name"
    local bz2_path="$DOWNLOAD_DIR/$iso_bz2_name"

    log_info "Downloading MINIX $version (release candidate)..."

    # Release candidate source
    local url="${MINIX_MIRROR_1}v${version}/${iso_bz2_name}"

    mkdir -p "$DOWNLOAD_DIR"

    if download_file "$url" "$bz2_path"; then
        log_info "Decompressing: $bz2_path"
        bunzip2 -f "$bz2_path" || log_error "Failed to decompress"
    else
        log_error "Failed to download MINIX $version"
        return 1
    fi

    verify_checksum "$iso_path" "${MINIX_CHECKSUMS[$version]}"

    log_success "MINIX $version downloaded and decompressed to: $iso_path"
}

download_minix_3_3_0() {
    local version="3.3.0"
    local base_name="${MINIX_RELEASES[$version]}"
    local iso_name="${base_name}.iso"
    local iso_path="$DOWNLOAD_DIR/$iso_name"

    log_info "Downloading MINIX $version..."

    # GitHub releases or official source
    local url="${MINIX_MIRROR_1}v${version}/${iso_name}"

    mkdir -p "$DOWNLOAD_DIR"

    download_file "$url" "$iso_path" || return 1
    verify_checksum "$iso_path" "${MINIX_CHECKSUMS[$version]}"

    log_success "MINIX $version downloaded to: $iso_path"
}

################################################################################
# Extract and Prepare Images
################################################################################

create_qemu_images() {
    local iso_path="$1"
    local dest_dir="$(dirname "$iso_path")"

    if [ ! -f "$iso_path" ]; then
        log_error "ISO not found: $iso_path"
        return 1
    fi

    log_info "Creating QEMU images from: $iso_path"

    # Extract boot image for direct QEMU boot
    # (Requires isodump or similar tool - optional)

    log_success "Images ready for QEMU at: $dest_dir"
}

################################################################################
# Integration Functions
################################################################################

prepare_for_docker() {
    local iso_path="$1"
    local docker_image_dir="$PROJECT_ROOT/docker/qemu"

    log_info "Preparing ISO for Docker build..."

    if [ -f "$iso_path" ]; then
        cp "$iso_path" "$docker_image_dir/" || log_error "Failed to copy ISO"
        log_success "ISO copied to Docker directory"
    fi
}

################################################################################
# Main Workflow
################################################################################

main() {
    log_info "=== MINIX ISO Download Workflow ==="
    log_info "Version: $MINIX_VERSION"
    log_info "Destination: $DOWNLOAD_DIR"

    verify_prerequisites || return 1

    case "$MINIX_VERSION" in
        3.4.0)
            download_minix_3_4_0 || return 1
            ;;
        3.4.0rc6)
            download_minix_3_4_0rc6 || return 1
            ;;
        3.3.0)
            download_minix_3_3_0 || return 1
            ;;
        *)
            log_error "Unsupported MINIX version: $MINIX_VERSION"
            log_info "Supported versions: 3.2.1, 3.3.0, 3.4.0, 3.4.0rc6"
            return 1
            ;;
    esac

    # Optional: Extract and create QEMU images
    # create_qemu_images "$DOWNLOAD_DIR/minix-*.iso"

    # Optional: Prepare for Docker build
    # prepare_for_docker "$DOWNLOAD_DIR/minix-*.iso"

    log_success "Download workflow complete!"
    log_info "Next steps:"
    log_info "  1. Use ISO in QEMU: qemu-system-i386 -cdrom <iso_path>"
    log_info "  2. Or mount for Docker: docker run -v <iso_path>:/minix.iso ..."
    log_info "  3. Or integrate into docker-compose.yml"
}

################################################################################
# Help and Usage
################################################################################

show_help() {
    cat <<'EOF'
MINIX 3 ISO Download Workflow

USAGE:
    ./tools/download_minix_images.sh [VERSION] [DIRECTORY]

ARGUMENTS:
    VERSION:    MINIX version (3.2.1, 3.3.0, 3.4.0, 3.4.0rc6)
                Default: 3.4.0

    DIRECTORY:  Download destination directory
                Default: current directory

EXAMPLES:
    # Download MINIX 3.4.0 to current directory
    ./tools/download_minix_images.sh

    # Download MINIX 3.4.0rc6 to minix-images/
    ./tools/download_minix_images.sh 3.4.0rc6 minix-images

    # Download MINIX 3.3.0
    ./tools/download_minix_images.sh 3.3.0

SUPPORTED SOURCES:
    - Official GitHub Releases (https://github.com/Minix3/minix/releases)
    - Official Mirror (http://ftp.minix3.org/)

INTEGRATION WITH DOCKER:
    Update docker-compose.yml volumes section:
        volumes:
            minix_images:
                driver: local
            minix_config:
                driver: local

    Then reference downloaded ISO:
        qemu-minix:
            volumes:
                - ./minix-source/minix-3.4.0.iso:/minix.iso

NOTES:
    - Large ISO files are NOT stored in git (see .gitignore)
    - Download happens at build/runtime, not during clone
    - Checksums verified when available
    - Automatic retry on download failure

For more information, see:
    - https://minix3.org/download/
    - https://github.com/Minix3/minix/releases
EOF
}

################################################################################
# Entry Point
################################################################################

# Handle help flag
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    show_help
    exit 0
fi

# Run main workflow
main "$@"
