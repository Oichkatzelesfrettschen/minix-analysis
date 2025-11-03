#!/usr/bin/env python3
"""
MINIX Boot Error Triage Tool
Analyzes MINIX boot logs to detect common errors and suggest solutions

Usage:
  python3 triage-minix-errors.py boot.log
  python3 triage-minix-errors.py --generate-registry MINIX-Error-Registry.md
  python3 triage-minix-errors.py --watch measurements/i386/boot.log
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import subprocess

class ErrorPattern:
    """Single error pattern with detection and solution"""
    
    def __init__(self, error_id: str, name: str, patterns: List[str], 
                 root_causes: List[str], solutions: List[str], 
                 severity: str, confidence: float):
        self.error_id = error_id
        self.name = name
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.root_causes = root_causes
        self.solutions = solutions
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.confidence = confidence  # 0.0-1.0

    def match(self, text: str) -> bool:
        """Check if error pattern matches text"""
        return any(pattern.search(text) for pattern in self.patterns)


class MinixErrorRegistry:
    """Registry of known MINIX boot errors"""
    
    ERRORS = [
        # Error 1: Blank Screen
        ErrorPattern(
            "E001", "Blank Screen / No Output",
            [r"no output", r"blank screen", r"nothing appears"],
            ["Display server not initialized", "Graphics driver missing", "Serial console not configured"],
            ["Add -sdl parameter", "Use -vnc :0 for visual monitoring", 
             "Use -serial file:boot.log -nographic for automated testing"],
            "HIGH", 0.7
        ),
        
        # Error 2: SeaBIOS Hang
        ErrorPattern(
            "E002", "SeaBIOS Hang",
            [r"SeaBIOS.*hang", r"stuck.*SeaBIOS", r"^SeaBIOS vX\.X\.X", r"bios.*hang"],
            ["CPU incompatibility", "SeaBIOS initialization failure", "QEMU version issue"],
            ["Use -cpu kvm32 instead of -cpu host", "Try different CPU models (486, pentium, kvm32)",
             "Upgrade QEMU: pacman -Syu qemu"],
            "HIGH", 0.8
        ),
        
        # Error 3: CD9660 Module Failure
        ErrorPattern(
            "E003", "CD9660 Module Load Failure",
            [r"failed to load cd9660", r"cd9660.*failed", r"mount.*cd9660.*failed"],
            ["Interactive ISO with no serial console", "MINIX version too old", 
             "Kernel module not compiled"],
            ["Use MINIX RC6 or later from https://www.minix3.org",
             "Build MINIX from source with ./build.sh",
             "Use pre-built disk image instead of ISO"],
            "CRITICAL", 0.95
        ),
        
        # Error 4: Active Partition Error
        ErrorPattern(
            "E004", "Active Partition Not Found",
            [r"active partition", r"partition.*not found", r"active.*error"],
            ["MINIX doesn't support USB installation from non-Unix systems",
             "Incompatible partition table format"],
            ["Use QEMU on Linux to create disk image first",
             "Boot live Linux, install QEMU, then use MINIX ISO to install"],
            "HIGH", 0.75
        ),
        
        # Error 5: AHCI Not Found
        ErrorPattern(
            "E005", "AHCI Boot Error",
            [r"trying.*c1d4", r"no cd found", r"ahci.*not found", r"c1d4.*not found"],
            ["QEMU Q35 doesn't implement AHCI spec properly",
             "MINIX AHCI driver expects missing interrupt"],
            ["Select IDE option (1) at MINIX boot menu instead of AHCI",
             "Disable AHCI in /etc/boot.cfg",
             "Use i440FX chipset instead of Q35"],
            "MEDIUM", 0.85
        ),
        
        # Error 6: IRQ Check Failed
        ErrorPattern(
            "E006", "IRQ Check Failed / TTY Errors",
            [r"do_irqctl.*irq check", r"couldn't obtain hook.*irq", 
             r"irq.*check.*failed", r"hook.*irq.*failed"],
            ["Ethernet driver (NE2K) configured with wrong IRQ",
             "IRQ conflict with other device", "TTY device initialization failure"],
            ["Configure NE2K with IRQ 3 (not default 11) and I/O 0x300",
             "In rc.local: export DPETH0=300:3",
             "Or at QEMU: -net nic,model=ne2k_isa,irq=3,iobase=0x300"],
            "HIGH", 0.8
        ),
        
        # Error 7: Memory Allocation
        ErrorPattern(
            "E007", "Memory Allocation Failure",
            [r"malloc.*failed", r"memory.*allocation.*failed", 
             r"out of memory", r"memory.*exhausted"],
            ["Insufficient VM memory for application",
             "X11 server trying to allocate too much",
             "MINIX lacks virtual memory (all must fit in physical RAM)"],
            ["Increase QEMU memory: -m 1G or higher",
             "Use chmem to reduce binary memory requirements: chmem =67108864 /usr/X11R6/bin/Xorg",
             "Reduce X11 workload (use minimal window manager)"],
            "MEDIUM", 0.75
        ),
        
        # Error 8: Network Not Working
        ErrorPattern(
            "E008", "Network Not Working",
            [r"routing error", r"network.*fail", r"ping.*fail",
             r"no route", r"connection refused"],
            ["NE2K driver not initialized", "DHCP not running", "IP not configured"],
            ["Check ifconfig output: ifconfig ne2k0",
             "Configure DPETH0 in rc.local: export DPETH0=300:3",
             "Start DHCP: service dhcp start",
             "Test: ping 8.8.8.8"],
            "MEDIUM", 0.65
        ),
        
        # Error 9: Boot from Disk Fails
        ErrorPattern(
            "E009", "Boot from Disk Fails",
            [r"boot.*fail", r"boot sector.*not found", r"no.*bootable"],
            ["Disk partition table corrupted", "Boot MBR missing or invalid",
             "Wrong boot order in QEMU"],
            ["Use correct QEMU parameter: -boot c",
             "Rebuild disk image from scratch",
             "Verify partition table: qemu-img info minix.img"],
            "HIGH", 0.7
        ),
        
        # Error 10: Timeout
        ErrorPattern(
            "E010", "Installation/Boot Timeout",
            [r"timeout", r"timed out", r"exceeded timeout"],
            ["File copy phase taking longer than expected",
             "Installer waiting for input (prompt not visible)",
             "Slow disk I/O"],
            ["Increase timeout: timeout 600 qemu-system-i386",
             "Monitor with VNC: -vnc :0",
             "Check serial log for hidden prompts: tail -f boot.log"],
            "LOW", 0.6
        ),
        
        # Error 11: Kernel Panic
        ErrorPattern(
            "E011", "Kernel Panic",
            [r"panic", r"fatal.*error", r"kernel.*halt"],
            ["Module load failure", "Memory allocation in kernel",
             "CPU feature not supported", "Interrupt controller not responding"],
            ["Check boot.log for which module failed to load",
             "Try simpler CPU: -cpu 486",
             "Increase memory: -m 1G",
             "Check MINIX version compatibility"],
            "CRITICAL", 0.9
        ),
        
        # Error 12: Disk I/O Error
        ErrorPattern(
            "E012", "Disk I/O Error",
            [r"error.*reading.*disk", r"i/o error", r"read.*failed"],
            ["QEMU disk emulation issue with qcow2", "Disk image corruption",
             "Raw format incompatible with operations"],
            ["Use raw format instead of qcow2: qemu-img create -f raw",
             "Check disk health: qemu-img check minix.img",
             "Rebuild disk from scratch if corrupted"],
            "HIGH", 0.7
        ),
        
        # Error 13: TTY Device Conflicts
        ErrorPattern(
            "E013", "TTY Device Not Responding",
            [r"tty.*not responding", r"device initialization.*failed",
             r"tty.*disabled"],
            ["Serial console conflict with TTY0", "TTY device not initialized"],
            ["Use serial-only console: console=tty00 consdev=com0",
             "Use VNC instead of serial to avoid conflicts",
             "Disable extra TTYs in /etc/inittab"],
            "MEDIUM", 0.7
        ),
        
        # Error 14: VNC Connection Fails
        ErrorPattern(
            "E014", "VNC Connection Refused",
            [r"vnc.*refused", r"vnc.*timeout", r"vnc.*unable to connect"],
            ["VNC server not started in QEMU", "Wrong port number"],
            ["Enable VNC: -vnc :0",
             "Check port: netstat -tlnp | grep 5900",
             "Try different port: -vnc :1 (port 5901)"],
            "LOW", 0.8
        ),
        
        # Error 15: SSH Timeout
        ErrorPattern(
            "E015", "SSH Connection Timeout",
            [r"ssh.*refused", r"ssh.*timeout", r"port.*closed"],
            ["Port forwarding not configured", "SSH daemon not running"],
            ["Add port forwarding: -net user,hostfwd=tcp::2222-:22",
             "Start SSH daemon in MINIX: /usr/sbin/sshd &",
             "Add to rc.local: /usr/sbin/sshd"],
            "LOW", 0.75
        ),
    ]

class MinixErrorTriager:
    """Main error diagnosis engine"""
    
    def __init__(self):
        self.registry = MinixErrorRegistry()
        self.detected_errors = []
    
    def analyze_log(self, log_path: Path) -> Dict:
        """Analyze boot log and detect errors"""
        if not log_path.exists():
            return {"status": "ERROR", "message": f"Log file not found: {log_path}"}
        
        try:
            with open(log_path, 'r', errors='ignore') as f:
                log_content = f.read()
        except Exception as e:
            return {"status": "ERROR", "message": f"Failed to read log: {e}"}
        
        # Detect all errors
        detected = []
        for error_pattern in self.registry.ERRORS:
            if error_pattern.match(log_content):
                detected.append({
                    "id": error_pattern.error_id,
                    "name": error_pattern.name,
                    "severity": error_pattern.severity,
                    "confidence": error_pattern.confidence,
                    "root_causes": error_pattern.root_causes,
                    "solutions": error_pattern.solutions,
                })
        
        self.detected_errors = detected
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "log_file": str(log_path),
            "log_size_bytes": len(log_content),
            "log_lines": len(log_content.split('\n')),
            "errors_detected": len(detected),
            "errors": detected,
            "summary": self._generate_summary(detected),
            "recommendations": self._generate_recommendations(detected),
        }
        
        return report
    
    def _generate_summary(self, errors: List[Dict]) -> str:
        """Generate text summary of detected errors"""
        if not errors:
            return "No known errors detected. Boot may have completed successfully."
        
        lines = []
        lines.append(f"Detected {len(errors)} error(s):\n")
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_errors = sorted(errors, key=lambda x: severity_order.get(x["severity"], 999))
        
        for err in sorted_errors:
            lines.append(f"  [{err['severity']}] {err['id']}: {err['name']}")
            lines.append(f"    Confidence: {err['confidence']*100:.0f}%")
            lines.append(f"    Root causes: {', '.join(err['root_causes'][:2])}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_recommendations(self, errors: List[Dict]) -> List[str]:
        """Generate prioritized fix recommendations"""
        if not errors:
            return []
        
        # Collect all solutions, deduplicate, prioritize
        all_solutions = []
        for err in errors:
            for solution in err['solutions'][:2]:  # Take top 2 per error
                all_solutions.append({
                    "solution": solution,
                    "error_id": err['id'],
                    "severity": err['severity'],
                })
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_solutions.sort(key=lambda x: severity_order.get(x["severity"], 999))
        
        # Return unique solutions
        seen = set()
        recommendations = []
        for sol_dict in all_solutions:
            sol = sol_dict['solution']
            if sol not in seen:
                recommendations.append(sol)
                seen.add(sol)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def print_report(self, report: Dict):
        """Print formatted report to console"""
        print("\n" + "="*80)
        print("MINIX BOOT ERROR ANALYSIS REPORT")
        print("="*80)
        print(f"Log File: {report['log_file']}")
        print(f"Generated: {report['timestamp']}")
        print(f"Log Size: {report['log_size_bytes']} bytes ({report['log_lines']} lines)")
        print(f"Errors Detected: {report['errors_detected']}")
        print("\n" + "-"*80)
        print("SUMMARY")
        print("-"*80)
        print(report['summary'])
        
        if report['recommendations']:
            print("\n" + "-"*80)
            print("RECOMMENDED FIXES (In Priority Order)")
            print("-"*80)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        
        if report['errors']:
            print("\n" + "-"*80)
            print("DETAILED ERROR ANALYSIS")
            print("-"*80)
            for err in report['errors']:
                print(f"\n[{err['severity']}] {err['id']}: {err['name']}")
                print(f"  Confidence: {err['confidence']*100:.0f}%")
                print(f"  Root Causes:")
                for cause in err['root_causes']:
                    print(f"    - {cause}")
                print(f"  Solutions:")
                for sol in err['solutions']:
                    print(f"    - {sol}")
        
        print("\n" + "="*80)
    
    def save_report_json(self, report: Dict, output_path: Path):
        """Save report as JSON"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"JSON report saved: {output_path}")
    
    def save_report_md(self, report: Dict, output_path: Path):
        """Save report as Markdown"""
        lines = []
        lines.append(f"# MINIX Error Analysis Report")
        lines.append(f"\nGenerated: {report['timestamp']}")
        lines.append(f"Log File: {report['log_file']}")
        lines.append(f"Log Size: {report['log_size_bytes']} bytes ({report['log_lines']} lines)")
        lines.append(f"\n## Summary\n")
        lines.append(report['summary'])
        
        if report['recommendations']:
            lines.append(f"\n## Recommended Fixes\n")
            for i, rec in enumerate(report['recommendations'], 1):
                lines.append(f"{i}. {rec}")
        
        if report['errors']:
            lines.append(f"\n## Detailed Error Analysis\n")
            for err in report['errors']:
                lines.append(f"### [{err['severity']}] {err['id']}: {err['name']}")
                lines.append(f"- **Confidence**: {err['confidence']*100:.0f}%")
                lines.append(f"- **Root Causes**:")
                for cause in err['root_causes']:
                    lines.append(f"  - {cause}")
                lines.append(f"- **Solutions**:")
                for sol in err['solutions']:
                    lines.append(f"  - {sol}")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        print(f"Markdown report saved: {output_path}")


