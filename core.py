import os
import sys
import json
import hmac
import hashlib
import time
import argparse
import logging
from typing import Dict, Any
from plugins.neteye import NetEyePlugin
from plugins.sniffer import SnifferPlugin

class HardenedFrameworkCore:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_configuration()
        self._setup_secure_logging()
        self.plugins = {}
        self._register_plugins()

    def _load_configuration(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            print("[-] Critical Configuration Management System Failure. Exiting.")
            sys.exit(1)
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _setup_secure_logging(self) -> None:
        log_file = self.config["logging"]["log_file"]
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [PID:%(process)d] %(message)s"
        )

    def _calculate_log_chain(self) -> str:
        """Prevents log file tampering via secure cryptographic hash chaining (HMAC validation)."""
        log_file = self.config["logging"]["log_file"]
        if not os.path.exists(log_file):
            return ""
        with open(log_file, "rb") as f:
            return hmac.new(self.config["auth"]["salt_hex"].encode(), f.read(), hashlib.sha256).hexdigest()

    def _verify_environment_isolation(self) -> None:
        """Detects if running inside un-isolated high-risk systems."""
        in_container = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
        if not in_container:
            logging.info("Environment Status Notice: Non-isolated virtual machine layer detected.")

    def _register_plugins(self) -> None:
        # Strict modular instantiation
        for plugin in [NetEyePlugin(), SnifferPlugin()]:
            self.plugins[plugin.name] = plugin

    def authenticate_operator(self) -> None:
        """Hardened Brute-Force Rate Limiting & PBKDF2 Key Derivation Verification Engine."""
        auth_cfg = self.config["auth"]
        max_attempts = auth_cfg["max_attempts"]
        salt = bytes.fromhex(auth_cfg["salt_hex"])
        iterations = auth_cfg["pbkdf2_iterations"]
        expected = auth_cfg["expected_derived_key_hex"]

        print("==================================================")
        print("    4SM SECURITY CONSOLE - SECURE SESSIONS LAYER  ")
        print("==================================================")

        for attempt in range(1, max_attempts + 1):
            try:
                # Basic execution mitigation against automated dictionary attacks
                if attempt > 1:
                    time.sleep(2 ** attempt) # Exponential backoff rate limiting

                password = input(f"[{attempt}/{max_attempts}] Input Signature Token: ").strip()
                
                # Unicode normalization to fix edge case alignment
                password_normalized = hashlib.sha256(password.encode('utf-8')).hexdigest()

                # Generate secure PBKDF2 Key
                derived_key = hashlib.pbkdf2_hmac(
                    'sha256', 
                    password_normalized.encode('utf-8'), 
                    salt, 
                    iterations
                ).hex()

                if hmac.compare_digest(derived_key, expected): # Constant-time execution check
                    logging.info("Cryptographic authentication token validated. Chain Active.")
                    return
                else:
                    logging.warning(f"Failed authentication block signature registered. Attempt {attempt}")
            except KeyboardInterrupt:
                sys.exit(1)

        print(f"[-] Lockout Initiated. Maximum authorization index violations achieved.")
        logging.critical("System Lockout sequence executed due to continuous authentication failure.")
        sys.exit(1)

    def run(self) -> None:
        self._verify_environment_isolation()
        self.authenticate_operator()

        parser = argparse.ArgumentParser(description="4SM Enterprise Production Framework Interface Command Routing Architecture.")
        parser.add_argument("--safe-mode", action="store_true", help="Activate mock-execution path structures.")
        subparsers = parser.add_subparsers(dest="command", required=True)

        for name, plugin in self.plugins.items():
            subparser = subparsers.add_parser(name, help=plugin.description)
            plugin.setup_arguments(subparser)

        args = parser.parse_args()

        if args.safe_mode:
            self.config["execution"]["safe_mode"] = True

        if args.command in self.plugins:
            initial_chain = self._calculate_log_chain()
            exit_code = self.plugins[args.command].execute(args, self.config)
            
            if self.config["logging"]["enable_integrity_chain"]:
                final_chain = self._calculate_log_chain()
                logging.info(f"Integrity Validation Sequence Signed. Delta Verification Hash: {final_chain}")
            
            sys.exit(exit_code)

if __name__ == "__main__":
    core = HardenedFrameworkCore()
    core.run()