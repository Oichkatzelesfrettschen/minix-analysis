#!/bin/bash
# MINIX MCP Analysis - Maintenance & Cleanup Utility
# Handles log cleanup, archival, and disk space optimization
# Usage: ./maintenance-cleanup.sh [OPTIONS]

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/measurements"
ARCHIVE_DIR="$PROJECT_ROOT/archive"
BACKUP_DIR="$PROJECT_ROOT/backups"
OLD_DAYS=30
ARCHIVE_SIZE_LIMIT=$((1024 * 1024 * 100))  # 100MB

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Help message
show_help() {
    cat << 'EOF'
maintenance-cleanup.sh - MINIX cleanup and optimization

USAGE:
  ./maintenance-cleanup.sh [OPTIONS]

OPTIONS:
  --help              Show this help message
  --clean-logs        Delete logs older than 30 days
  --archive-old       Archive old measurements and logs
  --compress-reports  Compress text reports to .gz
  --vacuum-db         Optimize SQLite database (vacuum)
  --cleanup-docker    Remove unused Docker containers/images
  --full              Run all cleanup operations
  --dry-run           Show what would be done without making changes
  --aggressive        Cleanup more aggressively (7-day threshold)

EXAMPLES:
  # Dry run to preview cleanup
  $ ./maintenance-cleanup.sh --clean-logs --dry-run

  # Archive logs older than 30 days
  $ ./maintenance-cleanup.sh --archive-old

  # Full cleanup (all operations)
  $ ./maintenance-cleanup.sh --full

  # Aggressive cleanup (7-day threshold)
  $ ./maintenance-cleanup.sh --aggressive --full

OUTPUT:
  - Space freed: reported in MB/GB
  - Archived files: moved to archive/ with timestamp
  - Backup: created in backups/ before aggressive ops

RECOMMENDATION:
  Run monthly: ./maintenance-cleanup.sh --archive-old --compress-reports
  Run quarterly: ./maintenance-cleanup.sh --full --compress-reports
EOF
    exit 0
}

# Initialize
init() {
    mkdir -p "$ARCHIVE_DIR" "$BACKUP_DIR"
    echo -e "${BLUE}========== MINIX Maintenance & Cleanup ==========${NC}"
    echo "Project Root: $PROJECT_ROOT"
    echo "Log Directory: $LOG_DIR"
    echo "Archive Directory: $ARCHIVE_DIR"
    echo ""
}

# Clean old logs
clean_logs() {
    info "Cleaning logs older than $OLD_DAYS days..."
    
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.log" -type f -mtime +$OLD_DAYS | while read logfile; do
            if [ "$DRY_RUN" = "true" ]; then
                echo "  Would delete: $(basename "$logfile")"
            else
                rm -f "$logfile"
                pass "Deleted: $(basename "$logfile")"
            fi
        done
        pass "Log cleanup complete"
    else
        warn "Log directory not found: $LOG_DIR"
    fi
    echo ""
}

