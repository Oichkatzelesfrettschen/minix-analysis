#!/usr/bin/env python3
"""
Generalized QEMU runner for MINIX testing.

This module provides a unified interface to control QEMU instances
within Docker containers, supporting both KVM-accelerated and pure
emulation modes.

Usage:
    from tools.testing.qemu_runner import QEMURunner
    
    runner = QEMURunner(config_path='.config/paths.yaml')
    runner.start_vm()
    runner.wait_for_boot()
    output = runner.send_command('ls -la')
    runner.stop_vm()
"""

import os
import sys
import time
import json
import socket
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import pexpect
import psutil
import yaml


class QEMUArchitecture(Enum):
    """Supported QEMU architectures."""
    I386 = "i386"
    X86_64 = "x86_64"
    ARM = "arm"
    ARM64 = "aarch64"


class QEMUMachine(Enum):
    """Supported QEMU machine types."""
    Q35 = "q35"
    I440FX = "i440fx"
    VIRT = "virt"


@dataclass
class QEMUConfig:
    """QEMU instance configuration."""
    arch: QEMUArchitecture = QEMUArchitecture.I386
    machine: QEMUMachine = QEMUMachine.Q35
    memory: str = "2G"
    cpus: int = 4
    disk_image: str = ""
    iso_image: str = ""
    enable_kvm: bool = True
    vnc_display: str = ":0"
    serial_port: Optional[str] = None
    monitor_port: int = 55555
    timeout: int = 60
    extra_args: List[str] = None

    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = []


