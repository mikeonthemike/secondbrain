"""
Core vault management for Obsidian Second Brain system.

Handles note creation, organization, and basic vault operations.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import yaml

try:
    from .config_manager import VaultConfig
except ImportError:
    from config_manager import VaultConfig


class VaultManager:
    """Manages Obsidian vault operations and note management."""
    
    def __init__(self, config: Optional[VaultConfig] = None):
        """
        Initialize vault manager.
        
        Args:
            config: VaultConfig instance. If None, creates a new one.
        """
        self.config = config or VaultConfig()
        self.vault_path = self.config.get_vault_path()
        
        if not self.vault_path:
            raise ValueError("No vault path configured. Run setup first.")
    
    def create_note(self, 
                   title: str, 
                   content: str = "", 
                   folder_type: str = "inbox",
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   template: Optional[str] = None) -> Optional[str]:
        """
        Create a new note in the vault.
        
        Args:
            title: Note title
            content: Note content
            folder_type: Type of folder (inbox, projects, areas, resources, archive)
            tags: List of tags to add
            metadata: Additional metadata for frontmatter
            template: Template to use for the note
            
        Returns:
            Path to created note, or None if failed
        """
        try:
            # Get folder path
            folder_path = self.config.get_folder_path(folder_type)
            if not folder_path:
                print(f"Invalid folder type: {folder_type}")
                return None
            
            # Create filename from title
            filename = self._title_to_filename(title)
            file_path = os.path.join(folder_path, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                print(f"Note already exists: {file_path}")
                return file_path
            
            # Prepare content
            if template:
                content = self._apply_template(template, title, content, tags, metadata)
            else:
                content = self._format_note_content(title, content, tags, metadata)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Created note: {filename}")
            return file_path
            
        except Exception as e:
            print(f"✗ Error creating note: {e}")
            return None
    
    def _title_to_filename(self, title: str) -> str:
        """Convert title to valid filename."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with hyphens
        filename = re.sub(r'\s+', '-', filename)
        # Remove multiple hyphens
        filename = re.sub(r'-+', '-', filename)
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        # Add .md extension
        return f"{filename}.md"
    
    def _format_note_content(self, 
                           title: str, 
                           content: str, 
                           tags: Optional[List[str]] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format note content with frontmatter."""
        # Prepare frontmatter
        frontmatter = {
            "title": title,
            "created": datetime.now().isoformat(),
            "status": "active"
        }
        
        if tags:
            frontmatter["tags"] = tags
        
        if metadata:
            frontmatter.update(metadata)
        
        # Format as YAML
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        
        # Combine frontmatter and content
        return f"---\n{yaml_content}---\n\n{content}\n"
    
    def _apply_template(self, 
                       template_name: str, 
                       title: str, 
                       content: str,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Apply template to note content."""
        template_path = self.config.get_template_path(template_name)
        if not template_path:
            print(f"Template not found: {template_name}")
            return self._format_note_content(title, content, tags, metadata)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace template variables
            template_content = template_content.replace("{{title}}", title)
            template_content = template_content.replace("{{content}}", content)
            template_content = template_content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            template_content = template_content.replace("{{time}}", datetime.now().strftime("%H:%M"))
            
            if tags:
                tags_str = " ".join([f"#{tag}" for tag in tags])
                template_content = template_content.replace("{{tags}}", tags_str)
            
            return template_content
            
        except Exception as e:
            print(f"Error applying template: {e}")
            return self._format_note_content(title, content, tags, metadata)
    
    def get_note(self, note_path: str) -> Optional[Dict[str, Any]]:
        """
        Read and parse a note file.
        
        Args:
            note_path: Path to the note file
            
        Returns:
            Dictionary with note data, or None if failed
        """
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            frontmatter, body = self._parse_frontmatter(content)
            
            return {
                "path": note_path,
                "frontmatter": frontmatter,
                "content": body,
                "title": frontmatter.get("title", os.path.basename(note_path))
            }
            
        except Exception as e:
            print(f"Error reading note: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from note content."""
        if not content.startswith("---\n"):
            return {}, content
        
        try:
            # Find end of frontmatter
            end_marker = content.find("\n---\n", 4)
            if end_marker == -1:
                return {}, content
            
            frontmatter_yaml = content[4:end_marker]
            body = content[end_marker + 5:]
            
            frontmatter = yaml.safe_load(frontmatter_yaml) or {}
            return frontmatter, body
            
        except Exception as e:
            print(f"Error parsing frontmatter: {e}")
            return {}, content
    
    def update_note(self, note_path: str, updates: Dict[str, Any]) -> bool:
        """
        Update a note with new content or metadata.
        
        Args:
            note_path: Path to the note file
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            note_data = self.get_note(note_path)
            if not note_data:
                return False
            
            # Update frontmatter
            if "frontmatter" in updates:
                note_data["frontmatter"].update(updates["frontmatter"])
            
            # Update content
            if "content" in updates:
                note_data["content"] = updates["content"]
            
            # Update metadata
            note_data["frontmatter"]["updated"] = datetime.now().isoformat()
            
            # Write back to file
            new_content = self._format_note_content(
                note_data["frontmatter"].get("title", ""),
                note_data["content"],
                note_data["frontmatter"].get("tags"),
                note_data["frontmatter"]
            )
            
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Updated note: {os.path.basename(note_path)}")
            return True
            
        except Exception as e:
            print(f"✗ Error updating note: {e}")
            return False
    
    def move_note(self, note_path: str, new_folder_type: str) -> bool:
        """
        Move a note to a different folder.
        
        Args:
            note_path: Current path to the note
            new_folder_type: Type of folder to move to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_folder_path = self.config.get_folder_path(new_folder_type)
            if not new_folder_path:
                print(f"Invalid folder type: {new_folder_type}")
                return False
            
            filename = os.path.basename(note_path)
            new_path = os.path.join(new_folder_path, filename)
            
            # Check if target file already exists
            if os.path.exists(new_path):
                print(f"Target file already exists: {new_path}")
                return False
            
            # Move file
            os.rename(note_path, new_path)
            print(f"✓ Moved note to: {new_folder_type}")
            return True
            
        except Exception as e:
            print(f"✗ Error moving note: {e}")
            return False
    
    def list_notes(self, folder_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List notes in the vault.
        
        Args:
            folder_type: Filter by folder type
            tags: Filter by tags
            
        Returns:
            List of note dictionaries
        """
        notes = []
        
        if folder_type:
            folder_path = self.config.get_folder_path(folder_type)
            if not folder_path:
                return notes
            search_paths = [folder_path]
        else:
            # Search all PARA folders
            search_paths = []
            for folder_name in self.config.config["para_structure"].values():
                folder_path = os.path.join(self.vault_path, folder_name)
                if os.path.exists(folder_path):
                    search_paths.append(folder_path)
        
        for search_path in search_paths:
            for filename in os.listdir(search_path):
                if filename.endswith('.md'):
                    note_path = os.path.join(search_path, filename)
                    note_data = self.get_note(note_path)
                    if note_data:
                        # Filter by tags if specified
                        if tags:
                            note_tags = note_data["frontmatter"].get("tags", [])
                            if not any(tag in note_tags for tag in tags):
                                continue
                        
                        notes.append(note_data)
        
        return notes
    
    def create_daily_note(self, date: Optional[datetime] = None) -> Optional[str]:
        """
        Create a daily note for the specified date.
        
        Args:
            date: Date for the note. If None, uses today.
            
        Returns:
            Path to created note, or None if failed
        """
        if not date:
            date = datetime.now()
        
        title = date.strftime("%Y-%m-%d")
        content = f"# {date.strftime('%A, %B %d, %Y')}\n\n## Notes\n\n## Tasks\n\n## Reflections\n"
        
        return self.create_note(
            title=title,
            content=content,
            folder_type="inbox",  # Will be moved to daily notes folder
            template="daily_note_template.md"
        )
    
    def create_moc(self, topic: str, notes: List[str]) -> Optional[str]:
        """
        Create a Map of Content (MOC) for a topic.
        
        Args:
            topic: Topic name
            notes: List of note titles to include
            
        Returns:
            Path to created MOC, or None if failed
        """
        content = f"# {topic} - Map of Content\n\n"
        
        for note in notes:
            content += f"- [[{note}]]\n"
        
        content += "\n## Related Topics\n\n"
        content += "- \n"
        
        return self.create_note(
            title=f"{topic} - MOC",
            content=content,
            folder_type="mocs",
            tags=["moc", topic.lower()]
        )


def main():
    """Command-line interface for vault management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Obsidian Second Brain Vault Manager")
    parser.add_argument("--create-note", help="Create a new note")
    parser.add_argument("--folder", default="inbox", help="Folder type for new note")
    parser.add_argument("--list", action="store_true", help="List notes")
    parser.add_argument("--daily-note", action="store_true", help="Create daily note")
    
    args = parser.parse_args()
    
    try:
        manager = VaultManager()
        
        if args.create_note:
            manager.create_note(args.create_note, folder_type=args.folder)
        elif args.list:
            notes = manager.list_notes()
            for note in notes:
                print(f"- {note['title']} ({note['path']})")
        elif args.daily_note:
            manager.create_daily_note()
        else:
            print("Use --help for available options")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Run setup first to configure vault path.")


if __name__ == "__main__":
    main()
