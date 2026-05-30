import argparse
import logging
import subprocess
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class SnifferPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "sniffer"

    @property
    def description(self) -> str:
        return "4SM-Sniffer: Secure Port Binding Validation Interface"

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--port", type=int, required=True, help="Target port matrix (1-65535)")

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        try:
            if not (1 <= args.port <= 65535):
                raise ValueError("Port allocation metric out of standard limits.")
            
            cmd = ["nc", "-lvp", str(args.port), "-s", "127.0.0.1"]
            
            if config["execution"]["safe_mode"]:
                print(f"[DRY-RUN] Would bind listener: {' '.join(cmd)}")
                return 0

            logging.info(f"Spawning local bound intercept node on port {args.port}")
            result = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=config["execution"]["subprocess_timeout_seconds"])
            print(result.stdout)
            return 0
        except Exception as e:
            print(f"[-] Sniffer Structural Error: {str(e)}")
            logging.error(f"Sniffer operational failure: {str(e)}")
            return 1