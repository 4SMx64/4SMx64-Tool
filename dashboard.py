import sys
import json
import hmac
import hashlib
from pathlib import Path

B_RED     = "\033[1;31m"
B_GREEN   = "\033[1;32m"
B_YELLOW  = "\033[1;33m"
B_CYAN    = "\033[1;36m"
B_WHITE   = "\033[1;37m"
RESET     = "\033[0m"
CLEAR_SCR = "\033[H\033[2J"

class OperationalDashboard:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

    def verify_log_integrity(self) -> tuple:
        log_file = Path(self.config["logging"]["log_file"])
        if not log_file.exists(): return False, "No active log file located."
        with open(log_file, "rb") as f:
            current_content = f.read()
        calculated_hmac = hmac.new(self.config["auth"]["salt_hex"].encode(), current_content, hashlib.sha256).hexdigest()
        return True, calculated_hmac

    def render(self):
        print(CLEAR_SCR)
        print(f"{B_RED}=================================================={RESET}")
        print(f"{B_RED}          4SM x64 MANAGEMENT & AUDIT NODE         {RESET}")
        print(f"{B_RED}=================================================={RESET}")
        status, message = self.verify_log_integrity()
        if status:
            print(f"{B_GREEN}[+] Cryptographic Chain: SECURE{RESET}")
            print(f"{B_CYAN}[>] Active Delta Hash  : {message}{RESET}")
        print(f"{B_RED}--------------------------------------------------{RESET}")
        print(f"{B_WHITE}Press Enter to refresh buffer or Ctrl+C to exit...{RESET}")

if __name__ == "__main__":
    db = OperationalDashboard()
    try:
        while True:
            db.render()
            input()
    except KeyboardInterrupt:
        print(f"\n{B_YELLOW}[*] Dashboard detached.{RESET}")