def watch_log(log_path: Path, interval: int = 2):
    """Watch log file for new errors (continuous monitoring)"""
    triager = MinixErrorTriager()
    last_size = 0
    
    print(f"Watching: {log_path}")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            if log_path.exists():
                current_size = log_path.stat().st_size
                if current_size > last_size:
                    report = triager.analyze_log(log_path)
                    if report.get('errors_detected', 0) > 0:
                        triager.print_report(report)
                    last_size = current_size
            
            import time
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="MINIX Boot Error Triage Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze boot log
  python3 triage-minix-errors.py measurements/i386/boot.log
  
  # Watch boot log in real-time
  python3 triage-minix-errors.py --watch measurements/i386/boot.log
  
  # Save report as JSON
  python3 triage-minix-errors.py -o report.json boot.log
  
  # Save report as Markdown
  python3 triage-minix-errors.py -o report.md --format md boot.log
        """
    )
    
    parser.add_argument("log_file", nargs='?', help="Boot log file to analyze")
    parser.add_argument("-o", "--output", help="Output file for report")
    parser.add_argument("--format", choices=["json", "md"], default="json",
                      help="Output format (default: json)")
    parser.add_argument("--watch", action="store_true",
                      help="Watch log file for new errors (continuous monitoring)")
    parser.add_argument("-q", "--quiet", action="store_true",
                      help="Don't print to console")
    
    args = parser.parse_args()
    
    if not args.log_file and not args.watch:
        parser.print_help()
        return 1
    
    if args.watch:
        if not args.log_file:
            print("ERROR: Must specify log file with --watch")
            return 1
        watch_log(Path(args.log_file))
        return 0
    
    # Analyze log
    triager = MinixErrorTriager()
    report = triager.analyze_log(Path(args.log_file))
    
    if report.get('status') == 'ERROR':
        print(f"ERROR: {report['message']}")
        return 1
    
    if not args.quiet:
        triager.print_report(report)
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        if args.format == "json":
            triager.save_report_json(report, output_path)
        else:
            triager.save_report_md(report, output_path)
    
    # Exit code based on error severity
    critical_count = len([e for e in report['errors'] if e['severity'] == 'CRITICAL'])
    high_count = len([e for e in report['errors'] if e['severity'] == 'HIGH'])
    
    if critical_count > 0:
        return 2  # Critical error
    elif high_count > 0:
        return 1  # High-level error
    else:
        return 0  # OK


if __name__ == '__main__':
    sys.exit(main())
