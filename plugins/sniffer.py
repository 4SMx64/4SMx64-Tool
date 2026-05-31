import socket
import argparse
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class SnifferPlugin(BasePlugin):
    @property
    def name(self) -> str: return "sniffer"
    @property
    def description(self) -> str: return "4SM-Sniffer: Connection Interception Array"

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--port", type=int, default=4444, help="Port to bind")

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("0.0.0.0", args.port))
            server.listen(1)
            print(f"[*] Sniffer binding deployed on port {args.port}. Waiting for telemetry...")
            server.settimeout(float(config["execution"]["subprocess_timeout_seconds"]))
            conn, addr = server.accept()
            print(f"[+] Inbound stream captured from {addr[0]}:{addr[1]}")
            data = conn.recv(1024)
            if data:
                print(f"  Stream Content: {data.decode('utf-8', errors='ignore')}")
            conn.close()
            server.close()
            return 0
        except socket.timeout:
            print("[-] Sniffer socket reached execution timeout bound.")
            return 1
        except Exception as e:
            print(f"[-] Sniffer fault: {str(e)}")
            return 1