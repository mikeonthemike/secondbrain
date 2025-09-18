"""
Obsidian Second Brain - Local-First Knowledge Management System

This module provides a high-level interface for managing your Obsidian-based
Second Brain system using the PARA methodology (Projects, Areas, Resources, Archive).
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add scripts directory to path for imports
scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_path)

try:
    from config_manager import VaultConfig
    from vault_manager import VaultManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)


class SecondBrain:
    """
    Main interface for the Obsidian Second Brain system.
    
    This class provides a high-level API for managing your knowledge base
    using the PARA methodology with Obsidian as the underlying storage.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Second Brain system.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self.config = VaultConfig(config_path)
        self.vault_manager = VaultManager(self.config)
        
        # Validate configuration
        issues = self.config.validate_config()
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            print("Run setup first to configure your vault.")
    
    def create_note(self, 
                   title: str, 
                   content: str = "", 
                   folder_type: str = "inbox",
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   template: Optional[str] = None) -> Optional[str]:
        """
        Create a new note in your Second Brain.
        
        Args:
            title: Note title
            content: Note content
            folder_type: PARA folder type (inbox, projects, areas, resources, archive)
            tags: List of tags to add
            metadata: Additional metadata for frontmatter
            template: Template to use for the note
            
        Returns:
            Path to created note, or None if failed
        """
        return self.vault_manager.create_note(
            title=title,
            content=content,
            folder_type=folder_type,
            tags=tags,
            metadata=metadata,
            template=template
        )
    
    def create_project_note(self, 
                           title: str, 
                           description: str = "",
                           deadline: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Create a project note with project-specific structure.
        
        Args:
            title: Project title
            description: Project description
            deadline: Project deadline (optional)
            tags: Additional tags
            
        Returns:
            Path to created note, or None if failed
        """
        # Add project-specific tags
        project_tags = ["project"]
        if tags:
            project_tags.extend(tags)
        
        # Create project-specific metadata
        metadata = {
            "type": "project",
            "status": "active"
        }
        if deadline:
            metadata["deadline"] = deadline
        
        # Create project content structure
        content = f"# {title}\n\n"
        if description:
            content += f"## Overview\n{description}\n\n"
        content += "## Goals\n- [ ] \n\n"
        content += "## Timeline\n"
        if deadline:
            content += f"- Deadline: {deadline}\n"
        content += "- Start: \n\n"
        content += "## Resources\n- \n\n"
        content += "## Notes\n\n"
        content += "## Next Actions\n- [ ] \n"
        
        return self.create_note(
            title=title,
            content=content,
            folder_type="projects",
            tags=project_tags,
            metadata=metadata,
            template="project_template.md"
        )
    
    def create_area_note(self, 
                        title: str, 
                        description: str = "",
                        tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Create an area note for ongoing responsibilities.
        
        Args:
            title: Area title
            description: Area description
            tags: Additional tags
            
        Returns:
            Path to created note, or None if failed
        """
        area_tags = ["area"]
        if tags:
            area_tags.extend(tags)
        
        metadata = {
            "type": "area",
            "status": "active"
        }
        
        content = f"# {title}\n\n"
        if description:
            content += f"## Overview\n{description}\n\n"
        content += "## Standards\n- \n\n"
        content += "## Current Projects\n- \n\n"
        content += "## Resources\n- \n\n"
        content += "## Notes\n\n"
        
        return self.create_note(
            title=title,
            content=content,
            folder_type="areas",
            tags=area_tags,
            metadata=metadata
        )
    
    def create_resource_note(self, 
                           title: str, 
                           content: str = "",
                           source: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Create a resource note for reference materials.
        
        Args:
            title: Resource title
            content: Resource content
            source: Source of the resource (URL, book, etc.)
            tags: Additional tags
            
        Returns:
            Path to created note, or None if failed
        """
        resource_tags = ["resource"]
        if tags:
            resource_tags.extend(tags)
        
        metadata = {
            "type": "resource",
            "status": "active"
        }
        if source:
            metadata["source"] = source
        
        # Add source information to content if provided
        if source:
            content = f"**Source:** {source}\n\n{content}"
        
        return self.create_note(
            title=title,
            content=content,
            folder_type="resources",
            tags=resource_tags,
            metadata=metadata
        )
    
    def create_daily_note(self, date: Optional[datetime] = None) -> Optional[str]:
        """
        Create a daily note for the specified date.
        
        Args:
            date: Date for the note. If None, uses today.
            
        Returns:
            Path to created note, or None if failed
        """
        return self.vault_manager.create_daily_note(date)
    
    def list_notes(self, 
                  folder_type: Optional[str] = None, 
                  tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List notes in your Second Brain.
        
        Args:
            folder_type: Filter by folder type
            tags: Filter by tags
            
        Returns:
            List of note dictionaries
        """
        return self.vault_manager.list_notes(folder_type, tags)
    
    def get_note(self, note_path: str) -> Optional[Dict[str, Any]]:
        """
        Read and parse a note file.
        
        Args:
            note_path: Path to the note file
            
        Returns:
            Dictionary with note data, or None if failed
        """
        return self.vault_manager.get_note(note_path)
    
    def update_note(self, note_path: str, updates: Dict[str, Any]) -> bool:
        """
        Update a note with new content or metadata.
        
        Args:
            note_path: Path to the note file
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        return self.vault_manager.update_note(note_path, updates)
    
    def move_note(self, note_path: str, new_folder_type: str) -> bool:
        """
        Move a note to a different folder.
        
        Args:
            note_path: Current path to the note
            new_folder_type: Type of folder to move to
            
        Returns:
            True if successful, False otherwise
        """
        return self.vault_manager.move_note(note_path, new_folder_type)
    
    def create_moc(self, topic: str, notes: List[str]) -> Optional[str]:
        """
        Create a Map of Content (MOC) for a topic.
        
        Args:
            topic: Topic name
            notes: List of note titles to include
            
        Returns:
            Path to created MOC, or None if failed
        """
        return self.vault_manager.create_moc(topic, notes)
    
    def get_vault_info(self) -> Dict[str, Any]:
        """
        Get information about the current vault.
        
        Returns:
            Dictionary with vault information
        """
        vault_path = self.config.get_vault_path()
        if not vault_path:
            return {"error": "No vault configured"}
        
        # Count notes in each folder
        folder_counts = {}
        for folder_type in ["inbox", "projects", "areas", "resources", "archive", "mocs"]:
            folder_path = self.config.get_folder_path(folder_type)
            if folder_path and os.path.exists(folder_path):
                md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
                folder_counts[folder_type] = len(md_files)
            else:
                folder_counts[folder_type] = 0
        
        return {
            "vault_path": vault_path,
            "folder_counts": folder_counts,
            "total_notes": sum(folder_counts.values()),
            "config_valid": len(self.config.validate_config()) == 0
        }


def main():
    """Command-line interface for Second Brain management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Obsidian Second Brain Manager")
    parser.add_argument("--create-note", help="Create a new note")
    parser.add_argument("--create-project", help="Create a new project note")
    parser.add_argument("--create-area", help="Create a new area note")
    parser.add_argument("--create-resource", help="Create a new resource note")
    parser.add_argument("--daily-note", action="store_true", help="Create daily note")
    parser.add_argument("--list", action="store_true", help="List notes")
    parser.add_argument("--folder", default="inbox", help="Folder type for new note")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--info", action="store_true", help="Show vault information")
    
    args = parser.parse_args()
    
    try:
        brain = SecondBrain()
        
        if args.create_note:
            tags = args.tags.split(',') if args.tags else None
            note_path = brain.create_note(args.create_note, folder_type=args.folder, tags=tags)
            if note_path:
                print(f"✓ Created note: {note_path}")
            else:
                print("✗ Failed to create note")
        
        elif args.create_project:
            tags = args.tags.split(',') if args.tags else None
            note_path = brain.create_project_note(args.create_project, tags=tags)
            if note_path:
                print(f"✓ Created project: {note_path}")
            else:
                print("✗ Failed to create project")
        
        elif args.create_area:
            tags = args.tags.split(',') if args.tags else None
            note_path = brain.create_area_note(args.create_area, tags=tags)
            if note_path:
                print(f"✓ Created area: {note_path}")
            else:
                print("✗ Failed to create area")
        
        elif args.create_resource:
            tags = args.tags.split(',') if args.tags else None
            note_path = brain.create_resource_note(args.create_resource, tags=tags)
            if note_path:
                print(f"✓ Created resource: {note_path}")
            else:
                print("✗ Failed to create resource")
        
        elif args.daily_note:
            note_path = brain.create_daily_note()
            if note_path:
                print(f"✓ Created daily note: {note_path}")
            else:
                print("✗ Failed to create daily note")
        
        elif args.list:
            notes = brain.list_notes()
            print(f"Found {len(notes)} notes:")
            for note in notes:
                print(f"  - {note['title']} ({note['path']})")
        
        elif args.info:
            info = brain.get_vault_info()
            if "error" in info:
                print(f"Error: {info['error']}")
            else:
                print(f"Vault: {info['vault_path']}")
                print(f"Total notes: {info['total_notes']}")
                print("Notes by folder:")
                for folder, count in info['folder_counts'].items():
                    print(f"  {folder}: {count}")
        
        else:
            print("Use --help for available options")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your vault is properly configured.")


if __name__ == "__main__":
    main()