class QEMURunner:
    """Unified QEMU control interface."""

    def __init__(self, config: Optional[QEMUConfig] = None, 
                 config_path: Optional[str] = None):
        """
        Initialize QEMU runner.
        
        Args:
            config: QEMUConfig instance
            config_path: Path to YAML configuration file
        """
        self.config = config or QEMUConfig()
        self.process = None
        self.serial_port = None
        self.is_running = False
        self.boot_time = None
        
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from YAML file."""
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
            if 'qemu' in cfg:
                qemu_cfg = cfg['qemu']
                for key, value in qemu_cfg.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
    
    def _build_qemu_command(self) -> List[str]:
        """Build QEMU command line arguments."""
        cmd = [
            f"qemu-system-{self.config.arch.value}",
            "-machine", self.config.machine.value,
            "-m", self.config.memory,
            "-smp", str(self.config.cpus),
        ]
        
        if self.config.enable_kvm:
            cmd.append("-enable-kvm")
        
        if self.config.disk_image:
            cmd.extend(["-drive", f"file={self.config.disk_image},format=qcow2"])
        
        if self.config.iso_image:
            cmd.extend(["-cdrom", self.config.iso_image])
        
        cmd.extend([
            "-vnc", self.config.vnc_display,
            "-monitor", f"tcp:127.0.0.1:{self.config.monitor_port},server,nowait",
        ])
        
        if self.config.serial_port:
            cmd.extend(["-serial", self.config.serial_port])
        else:
            cmd.extend(["-serial", "stdio"])
        
        cmd.extend(["-name", "minix-test"])
        cmd.extend(self.config.extra_args)
        
        return cmd
    
    def start_vm(self) -> bool:
        """
        Start QEMU virtual machine.
        
        Returns:
            True if VM started successfully, False otherwise
        """
        try:
            cmd = self._build_qemu_command()
            print(f"Starting QEMU: {' '.join(cmd)}")
            
            self.process = pexpect.spawn(
                cmd[0],
                args=cmd[1:],
                timeout=self.config.timeout,
                encoding='utf-8'
            )
            
            self.is_running = True
            self.boot_time = time.time()
            
            print("QEMU instance started")
            return True
        
        except Exception as e:
            print(f"Error starting QEMU: {e}", file=sys.stderr)
            self.is_running = False
            return False
    
    def wait_for_boot(self, prompt: str = "minix#", 
                      timeout: Optional[int] = None) -> bool:
        """
        Wait for VM to boot and reach shell prompt.
        
        Args:
            prompt: Shell prompt to wait for
            timeout: Override default timeout
        
        Returns:
            True if prompt found, False on timeout
        """
        if not self.process:
            print("QEMU process not running", file=sys.stderr)
            return False
        
        try:
            timeout_val = timeout or self.config.timeout
            self.process.expect(prompt, timeout=timeout_val)
            return True
        
        except pexpect.TIMEOUT:
            print(f"Timeout waiting for prompt: {prompt}", file=sys.stderr)
            return False
        except pexpect.EOF:
            print("QEMU process terminated unexpectedly", file=sys.stderr)
            return False
    
    def send_command(self, cmd: str, timeout: Optional[int] = None) -> str:
        """
        Send command to VM and capture output.
        
        Args:
            cmd: Shell command to execute
            timeout: Command timeout in seconds
        
        Returns:
            Command output as string
        """
        if not self.process or not self.is_running:
            raise RuntimeError("QEMU not running")
        
        try:
            self.process.sendline(cmd)
            timeout_val = timeout or self.config.timeout
            self.process.expect("[#$] ", timeout=timeout_val)
            return self.process.before
        
        except pexpect.TIMEOUT:
            raise TimeoutError(f"Command timeout: {cmd}")
        except Exception as e:
            raise RuntimeError(f"Command failed: {e}")
    
    def stop_vm(self, graceful: bool = True) -> bool:
        """
        Stop QEMU virtual machine.
        
        Args:
            graceful: Use graceful shutdown (poweroff) vs kill
        
        Returns:
            True if stopped successfully
        """
        if not self.process:
            return True
        
        try:
            if graceful:
                self.send_command("poweroff")
                time.sleep(2)
            
            if self.process.isalive():
                self.process.terminate()
                time.sleep(1)
            
            if self.process.isalive():
                self.process.kill()
            
            self.is_running = False
            return True
        
        except Exception as e:
            print(f"Error stopping QEMU: {e}", file=sys.stderr)
            return False
    
    def get_status(self) -> Dict[str, any]:
        """Get current VM status."""
        return {
            'running': self.is_running,
            'uptime': time.time() - self.boot_time if self.boot_time else None,
            'process_id': self.process.pid if self.process else None,
            'config': asdict(self.config),
        }


class DockerQEMURunner(QEMURunner):
    """QEMU runner with Docker container integration."""
    
    def __init__(self, container: str = "minix-qemu-test", **kwargs):
        """
        Initialize Docker-integrated QEMU runner.
        
        Args:
            container: Docker container name
            **kwargs: Additional arguments for QEMURunner
        """
        super().__init__(**kwargs)
        self.container = container
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            subprocess.run(["docker", "version"], 
                         capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def container_exec(self, cmd: str) -> str:
        """
        Execute command inside Docker container.
        
        Args:
            cmd: Command to execute
        
        Returns:
            Command output
        """
        if not self.docker_available:
            raise RuntimeError("Docker not available")
        
        try:
            result = subprocess.run(
                ["docker", "exec", self.container, "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Docker command timeout: {cmd}")
    
    def start_container(self) -> bool:
        """Start Docker container with QEMU."""
        if not self.docker_available:
            print("Docker not available", file=sys.stderr)
            return False
        
        try:
            subprocess.run([
                "docker-compose", "-f", "docker/qemu/docker-compose.yml",
                "up", "-d", "qemu-minix"
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start Docker container: {e}", file=sys.stderr)
            return False


if __name__ == "__main__":
    # Example usage
    config = QEMUConfig(
        arch=QEMUArchitecture.I386,
        memory="2G",
        cpus=4
    )
    
    runner = QEMURunner(config)
    
    if runner.start_vm():
        print("VM started, waiting for boot...")
        if runner.wait_for_boot():
            print("VM booted successfully")
            try:
                output = runner.send_command("uname -a")
                print(f"System info: {output}")
            finally:
                runner.stop_vm()
