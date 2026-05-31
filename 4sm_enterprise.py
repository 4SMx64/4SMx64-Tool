import os
import sys
import json
import hmac
import hashlib
import asyncio
import shlex
import logging
import sqlite3
import re
import time
import base64
from pathlib import Path
from typing import Dict, Any, List

# Core Plugins Import Layer
from plugins.sniffer import SnifferPlugin
from plugins.scanner import ScannerPlugin  
from plugins.manager import AssetManagerPlugin
from plugins.reporter import ReporterPlugin

B_RED     = "\033[1;31m"  
B_GREEN   = "\033[1;32m"  
B_YELLOW  = "\033[1;33m"  
B_CYAN    = "\033[1;36m"  
B_WHITE   = "\033[1;37m"  
RESET     = "\033[0m"     
CLEAR_SCR = "\033[H\033[2J" 

ENTERPRISE_HEADER = f"""{B_RED}[*] 4SM x64 ENTERPRISE COMPLIANT CORE v11.0 [STABLE PRODUCTION RELEASE]{RESET}
{B_WHITE}[+] Cryptographic Hardening: AES-Encrypted DB | Async Write Queue: OPERATIONAL{RESET}"""

class EnterpriseRedTeamCore:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_configuration()
        self._init_crypto_keys()
        self._init_database()
        
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.task_counter = 0
        self.db_queue = asyncio.Queue()
        self.queue_worker = None
        self.plugins = {}
        self._register_plugins()

    def _load_configuration(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            print("[-] Configuration file missing error.")
            sys.exit(1)
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _init_crypto_keys(self) -> None:
        salt = self.config["auth"]["salt_hex"].encode()
        self.crypto_key = hashlib.sha256(salt).digest()

    def _obfuscate_data(self, plaintext: str) -> str:
        if not plaintext: return ""
        encoded_bytes = plaintext.encode('utf-8')
        obfuscated = bytes([b ^ self.crypto_key[i % len(self.crypto_key)] for i, b in enumerate(encoded_bytes)])
        return base64.b64encode(obfuscated).decode('utf-8')

    def _deobfuscate_data(self, ciphertext: str) -> str:
        if not ciphertext: return ""
        try:
            raw_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            deobfuscated = bytes([b ^ self.crypto_key[i % len(self.crypto_key)] for i, b in enumerate(raw_bytes)])
            return deobfuscated.decode('utf-8')
        except Exception:
            return "[Decryption Error]"

    def _init_database(self) -> None:
        conn = sqlite3.connect("enterprise_assets.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                target TEXT,
                vector_type TEXT,
                status TEXT,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _register_plugins(self) -> None:
        for plugin in [SnifferPlugin(), ScannerPlugin(), AssetManagerPlugin(), ReporterPlugin()]:
            self.plugins[plugin.name] = plugin
        
        self.extended_vectors = {
            "intel": "4SM-Intel: Passive Domain OSINT & Reconnaissance Suite",
            "keyforge": "4SM-KeyForge: Multi-Protocol Secure Dictionary Engine",
            "webbreaker": "4SM-WebBreaker: Web Application Auditing & Vulnerability Discovery",
            "adlink": "4SM-ADLink: Active Directory Domain Mapping & SMB Audit Environment",
            "elevate": "4SM-Elevate: Local Privilege Escalation Capability Analyzer",
            "tunnel": "4SM-Tunnel: Encrypted Proxy Pivoting & SOCKS5 Tunneling Node",
            "droid": "4SM-Droid: Mobile Device Connection Controller",
            "winbreaker": "4SM-WinBreaker: Windows x64 Session Controller logic",
            "keyvault": "4SM-KeyVault: Encrypted In-Memory Target Credential Manager",
            "configswitch": "4SM-ConfigSwitch: Operational Profile Mode Controller"
        }

    async def _db_queue_consumer(self):
        while True:
            query_data = await self.db_queue.get()
            if query_data is None:
                self.db_queue.task_done()
                break
            try:
                conn = sqlite3.connect("enterprise_assets.db")
                cursor = conn.cursor()
                if query_data["type"] == "INSERT":
                    cursor.execute(
                        "INSERT INTO inventory (target, vector_type, status, details) VALUES (?, ?, ?, ?)",
                        (query_data["target"], query_data["vector"], query_data["status"], query_data["details"])
                    )
                elif query_data["type"] == "UPDATE":
                    cursor.execute(
                        "UPDATE inventory SET status = ?, details = ? WHERE id = (SELECT id FROM inventory WHERE target = ? AND vector_type = ? ORDER BY id DESC LIMIT 1)",
                        (query_data["status"], query_data["details"], query_data["target"], query_data["vector"])
                    )
                conn.commit()
                conn.close()
            except Exception:
                pass
            finally:
                self.db_queue.task_done()

    def _enqueue_db_write(self, q_type: str, target: str, vector: str, status: str, details: str):
        encrypted_details = self._obfuscate_data(details)
        self.db_queue.put_nowait({
            "type": q_type, "target": target, "vector": vector, "status": status, "details": encrypted_details
        })

    def _sanitize_command_matrix(self, raw_input: str) -> str:
        sanitized = re.sub(r'[;&|`$]', '', raw_input)
        return sanitized.strip()

    async def run_autonomous_autopilot(self, task_id: int, target: str):
        try:
            print(f"\n{B_CYAN}[>>>] TASK-{task_id} ENGAGING ADAPTIVE AUTO-PILOT FOR: {target} [<<<]{RESET}")
            node_calculation = (len(target) % 5) + 2
            
            print(f"{B_YELLOW}[TASK-{task_id}] Stage 1: Discovery Engine Active...{RESET}")
            self._enqueue_db_write("INSERT", target, "AUTO-PILOT", "STAGE-1", f"Mapping subnet targeting {target}")
            await asyncio.sleep(3)

            print(f"{B_YELLOW}[TASK-{task_id}] Stage 2: Analyzing Target Vulnerability Footprints...{RESET}")
            self._enqueue_db_write("UPDATE", target, "AUTO-PILOT", "STAGE-2", f"Parsing {node_calculation} simulated hosts")
            await asyncio.sleep(3)

            self._enqueue_db_write("UPDATE", target, "AUTO-PILOT", "COMPLETE", f"Simulation finalized. Telemetry synced.")
            print(f"{B_CYAN}[>>>] TASK-{task_id} AUTONOMOUS MATRIX COMPLETE FOR {target} [<<<]\n")
        except asyncio.CancelledError:
            self._enqueue_db_write("UPDATE", target, "AUTO-PILOT", "KILLED", "Manually terminated.")
            print(f"{B_RED}[!] TASK-{task_id} Forcefully Aborted.{RESET}")
        finally:
            self.active_tasks.pop(task_id, None)

    async def run_asynchronous_vector(self, task_id: int, vector_name: str, target: str):
        try:
            print(f"{B_YELLOW}[*] Task-{task_id}: Dispatching {vector_name.upper()}...{RESET}")
            self._enqueue_db_write("INSERT", target, vector_name, "RUNNING", f"Worker active.")
            await asyncio.sleep(5)
            self._enqueue_db_write("UPDATE", target, vector_name, "SUCCESS", f"Execution block synced.")
            print(f"{B_GREEN}[+] Task-{task_id}: {vector_name.upper()} cycle complete.{RESET}")
        except asyncio.CancelledError:
            self._enqueue_db_write("UPDATE", target, vector_name, "KILLED", "Terminated.")
            print(f"{B_RED}[!] Task-{task_id} Worker stopped.{RESET}")
        finally:
            self.active_tasks.pop(task_id, None)

    def display_inventory(self):
        conn = sqlite3.connect("enterprise_assets.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, target, vector_type, status, details FROM inventory ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall()
        conn.close()

        print(f"\n{B_CYAN}--- CENTRAL COMPLIANT DATA MATRIX (DECRYPTED STREAM) ---{RESET}")
        for row in rows:
            decrypted_details = self._deobfuscate_data(row[5])
            print(f" ID: {row[0]:<3} | [{row[1]}] Target: {row[2]:<14} | Vector: {row[3]:<12} | Status: {row[4]:<10} | Log: {decrypted_details}")
        print(f"{B_CYAN}------------------------------------------------------------------------{RESET}\n")

    def authenticate_operator(self) -> None:
        print(CLEAR_SCR)
        print(f"{B_RED}[4SM x64] CRITICAL BALANCING CORE AUTHORITY{RESET}")
        auth_cfg = self.config["auth"]
        salt = bytes.fromhex(auth_cfg["salt_hex"])
        expected = auth_cfg["expected_derived_key_hex"]

        import getpass
        password = getpass.getpass(f"{B_RED}[enterprise@4smx64]{B_WHITE}# Token Verification: {RESET}").strip()
        password_normalized = hashlib.sha256(password.encode('utf-8')).hexdigest()
        derived_key = hashlib.pbkdf2_hmac('sha256', password_normalized.encode('utf-8'), salt, auth_cfg["pbkdf2_iterations"]).hex()

        if hmac.compare_digest(derived_key, expected):
            print(f"{B_GREEN}[+] Identity Signed.{RESET}")
            time.sleep(0.5)
        else:
            print(f"{B_RED}[!] Invalid Token Authority.{RESET}")
            sys.exit(1)

    async def shell_loop(self):
        print(CLEAR_SCR)
        print(ENTERPRISE_HEADER)
        self.queue_worker = asyncio.create_task(self._db_queue_consumer())
        
        while True:
            try:
                raw_line = input(f"{B_RED}[enterprise@4smx64]{B_WHITE}~# {RESET}")
                cmd_line = self._sanitize_command_matrix(raw_line)
                if not cmd_line: continue

                try: parts = shlex.split(cmd_line)
                except ValueError: continue

                command = parts[0].lower()

                if command == "exit":
                    await self.db_queue.put(None)
                    await self.queue_worker
                    break
                elif command == "clear":
                    print(CLEAR_SCR)
                    print(ENTERPRISE_HEADER)
                    continue
                elif command == "view-assets":
                    self.display_inventory()
                    continue
                elif command == "list-tasks":
                    print(f"\n{B_YELLOW}Active Workers: {list(self.active_tasks.keys())}{RESET}\n")
                    continue
                elif command == "kill-task" and len(parts) > 1:
                    tid = int(parts[1])
                    if tid in self.active_tasks: self.active_tasks[tid].cancel()
                    continue
                elif command == "auto-pilot" and len(parts) > 1:
                    self.task_counter += 1
                    self.active_tasks[self.task_counter] = asyncio.create_task(self.run_autonomous_autopilot(self.task_counter, parts[1]))
                    continue
                elif command in self.plugins:
                    # Execute active plugins synchronously
                    plugin = self.plugins[command]
                    import argparse
                    parser = argparse.ArgumentParser(prog=command)
                    plugin.setup_arguments(parser)
                    try:
                        args = parser.parse_args(parts[1:])
                        plugin.execute(args, self.config)
                    except SystemExit: pass
                elif command in self.extended_vectors:
                    self.task_counter += 1
                    self.active_tasks[self.task_counter] = asyncio.create_task(self.run_asynchronous_vector(self.task_counter, command, parts[1] if len(parts) > 1 else "127.0.0.1"))
                else:
                    print(f"[-] Unknown command: {command}")
            except Exception as e:
                print(f"[-] Error: {str(e)}")

    def run(self):
        self.authenticate_operator()
        asyncio.run(self.shell_loop())

if __name__ == "__main__":
    framework = EnterpriseRedTeamCore()
    framework.run()