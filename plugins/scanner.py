import socket
import argparse
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class ScannerPlugin(BasePlugin):
    @property
    def name(self) -> str: return "neteye"
    @property
    def description(self) -> str: return "4SM-Scanner: Safe Network Discovery Engine"

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-t", "--target", required=True, help="Target IPv4/Domain")
        parser.add_argument("-p", "--ports", default="22,80,443,445,3389", help="Port list")

    def _scan_port(self, target: str, port: int, timeout: float) -> None:
        try:
            resolved_ip = socket.gethostbyname(target)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((resolved_ip, port))
                if result == 0:
                    print(f"  {port} -> OPEN")
                    conn = sqlite3.connect("enterprise_assets.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR IGNORE INTO inventory (target, vector_type, status, details) VALUES (?, 'NETEYE', 'OPEN', ?)", (resolved_ip, f"Port {port} confirmed active"))
                    conn.commit()
                    conn.close()
        except Exception:
            pass

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        try:
            ports = [int(p.strip()) for p in args.ports.split(",") if p.strip().isdigit()]
            timeout = float(config["execution"]["subprocess_timeout_seconds"]) / 10
            print(f"[*] Launching neteye discovery against {args.target}...")
            with ThreadPoolExecutor(max_workers=50) as executor:
                for port in ports:
                    executor.submit(self._scan_port, args.target, port, timeout)
            print("[+] Scan finished. Targets logged to Enterprise DB.")
            return 0
        except Exception as e:
            print(f"[-] Neteye Exception: {str(e)}")
            return 1