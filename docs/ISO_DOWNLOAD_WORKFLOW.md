# MINIX ISO Download Workflow

**Date**: November 2025
**Status**: Production-ready
**Purpose**: Download MINIX 3 ISOs from official sources instead of storing large binary files in git

---

## Overview

Instead of storing large MINIX ISO files (400-600 MB each) in the git repository, this workflow downloads them on-demand from official sources. This keeps the repository lean while ensuring reproducible builds.

### Rationale

- **Git limitation**: GitHub has a 100 MB file size limit; large ISOs cannot be pushed
- **Reproducibility**: Always download from official source, never rely on stale local copies
- **Flexibility**: Switch between MINIX versions without repository bloat
- **Build integration**: Automates ISO preparation for Docker/QEMU workflows

---

## Quick Start

### Download MINIX 3.4.0 (Latest Stable)

```bash
./tools/download_minix_images.sh
# Downloads to: ./3.4.0/minix-3.4.0.iso
```

### Download Specific Version

```bash
# MINIX 3.4.0rc6 (Release Candidate)
./tools/download_minix_images.sh 3.4.0rc6 minix-images/

# MINIX 3.3.0 (Previous Stable)
./tools/download_minix_images.sh 3.3.0 minix-images/

# MINIX 3.2.1 (Older Release)
./tools/download_minix_images.sh 3.2.1 minix-images/
```

---

## Supported Versions

| Version | Status | Size | Source |
|---------|--------|------|--------|
| 3.4.0 | Stable | ~603 MB | GitHub Releases |
| 3.4.0rc6 | Release Candidate | ~410 MB | GitHub Releases |
| 3.3.0 | Stable (Previous) | ~500 MB | GitHub Releases |
| 3.2.1 | Legacy | ~300 MB | GitHub Releases |

---

## Features

### Automatic Download and Decompression

```bash
# Automatically detects .iso.bz2 files and decompresses
./tools/download_minix_images.sh 3.4.0rc6

# Extracts: minix_R3.4.0rc6-d5e4fc0.iso.bz2 -> minix_R3.4.0rc6-d5e4fc0.iso
```

### Checksum Verification

```bash
# Verifies SHA256 checksums when available
./tools/download_minix_images.sh 3.4.0

# Output: [SUCCESS] Checksum verified
```

### Retry Logic

```bash
# Automatically retries up to 3 times on failure
# Exponential backoff: 5s, 10s, 15s between retries

./tools/download_minix_images.sh 3.4.0 \
    # Retry 1: fails, waits 5s
    # Retry 2: fails, waits 10s
    # Retry 3: succeeds, downloads complete
```

### Multiple Sources

```bash
# Primary: GitHub Releases (official)
# Fallback: FTP Mirror (ftp.minix3.org)

# Automatically tries fallback if primary fails
./tools/download_minix_images.sh 3.4.0
```

---

## Integration with Docker

### Option 1: Pre-downloaded ISO

Download before building:

```bash
./tools/download_minix_images.sh 3.4.0 minix-images/

# Build Docker image with ISO
docker build -f docker/qemu/Dockerfile \
    -v minix-images/:/minix-images \
    .
```

### Option 2: Volume Mount at Runtime

```bash
# Download to persistent location
./tools/download_minix_images.sh 3.4.0 /opt/minix-images/

# Use in docker-compose.yml
docker-compose -f docker/qemu/docker-compose.yml up \
    -v /opt/minix-images:/minix-images
```

### Option 3: Automated Download in Docker

Modify `docker/qemu/Dockerfile`:

```dockerfile
# Download MINIX at container build time
RUN apt-get install -y curl bzip2 && \
    curl -L https://github.com/Minix3/minix/releases/download/v3.4.0/minix-3.4.0.iso \
    -o /qemu-images/minix-3.4.0.iso && \
    chmod 644 /qemu-images/minix-3.4.0.iso
```

---

## Command Reference

### Basic Usage

```bash
./tools/download_minix_images.sh [VERSION] [DIRECTORY]
```

### Arguments

- `VERSION`: MINIX version (3.2.1, 3.3.0, 3.4.0, 3.4.0rc6)
  - Default: `3.4.0`
  - Examples: `3.4.0`, `3.4.0rc6`

- `DIRECTORY`: Download destination directory
  - Default: Current directory (`.`)
  - Examples: `./minix-images`, `/opt/minix`, `../iso-cache`

### Return Values

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (download failed, invalid version, etc.) |

### Output

```
[INFO] === MINIX ISO Download Workflow ===
[INFO] Version: 3.4.0
[INFO] Destination: ./3.4.0
[SUCCESS] All prerequisites available
[INFO] Downloading: https://github.com/Minix3/minix/releases/download/v3.4.0/minix-3.4.0.iso
[INFO] Destination: ./3.4.0/minix-3.4.0.iso
######################################################################## 100.0%
[SUCCESS] Downloaded: minix-3.4.0.iso
[SUCCESS] Checksum verified
[SUCCESS] Download workflow complete!
```

---

