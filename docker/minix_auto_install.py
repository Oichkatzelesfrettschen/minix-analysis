#!/usr/bin/env python3
"""
MINIX 3.4 RC6 Automated Installation Script
Automates the MINIX installation process using pexpect and QEMU serial console.

Author: Automated installation framework for MINIX boot profiling
License: MIT
"""

import pexpect
import sys
import time
import argparse
from pathlib import Path

class MinixInstaller:
    def __init__(self, iso_path, disk_image, disk_size="2G", memory="512M", timeout=600):
        self.iso_path = iso_path
        self.disk_image = disk_image
        self.disk_size = disk_size
        self.memory = memory
        self.timeout = timeout
        self.child = None

    def create_disk_image(self):
        """Create a blank disk image for installation."""
        print(f"[*] Creating {self.disk_size} disk image: {self.disk_image}")
        import subprocess
        subprocess.run([
            "qemu-img", "create", "-f", "qcow2",
            self.disk_image, self.disk_size
        ], check=True)

    def start_qemu(self):
        """Start QEMU with serial console enabled."""
        cmd = [
            "qemu-system-i386",
            "-m", self.memory,
            "-cdrom", self.iso_path,
            "-hda", self.disk_image,
            "-boot", "d",  # Boot from CD-ROM first
            "-serial", "stdio",  # Redirect serial to stdio
            "-nographic",  # No graphical window
            "-enable-kvm",  # Use KVM acceleration if available
        ]

        print(f"[*] Starting QEMU: {' '.join(cmd)}")
        self.child = pexpect.spawn(" ".join(cmd), encoding='utf-8', timeout=self.timeout)
        self.child.logfile_read = sys.stdout  # Echo all output

    def wait_and_send(self, pattern, response, timeout=None):
        """Wait for a pattern and send a response."""
        if timeout is None:
            timeout = self.timeout
        print(f"[*] Waiting for: {pattern}")
        self.child.expect(pattern, timeout=timeout)
        time.sleep(0.5)  # Small delay to avoid overwhelming serial
        print(f"[*] Sending: {response}")
        self.child.sendline(response)
        time.sleep(0.5)

    def install(self):
        """Execute the complete MINIX installation sequence."""
        try:
            # Step 1: Wait for boot and login prompt
            print("\n[STEP 1] Waiting for login prompt...")
            self.wait_and_send(r'(?i)login:', 'root', timeout=60)

            # Step 2: No password required, press enter
            print("\n[STEP 2] Bypassing password (press enter)...")
            time.sleep(2)
            self.child.sendline('')

            # Step 3: Wait for shell prompt and start setup
            print("\n[STEP 3] Starting setup...")
            self.wait_and_send(r'#', 'setup', timeout=10)

            # Step 4: Initial setup prompt (press enter to continue)
            print("\n[STEP 4] Confirming setup start...")
            self.wait_and_send(r'Press ENTER to continue', '', timeout=10)

            # Step 5: Keyboard selection (accept default)
            print("\n[STEP 5] Selecting keyboard (us-std)...")
            self.wait_and_send(r'Keyboard type\?', '', timeout=10)

            # Step 6: Partition mode (automatic, not expert)
            print("\n[STEP 6] Selecting automatic partition mode...")
            self.wait_and_send(r'expert', '', timeout=10)

            # Step 7: Select first drive (if prompted)
            print("\n[STEP 7] Selecting first drive...")
            # This step may vary - might auto-detect single drive
            try:
                self.wait_and_send(r'(?i)select.*drive', '1', timeout=5)
            except pexpect.TIMEOUT:
                print("[*] Drive auto-detected, continuing...")

            # Step 8: Confirm partition destruction
            print("\n[STEP 8] Confirming partition selection...")
            self.wait_and_send(r'(?i)yes.*no', 'yes', timeout=10)

            # Step 9: Full install (not reinstall)
            print("\n[STEP 9] Selecting full install...")
            self.wait_and_send(r'Full or.*Reinstall', '', timeout=10)

            # Step 10: Accept default home partition size
            print("\n[STEP 10] Accepting default home partition size...")
            self.wait_and_send(r'How big.*home', '', timeout=10)

            # Step 11: Confirm home size
            print("\n[STEP 11] Confirming home partition size...")
            self.wait_and_send(r'Ok\?', '', timeout=10)

            # Step 12: Accept default block size
            print("\n[STEP 12] Accepting default block size...")
            self.wait_and_send(r'Block size', '', timeout=10)

            # Step 13: Wait for file copying to complete
            print("\n[STEP 13] Waiting for file copy (may take 2-3 minutes)...")
            self.wait_and_send(r'(?i)copy.*complete|(?i)installation.*complete', '', timeout=300)

            # Step 14: Skip ethernet configuration (or configure if needed)
            print("\n[STEP 14] Skipping ethernet configuration...")
            try:
                self.wait_and_send(r'(?i)ethernet', '', timeout=10)
            except pexpect.TIMEOUT:
                print("[*] No ethernet prompt, continuing...")

            # Step 15: Shutdown the system
            print("\n[STEP 15] Shutting down installer...")
            self.wait_and_send(r'#', 'shutdown', timeout=10)

            # Wait for shutdown to complete
            print("\n[*] Waiting for shutdown...")
            time.sleep(5)

            print("\n[SUCCESS] Installation completed successfully!")
            return True

        except pexpect.TIMEOUT as e:
            print(f"\n[ERROR] Timeout waiting for prompt: {e}")
            print(f"[DEBUG] Last output: {self.child.before}")
            return False
        except pexpect.EOF as e:
            print(f"\n[ERROR] Unexpected EOF: {e}")
            return False
        except Exception as e:
            print(f"\n[ERROR] Installation failed: {e}")
            return False
        finally:
            if self.child:
                self.child.close()

    def boot_installed_system(self):
        """Boot the installed MINIX system (without CD-ROM)."""
        cmd = [
            "qemu-system-i386",
            "-m", self.memory,
            "-hda", self.disk_image,
            "-boot", "c",  # Boot from hard disk
            "-serial", "stdio",
            "-nographic",
            "-enable-kvm",
        ]

        print(f"\n[*] Booting installed system: {' '.join(cmd)}")
        self.child = pexpect.spawn(" ".join(cmd), encoding='utf-8', timeout=self.timeout)
        self.child.logfile_read = sys.stdout

        # Wait for login prompt
        print("\n[*] Waiting for boot to complete...")
        self.child.expect(r'(?i)login:', timeout=120)
        print("\n[SUCCESS] System booted successfully!")

        # Login
        self.child.sendline('root')
        time.sleep(1)
        self.child.sendline('')  # No password

        # Interactive mode
        print("\n[*] Entering interactive mode. Press Ctrl+] to exit.")
        self.child.interact()

