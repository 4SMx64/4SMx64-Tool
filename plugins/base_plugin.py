import abc
import argparse
from typing import Dict, Any

class BasePlugin(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the custom vector name of the plugin."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Returns a short description of the plugin capability."""
        pass

    @abc.abstractmethod
    def setup_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Defines the plugin-specific arguments using command routing."""
        pass

    @abc.abstractmethod
    def execute(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Executes the operational logic within strict exception boundaries."""
        pass