# Archive old measurements
archive_old() {
    info "Archiving measurements older than $OLD_DAYS days..."
    
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    ARCHIVE_TAR="$ARCHIVE_DIR/measurements-$TIMESTAMP.tar.gz"
    
    if [ -d "$LOG_DIR" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            info "Would create archive: $ARCHIVE_TAR"
            find "$LOG_DIR" -type f -mtime +$OLD_DAYS | head -5 | while read f; do
                echo "  Would archive: $(basename "$f")"
            done
        else
            # Create tarball of old files
            find "$LOG_DIR" -type f -mtime +$OLD_DAYS \
                -exec tar --absolute-names -czf "$ARCHIVE_TAR" {} + 2>/dev/null || true
            
            if [ -f "$ARCHIVE_TAR" ]; then
                SIZE=$(du -h "$ARCHIVE_TAR" | cut -f1)
                pass "Archive created: $ARCHIVE_TAR ($SIZE)"
            else
                warn "No old files to archive"
            fi
        fi
    fi
    echo ""
}

# Compress reports
compress_reports() {
    info "Compressing text reports to .gz..."
    
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.txt" -type f | while read txtfile; do
            if [ "$DRY_RUN" = "true" ]; then
                SIZE=$(du -h "$txtfile" | cut -f1)
                echo "  Would compress: $(basename "$txtfile") ($SIZE)"
            else
                gzip -9 "$txtfile"
                pass "Compressed: $(basename "$txtfile")"
            fi
        done
        pass "Report compression complete"
    fi
    echo ""
}

# Optimize SQLite database
vacuum_db() {
    info "Optimizing SQLite database..."
    
    DB="$LOG_DIR/boot-profiling.db"
    if [ -f "$DB" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo "  Would optimize: $(basename "$DB")"
            echo "  Current size: $(du -h "$DB" | cut -f1)"
        else
            sqlite3 "$DB" "VACUUM;" 2>/dev/null || true
            pass "Database optimized: $(basename "$DB")"
            echo "  New size: $(du -h "$DB" | cut -f1)"
        fi
    else
        warn "Database not found: $DB"
    fi
    echo ""
}

# Cleanup Docker
cleanup_docker() {
    info "Cleaning up unused Docker resources..."
    
    if command -v docker &> /dev/null; then
        if [ "$DRY_RUN" = "true" ]; then
            IMAGES=$(docker images --filter dangling=true -q | wc -l)
            CONTAINERS=$(docker ps -a --filter status=exited -q | wc -l)
            echo "  Would remove $IMAGES dangling images"
            echo "  Would remove $CONTAINERS exited containers"
        else
            # Remove dangling images
            docker images --filter dangling=true -q | xargs -r docker rmi 2>/dev/null || true
            pass "Dangling images removed"
            
            # Remove exited containers
            docker ps -a --filter status=exited -q | xargs -r docker rm 2>/dev/null || true
            pass "Exited containers removed"
            
            # Prune unused volumes
            docker volume prune -f 2>/dev/null || true
            pass "Unused volumes pruned"
        fi
    else
        warn "Docker not installed"
    fi
    echo ""
}

# Create backup before aggressive operations
backup_before_cleanup() {
    info "Creating backup before aggressive cleanup..."
    
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BACKUP_TAR="$BACKUP_DIR/pre-cleanup-backup-$TIMESTAMP.tar.gz"
    
    tar -czf "$BACKUP_TAR" -C "$PROJECT_ROOT" \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        measurements/ diagrams/ 2>/dev/null || true
    
    SIZE=$(du -h "$BACKUP_TAR" | cut -f1)
    pass "Backup created: $BACKUP_TAR ($SIZE)"
    echo ""
}

# Report disk usage
report_usage() {
    echo -e "${BLUE}========== Disk Usage Report ==========${NC}"
    
    if [ -d "$LOG_DIR" ]; then
        echo "Measurements directory: $(du -sh "$LOG_DIR" | cut -f1)"
    fi
    
    if [ -d "$ARCHIVE_DIR" ]; then
        echo "Archive directory: $(du -sh "$ARCHIVE_DIR" | cut -f1)"
    fi
    
    if [ -d "$BACKUP_DIR" ]; then
        echo "Backup directory: $(du -sh "$BACKUP_DIR" | cut -f1)"
    fi
    
    echo "Project total: $(du -sh "$PROJECT_ROOT" | cut -f1)"
    echo ""
}

# Main execution
main() {
    init
    
    # Set aggressive threshold if requested
    if [ "$AGGRESSIVE" = "true" ]; then
        OLD_DAYS=7
        info "Using aggressive cleanup (7-day threshold)"
    fi
    
    # Create backup if doing aggressive cleanup
    if [ "$AGGRESSIVE" = "true" ] && [ "$DRY_RUN" != "true" ]; then
        backup_before_cleanup
    fi
    
    # Run requested operations
    if [ "$CLEAN_LOGS" = "true" ]; then clean_logs; fi
    if [ "$ARCHIVE_OLD" = "true" ]; then archive_old; fi
    if [ "$COMPRESS_REPORTS" = "true" ]; then compress_reports; fi
    if [ "$VACUUM_DB" = "true" ]; then vacuum_db; fi
    if [ "$CLEANUP_DOCKER" = "true" ]; then cleanup_docker; fi
    
    # Report final usage
    report_usage
    
    if [ "$DRY_RUN" = "true" ]; then
        warn "DRY RUN MODE - No changes made"
        echo ""
        echo "To apply changes, run without --dry-run flag"
    else
        pass "Cleanup operations complete"
    fi
}

# Parse arguments
CLEAN_LOGS=false
ARCHIVE_OLD=false
COMPRESS_REPORTS=false
VACUUM_DB=false
CLEANUP_DOCKER=false
DRY_RUN=false
AGGRESSIVE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help) show_help ;;
        --clean-logs) CLEAN_LOGS=true ;;
        --archive-old) ARCHIVE_OLD=true ;;
        --compress-reports) COMPRESS_REPORTS=true ;;
        --vacuum-db) VACUUM_DB=true ;;
        --cleanup-docker) CLEANUP_DOCKER=true ;;
        --full)
            CLEAN_LOGS=true
            ARCHIVE_OLD=true
            COMPRESS_REPORTS=true
            VACUUM_DB=true
            CLEANUP_DOCKER=true
            ;;
        --dry-run) DRY_RUN=true ;;
        --aggressive) AGGRESSIVE=true ;;
        *) fail "Unknown option: $1" ;;
    esac
    shift
done

# Validate at least one operation selected
if [ "$CLEAN_LOGS" = "false" ] && [ "$ARCHIVE_OLD" = "false" ] && \
   [ "$COMPRESS_REPORTS" = "false" ] && [ "$VACUUM_DB" = "false" ] && \
   [ "$CLEANUP_DOCKER" = "false" ]; then
    warn "No operations specified. Use --help for options."
    show_help
fi

main
