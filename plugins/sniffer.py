import socket
import argparse
import platform
import sys
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class SnifferPlugin(BasePlugin):
    @property
    def name(self) -> str: return "sniffer"
    @property
    def description(self) -> str: return "4SM-Sniffer: Cross-Platform Reliable Raw Telemetry Interceptor"

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-i", "--interface", default="ANY", help="Interface bound (Ignored on Windows)")

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        current_os = platform.system()
        print(f"\033[1;33m[*] Initializing Raw Promiscuous Sniffer Sub-system on {current_os}...\033[0m")
        
        try:
            if current_os == "Windows":
                # Windows Promiscuous Mode Socket Hardening
                host_ip = socket.gethostbyname(socket.gethostname())
                raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                raw_socket.bind((host_ip, 0))
                raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                raw_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            elif current_os in ["Linux", "Darwin"]: # Kali, BlackArch, macOS
                # Linux/macOS Packet capture hardening
                raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            raw_socket.settimeout(10.0)
            print("\033[1;32m[+] Network Pipeline Connected. Capturing live stream data packet chunks...\033[0m")
            
            packet, addr = raw_socket.recvfrom(65565)
            print(f"  \033[1;32m[+] Packet Intercepted from {addr[0]} | Chunk Size: {len(packet)} Bytes\033[0m")
            
            # Clean up Windows state
            if current_os == "Windows":
                raw_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            raw_socket.close()
            return 0
        except PermissionError:
            print("\033[1;31m[-] Privilege Deficit: Raw sniffing requires Root/Administrator privileges.\033[0m")
            print("\033[1;36m    [Hint] Run via 'sudo python 4sm_enterprise.py' or elevated PowerShell.\033[0m")
            return 1
        except Exception as e:
            print(f"\033[1;31m[-] Interception Failed: {str(e)}\033[0m")
            return 1