def main():
    parser = argparse.ArgumentParser(description="Automated MINIX 3.4 RC6 Installation")
    parser.add_argument("--iso", required=True, help="Path to MINIX ISO file")
    parser.add_argument("--disk", required=True, help="Path to output disk image")
    parser.add_argument("--size", default="2G", help="Disk size (default: 2G)")
    parser.add_argument("--memory", default="512M", help="RAM allocation (default: 512M)")
    parser.add_argument("--boot", action="store_true", help="Boot installed system after install")
    parser.add_argument("--no-create", action="store_true", help="Don't create disk (use existing)")

    args = parser.parse_args()

    # Verify ISO exists
    if not Path(args.iso).exists():
        print(f"[ERROR] ISO file not found: {args.iso}")
        sys.exit(1)

    # Create installer
    installer = MinixInstaller(
        iso_path=args.iso,
        disk_image=args.disk,
        disk_size=args.size,
        memory=args.memory
    )

    # Create disk image if needed
    if not args.no_create:
        installer.create_disk_image()

    # Start QEMU and install
    installer.start_qemu()
    success = installer.install()

    if not success:
        print("\n[ERROR] Installation failed!")
        sys.exit(1)

    # Boot installed system if requested
    if args.boot:
        print("\n[*] Proceeding to boot installed system...")
        time.sleep(2)
        installer.boot_installed_system()

if __name__ == "__main__":
    main()
