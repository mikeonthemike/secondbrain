"""
Folder structure management for file organization.

Handles creation of appropriate folder structures in the vault
based on content type and maintains folder hierarchy from staging.
"""

import os
from pathlib import Path
from typing import Optional, List
from config_manager import VaultConfig


class FolderManager:
    """Manages folder structure creation and organization."""

    def __init__(self, config: VaultConfig):
        """
        Initialize the folder manager.

        Args:
            config: VaultConfig instance for folder paths
        """
        self.config = config

    def create_subfolder_structure(self, file_path: Path, staging_dir: Path, vault_folder: str) -> Optional[str]:
        """
        Create equivalent subfolder structure in the vault.
        
        Args:
            file_path: Path to the file
            staging_dir: Root staging directory
            vault_folder: Target vault folder (e.g., 'resources', 'projects')
            
        Returns:
            Path to the target subfolder in vault
        """
        try:
            # Get relative path from staging directory
            rel_path = file_path.relative_to(staging_dir)
            # Get all parent directories (excluding the file itself)
            folder_parts = rel_path.parts[:-1]
            
            if not folder_parts:
                # File is in root of staging directory
                return self.config.get_folder_path(vault_folder)
            
            # Build target path in vault
            vault_path = self.config.get_vault_path()
            if not vault_path:
                return None
                
            target_folder = os.path.join(vault_path, self.config.config["para_structure"][vault_folder])
            
            # Create subfolder structure
            for part in folder_parts:
                target_folder = os.path.join(target_folder, part)
                os.makedirs(target_folder, exist_ok=True)
            
            return target_folder
        except ValueError:
            # File is not relative to staging directory
            return self.config.get_folder_path(vault_folder)

    def ensure_folder_exists(self, folder_path: str) -> bool:
        """
        Ensure a folder exists, creating it if necessary.

        Args:
            folder_path: Path to the folder

        Returns:
            True if folder exists or was created successfully
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True
        except OSError as e:
            print(f"❌ Error creating folder {folder_path}: {e}")
            return False

    def get_vault_folder_path(self, folder_type: str) -> Optional[str]:
        """
        Get the full path for a vault folder type.

        Args:
            folder_type: Type of folder (resources, projects, areas, etc.)

        Returns:
            Full path to the folder, or None if not found
        """
        return self.config.get_folder_path(folder_type)

    def create_daily_notes_folder(self) -> Optional[str]:
        """
        Create and return the daily notes folder path.

        Returns:
            Path to daily notes folder, or None if creation failed
        """
        daily_folder_name = self.config.config["obsidian_config"]["daily_notes_folder"]
        vault_path = self.config.get_vault_path()
        if not vault_path:
            return None
            
        daily_folder = os.path.join(vault_path, daily_folder_name)
        if self.ensure_folder_exists(daily_folder):
            return daily_folder
        return None