## Prerequisites

The script requires these command-line tools:

```bash
curl     # HTTP download tool
wget     # Alternative download tool (fallback)
tar      # Archive extraction
bzip2    # BZ2 decompression
sha256sum # Checksum verification
```

### Installation

**On Ubuntu/Debian:**
```bash
sudo apt-get install curl wget tar bzip2 coreutils
```

**On Arch/CachyOS:**
```bash
sudo pacman -S curl wget tar bzip2 coreutils
```

**On macOS:**
```bash
brew install curl wget coreutils bzip2
```

### Verification

```bash
./tools/download_minix_images.sh --help
# Should display help without errors
```

---

## Troubleshooting

### Issue: "Checksum mismatch"

**Cause**: Corrupted download or ISO version mismatch
**Solution**: Delete the file and retry
```bash
rm ./3.4.0/minix-3.4.0.iso
./tools/download_minix_images.sh 3.4.0
```

### Issue: "Failed to download"

**Cause**: Network issue, GitHub down, or firewall blocking
**Solution**: Check network and try again
```bash
# Test connectivity
curl -I https://github.com/Minix3/minix/releases

# Retry with verbose output
bash -x ./tools/download_minix_images.sh 3.4.0
```

### Issue: "Required command not found: curl"

**Cause**: curl not installed
**Solution**: Install curl
```bash
sudo pacman -S curl      # Arch/CachyOS
sudo apt install curl    # Ubuntu/Debian
```

### Issue: "Failed to decompress"

**Cause**: Incomplete or corrupted .bz2 file
**Solution**: Delete and re-download
```bash
rm ./3.4.0rc6/minix_R3.4.0rc6-d5e4fc0.iso.bz2
./tools/download_minix_images.sh 3.4.0rc6
```

---

## Advanced Usage

### Parallel Downloads

Download multiple versions simultaneously:

```bash
# Terminal 1
./tools/download_minix_images.sh 3.4.0 ~/minix-images &

# Terminal 2
./tools/download_minix_images.sh 3.3.0 ~/minix-images &

# Wait for all to complete
wait
```

### Integration with CI/CD

**GitHub Actions example:**

```yaml
jobs:
  download-minix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download MINIX 3.4.0
        run: ./tools/download_minix_images.sh 3.4.0

      - name: Cache ISO
        uses: actions/cache@v3
        with:
          path: ./3.4.0/minix-3.4.0.iso
          key: minix-3.4.0-iso
```

### Cron-based Updates

**Update ISOs daily:**

```bash
# In crontab
0 2 * * * cd /opt/minix-analysis && ./tools/download_minix_images.sh 3.4.0 /opt/minix-images/
```

---

## File Structure

After downloading, expected structure:

```
minix-analysis/
├── tools/
│   └── download_minix_images.sh      # This script
├── 3.4.0/                             # Downloaded ISOs
│   ├── minix-3.4.0.iso               # Main ISO (603 MB)
│   └── ...
└── minix-images/                      # Alternative download location
    ├── minix-3.3.0.iso
    ├── minix-3.4.0rc6.iso
    └── ...
```

---

## Performance Notes

### Typical Download Times

| Version | Size | Network | Duration |
|---------|------|---------|----------|
| 3.4.0 | 603 MB | 50 Mbps | 2 minutes |
| 3.4.0rc6 | 410 MB (bz2) | 50 Mbps | 2 minutes |
| 3.3.0 | 500 MB | 50 Mbps | 2 minutes |

### Storage Requirements

| Version | Size | Extracted (if bz2) |
|---------|------|-------------------|
| 3.4.0 | 603 MB | N/A (already ISO) |
| 3.4.0rc6 | 410 MB (bz2) | 603 MB |
| 3.3.0 | 500 MB | N/A (already ISO) |

Total storage for all versions: ~2.5 GB

---

## Security Considerations

### Checksum Verification

All downloads are verified against SHA256 checksums when available:

```bash
# The script automatically performs:
sha256sum -c <<< "HASH  minix-3.4.0.iso"
```

### Download Source

- **Primary**: GitHub Releases (HTTPS, official source)
- **Fallback**: FTP Mirror (consider firewall rules)

### Network Security

```bash
# HTTPS enforced for GitHub downloads
curl -L https://github.com/Minix3/minix/releases/download/...

# Warning: FTP fallback is unencrypted (use only if necessary)
```

---

## Further Reading

- MINIX 3 Official: https://minix3.org/
- Downloads: https://minix3.org/download/
- GitHub Releases: https://github.com/Minix3/minix/releases/
- FTP Mirror: http://ftp.minix3.org/

---

## Contributing

To add support for new MINIX versions:

1. Update `MINIX_RELEASES` array in script
2. Add checksums to `MINIX_CHECKSUMS`
3. Create version-specific download function
4. Test with: `./tools/download_minix_images.sh new-version`
5. Submit PR with updated documentation

---

**Status**: Ready for production use
**Last Updated**: November 2025
**Tested On**: CachyOS, Ubuntu 22.04, Debian 11
