# MCP Configuration - Quick Start Guide

**Source**: START-HERE-MCP-FIXED.md
**Date Organized**: 2025-11-01
**Purpose**: Quick start guide for MCP (Model Context Protocol) configuration
**Complexity Level**: ⭐⭐ (Beginner-Intermediate)
**Estimated Time**: 5-10 minutes

---

MCP CONFIGURATION - FIXED AND READY TO TEST
Quick Start Guide for Next Session
================================================================================

TL;DR - WHAT HAPPENED
================================================================================

Previous MCP configuration had 2 CRITICAL issues discovered through testing:
  1. GitHub MCP package: DEPRECATED (no longer supported)
  2. SQLite MCP package: NEVER EXISTED in registry (404 error)

Both packages have been REPLACED with working alternatives:
  1. Filesystem: @modelcontextprotocol/server-filesystem (official, verified)
  2. SQLite: mcp-sqlite (community, v1.0.7, actively maintained, verified)

Status: READY FOR CLAUDE CODE TESTING ✓

================================================================================
WHAT TO DO NOW - NEXT SESSION
================================================================================

STEP 1: Start Claude Code
  $ cd /home/eirikr/Playground/minix-analysis
  $ claude

STEP 2: Verify MCP Servers Loaded
  In Claude Code, run:
  /mcp list

  Expected output:
    fs: @modelcontextprotocol/server-filesystem (running)
    sqlite: mcp-sqlite (running)

STEP 3: Test Filesystem Server
  Prompt: "List the Python tools in the minix-analysis project"
  Expected: File listing of tools/ directory contents

STEP 4: Test SQLite Server
  Prompt: "Query the boot_measurements table and calculate average boot times by architecture"
  Expected: Results showing i386 and arm boot times

STEP 5: Success
  If both servers respond without errors: SETUP IS SUCCESSFUL ✓

================================================================================
WHAT WAS FIXED
================================================================================

.mcp.json Configuration
  Original Problem: Referenced 2 broken packages
  Solution Applied: Updated to working packages + verified both work
  Status: ✓ FIXED AND TESTED

Package Installation
  Original Problem: Would fail at runtime trying to load bad packages
  Solution Applied: Replaced with available, working packages
  Status: ✓ WORKING

Database Setup
  Original Problem: Would reference non-existent database
  Solution Applied: Created minix-analysis.db with sample boot profiling data
  Status: ✓ READY FOR QUERIES

Directory Structure
  Original Problem: Missing measurement and log directories
  Solution Applied: Created all directories + database
  Status: ✓ COMPLETE

================================================================================
DOCUMENTATION FILES (READ IN THIS ORDER)
================================================================================

For Next Session:
  1. START-HERE-MCP-FIXED.md (this file)
     - Quick overview, what to do next

  2. MCP-SESSION-SUMMARY-2025-11-01.md
     - What happened in this session
     - What issues were fixed
     - Statistical summary

  3. MCP-VALIDATION-AND-READY-TO-TEST.md
     - Complete validation checklist
     - Test plan with expected results
     - Troubleshooting reference

For Reference/Troubleshooting:
  4. MCP-CRITICAL-DISCOVERY-REPORT.md
     - Detailed analysis of package registry issues
     - Why packages were deprecated/non-existent
     - WebSearch findings and evidence

  5. MCP-TROUBLESHOOTING-AND-FIXES.md
     - Original 14 configuration issues
     - Still valid for directory/infrastructure setup

For Quick Lookup:
  6. MCP-QUICK-REFERENCE.md
     - One-page cheat sheet
     - Common problems and solutions

================================================================================
KEY CONFIGURATION
================================================================================

File: .mcp.json

Two MCP Servers:
  1. "fs" - Filesystem Server
     Package: @modelcontextprotocol/server-filesystem (official)
     Allows: Read/write files in /home/eirikr/Playground/minix-analysis

  2. "sqlite" - SQLite Server
     Package: mcp-sqlite (community-maintained)
     Allows: Query /home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db

Database (minix-analysis.db):
  Table 1: boot_measurements
    - 3 sample records (i386 x2, arm x1)
    - Fields: timestamp, architecture, boot_time_ms, syscall_count, etc.

  Table 2: syscall_statistics
    - 6 sample records (3 per architecture)
    - Fields: syscall_name, call_count, total_time_us, avg_time_us, etc.

================================================================================
WHAT CHANGED FROM PREVIOUS VERSION
================================================================================

Before:
  "gh": "@modelcontextprotocol/server-github"  ← DEPRECATED (no longer supported)
  "db": "@modelcontextprotocol/server-sqlite"  ← NEVER EXISTED (404 in registry)

After:
  "fs": "@modelcontextprotocol/server-filesystem"  ← OFFICIAL, WORKING ✓
  "sqlite": "mcp-sqlite"                            ← COMMUNITY, WORKING ✓

================================================================================
IF SOMETHING DOESN'T WORK
================================================================================

Error: "Package not found"
Fix: Both packages are available via npx and have been tested
Try:
  npx -y @modelcontextprotocol/server-filesystem
  npx -y mcp-sqlite /tmp/test.db
Result: Both should spawn successfully

Error: "Permission denied" accessing database
Fix: Check database permissions
Try:
  ls -l measurements/minix-analysis.db
Expected: File readable by your user

Error: "ENOENT" (file not found)
Fix: Verify directory structure
Try:
  ls -la /home/eirikr/Playground/minix-analysis/measurements/
Expected: minix-analysis.db file exists

For more help:
  See: MCP-VALIDATION-AND-READY-TO-TEST.md (Troubleshooting section)

================================================================================
QUICK REFERENCE - COMMAND REFERENCE
================================================================================

Check MCP status:
  /mcp list

Disable/enable server:
  /mcp disable fs       # Disable filesystem
  /mcp enable fs        # Re-enable

Check context usage:
  /context info

Clear context (if needed):
  /clear

Validate configuration:
  python3 -m json.tool .mcp.json

Query database directly (if needed):
  sqlite3 measurements/minix-analysis.db
  > SELECT * FROM boot_measurements;
  > SELECT AVG(boot_time_ms) FROM boot_measurements GROUP BY architecture;
  > .exit

List files in project:
  ls -la /home/eirikr/Playground/minix-analysis

================================================================================
SUCCESS CHECKLIST FOR NEXT SESSION
================================================================================

After starting Claude Code and running tests, verify:

✓ /mcp list shows "fs" and "sqlite" servers running
✓ Filesystem server responds to file listing requests
✓ SQLite server responds to database queries
✓ boot_measurements returns 3 records (i386 x2, arm x1)
✓ syscall_statistics returns 6 records
✓ No "package not found" errors
✓ No "permission denied" errors
✓ Queries complete within timeout (30 seconds)

If all above are true: MCP SETUP SUCCESSFUL ✓

================================================================================
REMEMBER
================================================================================

1. Both MCP servers have been TESTED and VERIFIED to work
2. Database has been CREATED with sample data
3. Configuration has been VALIDATED for JSON syntax
4. Full documentation is available for reference
5. You have a clear test plan to follow

Everything is ready. Just start Claude Code and test.

================================================================================
NEXT STEPS AFTER SUCCESSFUL TESTING
================================================================================

1. Expand database with real MINIX boot profiling data
2. Research GitHub MCP alternatives (package deprecated)
3. Optionally install Docker for advanced services
4. Document findings and share with team

For details: See MCP-SESSION-SUMMARY-2025-11-01.md (Next Steps section)

================================================================================
END QUICK START GUIDE
================================================================================
