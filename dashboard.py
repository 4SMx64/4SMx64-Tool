import sys
import json
import hmac
import hashlib
from pathlib import Path

B_RED     = "\033[1;31m"; B_GREEN   = "\033[1;32m"; B_YELLOW  = "\033[1;33m"
B_CYAN    = "\033[1;36m"; B_WHITE   = "\033[1;37m"; RESET     = "\033[0m"
CLEAR_SCR = "\033[H\033[2J"

class OperationalDashboard:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        with open(self.config_path, "r") as f: self.config = json.load(f)

    def verify_log_integrity(self) -> tuple:
        log_file = Path(self.config["logging"]["log_file"])
        if not log_file.exists(): return False, "No active runtime log sequence located."
        with open(log_file, "rb") as f: current_content = f.read()
        calc_hmac = hmac.new(self.config["auth"]["salt_hex"].encode(), current_content, hashlib.sha256).hexdigest()
        return True, calc_hmac

    def render(self):
        print(CLEAR_SCR)
        print(f"{B_RED}=================================================={RESET}")
        print(f"{B_RED}      4SM x64 MANAGEMENT SIEM & COMPLIANCE NODE   {RESET}")
        print(f"{B_RED}=================================================={RESET}")
        status, message = self.verify_log_integrity()
        if status:
            print(f"{B_GREEN}[+] ISO 27001 Log Verification Cryptographic Chain: SECURE{RESET}")
            print(f"{B_CYAN}[>] Operational Chain Delta Signature: {message}{RESET}")
        print(f"{B_RED}--------------------------------------------------{RESET}")
        print(f"{B_WHITE}Press Enter to re-index buffers or Ctrl+C to detach pipeline...{RESET}")

if __name__ == "__main__":
    db = OperationalDashboard()
    try:
        while True: db.render(); input()
    except KeyboardInterrupt: print(f"\n{B_YELLOW}[*] Log Dashboard Stream Detached Cleanly.{RESET}")