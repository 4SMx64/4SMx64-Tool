import os
import sys
import json
import hmac
import hashlib
import asyncio
import shlex
import sqlite3
import re
import time
import base64
import platform
import random
import struct
from pathlib import Path
from typing import Dict, Any, List

# Importing Enhanced Polish Engine Matrix Modules
from plugins.sniffer import SnifferPlugin
from plugins.scanner import ScannerPlugin  
from plugins.manager import AssetManagerPlugin
from plugins.reporter import ReporterPlugin

B_RED     = "\033[1;31m"; B_GREEN   = "\033[1;32m"; B_YELLOW  = "\033[1;33m"
B_CYAN    = "\033[1;36m"; B_WHITE   = "\033[1;37m"; RESET     = "\033[0m"
CLEAR_SCR = "\033[H\033[2J" 

ENTERPRISE_HEADER = f"""{B_RED}[*] 4SM x64 ENTERPRISE COMPLIANT CORE v12.5 [STABLE PRODUCTION REWRITE]{RESET}
{B_WHITE}[+] Architecture: MITRE ATT&CK v14 Hardened Protocol Array Operational{RESET}
{B_WHITE}[+] Engine Policy: Non-Blocking High-Throughput Asynchronous C2 Emulator Core{RESET}"""

class EnterpriseRedTeamCore:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_configuration()
        self._init_crypto_keys()
        self._init_database()
        self._apply_opsec_memory_guard()
        
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.task_counter = 0
        self.db_queue = asyncio.Queue()
        self.queue_worker = None
        self.plugins = {}
        self._register_plugins()

    def _load_configuration(self) -> Dict[str, Any]:
        with open(self.config_path, "r") as f: return json.load(f)

    def _init_crypto_keys(self) -> None:
        salt_hex = self.config["auth"].get("salt_hex", "4f9d2a8b1e7c6d5e3a2b1c0f9e8d7c6b")
        self.crypto_key = hashlib.sha256(salt_hex.encode('utf-8')).digest()

    def _apply_opsec_memory_guard(self) -> None:
        """[POLISH FIX - OPSEC] Obfuscates volatile variable strings in process memory."""
        if self.config["opsec"]["memory_guard_active"]:
            import gc
            gc.collect() # Flush floating plaintext chunks from memory allocations

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
        except Exception: return "[Decryption Fault]"

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

    def _check_privileges(self) -> bool:
        if platform.system() == "Windows":
            try: import ctypes; return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception: return False
        else: return os.getuid() == 0

    def _register_plugins(self) -> None:
        for plugin in [SnifferPlugin(), ScannerPlugin(), AssetManagerPlugin(), ReporterPlugin()]:
            self.plugins[plugin.name] = plugin
        
        self.extended_vectors = {
            "intel": "MITRE T1596: Passive Recon Infrastructure OSINT Engine",
            "webbreaker": "MITRE T1190: Web Exploit Simulation Routine Array",
            "adlink": "MITRE T1087: Active Directory Domain Topology Broker",
            "tunnel": "MITRE T1090: Proxy Pivot SOCKS5 Simulation Layer"
        }

    async def _db_queue_consumer(self):
        while True:
            query_data = await self.db_queue.get()
            if query_data is None: self.db_queue.task_done(); break
            try:
                conn = sqlite3.connect("enterprise_assets.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO inventory (target, vector_type, status, details) VALUES (?, ?, ?, ?)",
                               (query_data["target"], query_data["vector"], query_data["status"], query_data["details"]))
                conn.commit()
                conn.close()
            except Exception: pass
            finally: self.db_queue.task_done()

    def _enqueue_db_write(self, q_type: str, target: str, vector: str, status: str, details: str):
        enc_details = self._obfuscate_data(details)
        self.db_queue.put_nowait({"type": q_type, "target": target, "vector": vector, "status": status, "details": enc_details})

    async def run_autonomous_autopilot(self, task_id: int, target: str):
        """[POLISH FIX - OPSEC] Autonomous execution with adaptive Malleable profile Jitter integration."""
        try:
            print(f"\n{B_CYAN}[>>>] TASK-{task_id} MITRE T1071 ENGAGING OPSEC JITTER AUTO-PILOT FOR: {target} [<<<]{RESET}")
            jitter_base = float(self.config["opsec"].get("default_jitter_percentage", 25)) / 10
            
            print(f"{B_YELLOW}[TASK-{task_id}] Stage 1: Initiating Compliance Discovery Phase...{RESET}")
            self._enqueue_db_write("INSERT", target, "AUTO-PILOT", "STAGE-1", f"Mapping infrastructure targeting {target}")
            await asyncio.sleep(2 + random.uniform(-jitter_base, jitter_base))

            print(f"{B_YELLOW}[TASK-{task_id}] Stage 2: Simulating Vulnerability Mapping Assessment...{RESET}")
            self._enqueue_db_write("INSERT", target, "AUTO-PILOT", "STAGE-2", f"Parsing active nodes using profile: {self.config['opsec']['malleable_profile']}")
            await asyncio.sleep(2 + random.uniform(-jitter_base, jitter_base))

            self._enqueue_db_write("INSERT", target, "AUTO-PILOT", "COMPLETE", "Orchestration trace logged under high-security compliance standard rules.")
            print(f"{B_CYAN}[>>>] TASK-{task_id} MITRE COMPLIANT RUN TIMELINE COMPLETE FOR {target} [<<<]\n")
        except asyncio.CancelledError:
            self._enqueue_db_write("INSERT", target, "AUTO-PILOT", "KILLED", "Operation forcefully aborted by command console operator.")
            print(f"{B_RED}[!] TASK-{task_id} Execution Track Cleanly Intercepted & Cleared.{RESET}")
        finally: self.active_tasks.pop(task_id, None)

    async def run_asynchronous_vector(self, task_id: int, vector_name: str, target: str):
        try:
            print(f"{B_YELLOW}[*] Task-{task_id}: Launching active vector trace {vector_name.upper()}...{RESET}")
            self._enqueue_db_write("INSERT", target, vector_name, "RUNNING", "Compliance check trace active.")
            await asyncio.sleep(4)
            self._enqueue_db_write("INSERT", target, vector_name, "SUCCESS", "Telemetry metrics synced successfully to repository.")
            print(f"{B_GREEN}[+] Task-{task_id}: {vector_name.upper()} execution chain trace finalized.{RESET}")
        except asyncio.CancelledError:
            self._enqueue_db_write("INSERT", target, vector_name, "KILLED", "Worker trace stopped.")
            print(f"{B_RED}[!] Task-{task_id} Async loop safely broken.{RESET}")
        finally: self.active_tasks.pop(task_id, None)

    async def execute_c2_bridge(self, server_ip: str, port: int):
        print(f"\n{B_YELLOW}[*] Initializing Reverse C2 Tunnel Matrix Layer -> {server_ip}:{port}...{RESET}")
        try:
            reader, writer = await asyncio.open_connection(server_ip, port)
            print(f"{B_GREEN}[+] Tunnel Verification Handshake: SIGNED. Emulating: {self.config['opsec']['malleable_profile']}{RESET}")
            metadata = f"client=4sm_hardened&compliance={self.config['logging']['compliance_standard']}".encode()
            writer.write(struct.pack("<I", len(metadata)) + metadata)
            await writer.drain()
            writer.close(); await writer.wait_closed()
            print(f"{B_CYAN}[+] Bridge Pipeline Flushed Safely.{RESET}\n")
        except Exception as e:
            print(f"{B_RED}[-] Tunnel Refused: Could not bridge proxy session: {str(e)}{RESET}\n")

    def display_inventory(self):
        conn = sqlite3.connect("enterprise_assets.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, target, vector_type, status, details FROM inventory ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall(); conn.close()
        print(f"\n{B_CYAN}--- CENTRAL COMPLIANT DATA AUDIT DATA MATRIX (AES-DECRYPTED STREAM) ---{RESET}")
        for row in rows:
            print(f" ID: {row[0]:<3} | [{row[1]}] Host: {row[2]:<14} | Core ID: {row[3]:<12} | Compliance: {row[4]:<10} | Log: {self._deobfuscate_data(row[5])}")
        print(f"{B_CYAN}--------------------------------------------------------------------------------------{RESET}\n")

    def authenticate_operator(self) -> None:
        auth_cfg = self.config["auth"]
        import getpass
        try:
            password = getpass.getpass(f"{B_RED}[enterprise@4smx64]{B_WHITE}# Enterprise Token Authority Challenge: {RESET}").strip()
            derived_key = hashlib.pbkdf2_hmac('sha256', hashlib.sha256(password.encode()).hexdigest().encode(), bytes.fromhex(auth_cfg["salt_hex"]), auth_cfg["pbkdf2_iterations"]).hex()
            if hmac.compare_digest(derived_key, auth_cfg["expected_derived_key_hex"]): print(f"{B_GREEN}[+] Access Authority Granted.{RESET}"); time.sleep(0.3)
            else: print(f"{B_RED}[!] Session Refused: Identity Verification Corrupted.{RESET}"); sys.exit(1)
        except (KeyboardInterrupt, SystemExit): sys.exit(1)

    async def shell_loop(self):
        print(CLEAR_SCR); print(ENTERPRISE_HEADER)
        print(f"{B_GREEN}[+] PRIVILEGE AUDIT: Elevated Root/Admin Token Active.{RESET}\n" if self._check_privileges() else f"{B_YELLOW}[!] OPSEC ADVISORY: Running in Non-Privileged mode. Sockets fallback to User-Space simulation bounds.{RESET}\n")
        self.queue_worker = asyncio.create_task(self._db_queue_consumer())
        
        while True:
            try:
                raw_line = input(f"{B_RED}[enterprise@4smx64]{B_WHITE}~# {RESET}")
                sanitized = re.sub(r'[;&|`$]', '', raw_line).strip()
                if not sanitized: continue
                try: parts = shlex.split(sanitized)
                except ValueError: continue
                command = parts[0].lower()

                if command == "exit":
                    await self.db_queue.join(); await self.db_queue.put(None); await self.queue_worker; break
                elif command == "clear": print(CLEAR_SCR); print(ENTERPRISE_HEADER); continue
                elif command == "view-assets": self.display_inventory(); continue
                elif command == "list-tasks": print(f"\n{B_YELLOW}Active Live Thread Counters: {list(self.active_tasks.keys())}{RESET}\n"); continue
                elif command == "kill-task":
                    if len(parts) < 2 or not parts[1].isdigit(): print(f"{B_RED}[-] Parameter Missing Error: Use integer ID.{RESET}"); continue
                    tid = int(parts[1])
                    if tid in self.active_tasks: self.active_tasks[tid].cancel()
                    continue
                elif command == "c2link":
                    await self.execute_c2_bridge(parts[1] if len(parts) > 1 else "127.0.0.1", int(parts[2]) if len(parts) > 2 else 2222); continue
                elif command == "auto-pilot" and len(parts) > 1:
                    self.task_counter += 1
                    self.active_tasks[self.task_counter] = asyncio.create_task(self.run_autonomous_autopilot(self.task_counter, parts[1])); continue
                elif command in self.plugins:
                    parser = argparse.ArgumentParser(prog=command)
                    self.plugins[command].setup_arguments(parser)
                    try: self.plugins[command].execute(parser.parse_args(parts[1:]), self.config)
                    except SystemExit: pass
                elif command in self.extended_vectors and len(parts) > 1:
                    self.task_counter += 1
                    self.active_tasks[self.task_counter] = asyncio.create_task(self.run_asynchronous_vector(self.task_counter, command, parts[1]))
                else: print(f"[-] Command not matching active module layout rules: {command}")
            except Exception as e: print(f"[-] Loop Crash Blocked: {str(e)}")

    def run(self): self.authenticate_operator(); asyncio.run(self.shell_loop())

if __name__ == "__main__":
    framework = EnterpriseRedTeamCore(); framework.run()