import ipaddress
import socket
import argparse
import logging
import subprocess
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class NetEyePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "neteye"

    @property
    def description(self) -> str:
        return "4SM-NetEye: Advanced Endpoint Mapping and Target Verification"

    def _validate_target(self, target: str) -> str:
        """Performs robust RFC-compliant DNS resolution and IP verification (IPv4/IPv6)."""
        target_normalized = target.strip().encode('idna').decode('ascii')
        
        # Check if valid IP Address
        try:
            ipaddress.ip_address(target_normalized)
            return target_normalized
        except ValueError:
            pass

        # Check if valid resolving Domain
        try:
            socket.getaddrinfo(target_normalized, None)
            return target_normalized
        except socket.gaierror:
            raise ValueError(f"Target '{target}' failed structural DNS/IP verification.")

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-t", "--target", required=True, help="Target IPv4, IPv6 or Domain name")
        parser.add_argument("-m", "--mode", choices=["quick", "deep"], default="quick", help="Scanning profile matrix")

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        try:
            validated_target = self._validate_target(args.target)
            timeout = config["execution"]["subprocess_timeout_seconds"]
            retries = config["execution"]["retry_attempts"]

            cmd = ["nmap", "-F", validated_target] if args.mode == "quick" else ["nmap", "-A", "-v", validated_target]
            
            if config["execution"]["safe_mode"]:
                print(f"[DRY-RUN] Would execute command: {' '.join(cmd)}")
                return 0

            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"Executing NetEye Scan on {validated_target} (Attempt {attempt}/{retries})")
                    result = subprocess.run(
                        cmd, 
                        shell=False, 
                        capture_output=True, 
                        text=True, 
                        timeout=timeout, 
                        check=True
                    )
                    print(result.stdout)
                    return 0
                except subprocess.TimeoutExpired:
                    logging.warning(f"NetEye Subprocess timeout reached on attempt {attempt}")
                    if attempt == retries:
                        raise RuntimeError("Subprocess critical execution timeout.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"NetEye Error Output: {e.stderr}")
                    if attempt == retries:
                        return e.returncode
            return 1
        except Exception as e:
            print(f"[-] NetEye Module Execution Failure: {str(e)}")
            logging.error(f"Execution aborted in NetEye module context: {str(e)}")
            return 1