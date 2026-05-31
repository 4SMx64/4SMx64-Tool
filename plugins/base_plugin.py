import argparse
from typing import Dict, Any

class BasePlugin:
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        raise NotImplementedError