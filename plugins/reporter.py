import argparse
import sqlite3
from typing import Dict, Any
from plugins.base_plugin import BasePlugin

class ReporterPlugin(BasePlugin):
    @property
    def name(self) -> str: return "reporter"
    @property
    def description(self) -> str: return "4SM-Reporter: Automated Executive Summary Generator"

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-o", "--output", default="summary.md", help="Output file name")

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        try:
            conn = sqlite3.connect("enterprise_assets.db")
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, target, vector_type, status FROM inventory")
            rows = cursor.fetchall()
            conn.close()

            with open(args.output, "w") as md:
                md.write("# 4SM x64 ENTERPRISE REPORT\n\n")
                md.write("| Timestamp | Target Matrix | Vector Type | Status |\n")
                md.write("|---|---|---|---|\n")
                for row in rows:
                    md.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
            print(f"[+] Professional summary compiled to '{args.output}' successfully.")
            return 0
        except Exception as e:
            print(f"[-] Reporter failed: {str(e)}")
            return 1