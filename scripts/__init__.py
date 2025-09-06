"""
Obsidian Second Brain - Python Automation Scripts

This package provides automation tools for managing an Obsidian-based Second Brain system.
It implements the Building a Second Brain (BASB) methodology with Python automation.
"""

__version__ = "1.0.0"
__author__ = "Second Brain Team"

try:
    from .config_manager import VaultConfig
    from .vault_manager import VaultManager
except ImportError:
    from config_manager import VaultConfig
    from vault_manager import VaultManager

__all__ = ["VaultConfig", "VaultManager"]
