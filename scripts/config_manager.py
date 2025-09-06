"""
Configuration management for Obsidian Second Brain system.

Handles vault path configuration, environment variables, and user preferences.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import getpass


class VaultConfig:
    """Manages configuration for the Obsidian Second Brain system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. Defaults to 'config/vault_config.json'
        """
        self.config_path = config_path or "config/vault_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration.")
        
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration structure."""
        return {
            "vault_path": None,
            "obsidian_config": {
                "daily_notes_folder": "06-Daily-Notes",
                "templates_folder": "05-Templates",
                "attachment_folder": "99-Attachments",
                "inbox_folder": "00-Inbox"
            },
            "para_structure": {
                "inbox": "00-Inbox",
                "projects": "01-Projects",
                "areas": "02-Areas",
                "resources": "03-Resources",
                "archive": "04-Archive",
                "mocs": "07-MOCs"
            },
            "automation": {
                "auto_backup": True,
                "backup_location": None,
                "email_import": {
                    "enabled": False,
                    "inbox_label": "To Process"
                },
                "daily_notes": {
                    "enabled": True,
                    "template": "daily_note_template.md"
                }
            },
            "metadata": {
                "created": None,
                "last_updated": None,
                "version": "1.0.0"
            }
        }
    
    def get_vault_path(self) -> Optional[str]:
        """
        Get vault path from config, env var, or prompt user.
        
        Returns:
            Path to Obsidian vault, or None if not found/configured
        """
        # Check environment variable first
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        if vault_path and self._validate_vault_path(vault_path):
            return vault_path
        
        # Check config file
        vault_path = self.config.get("vault_path")
        if vault_path and self._validate_vault_path(vault_path):
            return vault_path
        
        # Prompt user for vault path
        return self._prompt_vault_path()
    
    def _validate_vault_path(self, path: str) -> bool:
        """Validate that path exists and is an Obsidian vault."""
        if not os.path.exists(path):
            return False
        
        # Check if it looks like an Obsidian vault
        return self.is_obsidian_vault(path)
    
    def is_obsidian_vault(self, path: str) -> bool:
        """Check if path contains .obsidian folder."""
        obsidian_path = os.path.join(path, ".obsidian")
        return os.path.exists(obsidian_path) and os.path.isdir(obsidian_path)
    
    def _prompt_vault_path(self) -> Optional[str]:
        """Interactively prompt user for vault path."""
        print("\n" + "="*60)
        print("OBSIDIAN VAULT CONFIGURATION")
        print("="*60)
        print("No Obsidian vault configured.")
        print("Please provide the path to your Obsidian vault.")
        print("This should be the folder containing your .obsidian directory.")
        print("\nExample: /Users/username/Documents/MyVault")
        print("="*60)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            vault_path = input(f"\nVault path (attempt {attempt + 1}/{max_attempts}): ").strip()
            
            if not vault_path:
                print("Please enter a valid path.")
                continue
            
            # Expand user path and resolve
            vault_path = os.path.expanduser(vault_path)
            vault_path = os.path.abspath(vault_path)
            
            if self._validate_vault_path(vault_path):
                self.config["vault_path"] = vault_path
                self.config["metadata"]["last_updated"] = self._get_current_timestamp()
                self.save_config()
                print(f"✓ Vault configured: {vault_path}")
                return vault_path
            else:
                if not os.path.exists(vault_path):
                    print(f"✗ Path does not exist: {vault_path}")
                elif not self.is_obsidian_vault(vault_path):
                    print(f"✗ Not an Obsidian vault (missing .obsidian folder): {vault_path}")
                else:
                    print(f"✗ Invalid vault path: {vault_path}")
        
        print(f"\n✗ Failed to configure vault after {max_attempts} attempts.")
        print("You can configure it later by running the setup script.")
        return None
    
    def get_folder_path(self, folder_type: str) -> Optional[str]:
        """
        Get the full path for a specific folder type.
        
        Args:
            folder_type: Type of folder (inbox, projects, areas, resources, archive, mocs)
            
        Returns:
            Full path to the folder, or None if not found
        """
        vault_path = self.get_vault_path()
        if not vault_path:
            return None
        
        folder_name = self.config["para_structure"].get(folder_type)
        if not folder_name:
            return None
        
        folder_path = os.path.join(vault_path, folder_name)
        return folder_path if os.path.exists(folder_path) else None
    
    def get_template_path(self, template_name: str) -> Optional[str]:
        """
        Get the full path to a template file.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Full path to the template, or None if not found
        """
        vault_path = self.get_vault_path()
        if not vault_path:
            return None
        
        templates_folder = self.config["obsidian_config"]["templates_folder"]
        template_path = os.path.join(vault_path, templates_folder, template_name)
        return template_path if os.path.exists(template_path) else None
    
    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        self._deep_update(self.config, updates)
        self.config["metadata"]["last_updated"] = self._get_current_timestamp()
        self.save_config()
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_config(self) -> List[str]:
        """
        Validate current configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check vault path
        vault_path = self.config.get("vault_path")
        if not vault_path:
            issues.append("No vault path configured")
        elif not self._validate_vault_path(vault_path):
            issues.append(f"Invalid vault path: {vault_path}")
        
        # Check folder structure
        if vault_path and self._validate_vault_path(vault_path):
            for folder_type, folder_name in self.config["para_structure"].items():
                folder_path = os.path.join(vault_path, folder_name)
                if not os.path.exists(folder_path):
                    issues.append(f"Missing folder: {folder_name}")
        
        return issues
    
    def setup_vault_structure(self) -> bool:
        """
        Create the basic vault folder structure if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        vault_path = self.get_vault_path()
        if not vault_path:
            print("No vault path configured. Run setup first.")
            return False
        
        try:
            # Create PARA folders
            for folder_name in self.config["para_structure"].values():
                folder_path = os.path.join(vault_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                print(f"✓ Created folder: {folder_name}")
            
            # Create Obsidian-specific folders
            for folder_name in self.config["obsidian_config"].values():
                if folder_name not in self.config["para_structure"].values():
                    folder_path = os.path.join(vault_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    print(f"✓ Created folder: {folder_name}")
            
            print(f"\n✓ Vault structure created successfully in: {vault_path}")
            return True
            
        except OSError as e:
            print(f"✗ Error creating vault structure: {e}")
            return False


def main():
    """Command-line interface for configuration management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Obsidian Second Brain Configuration Manager")
    parser.add_argument("--vault-path", help="Set vault path")
    parser.add_argument("--validate", action="store_true", help="Validate current configuration")
    parser.add_argument("--setup", action="store_true", help="Setup vault structure")
    
    args = parser.parse_args()
    
    config = VaultConfig()
    
    if args.vault_path:
        config.update_config({"vault_path": args.vault_path})
        print(f"Vault path set to: {args.vault_path}")
    
    if args.validate:
        issues = config.validate_config()
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Configuration is valid.")
    
    if args.setup:
        config.setup_vault_structure()


if __name__ == "__main__":
    main()
