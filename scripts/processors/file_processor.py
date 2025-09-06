"""
Individual file processing logic.

Handles the complete workflow for processing a single file,
including conversion, analysis, organization, and vault integration.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from converters import TextConverter, PandocConverter
from analyzers import ContentAnalyzer, TitleExtractor
from organizers import FolderManager, TagExtractor
from vault_manager import VaultManager


class FileProcessor:
    """Processes individual files for conversion and organization."""

    def __init__(self, config, vault_manager: VaultManager):
        """
        Initialize the file processor.

        Args:
            config: VaultConfig instance
            vault_manager: VaultManager instance for note creation
        """
        self.config = config
        self.vault_manager = vault_manager
        
        # Initialize components
        self.text_converter = TextConverter()
        self.pandoc_converter = PandocConverter()
        self.content_analyzer = ContentAnalyzer()
        self.title_extractor = TitleExtractor()
        self.folder_manager = FolderManager(config)
        self.tag_extractor = TagExtractor()

    def _get_converter(self, file_path: str):
        """
        Get the appropriate converter for a file.

        Args:
            file_path: Path to the file

        Returns:
            Converter instance or None if no converter available
        """
        if self.text_converter.can_convert(file_path):
            return self.text_converter
        elif self.pandoc_converter.can_convert(file_path):
            return self.pandoc_converter
        return None

    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content with proper encoding handling.

        Args:
            file_path: Path to the file

        Returns:
            File content or None if reading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except UnicodeDecodeError:
                print(f"❌ Could not read file {file_path.name} - unsupported encoding")
                return None

    def process_file(self, file_path: str, staging_dir: Path, delete_original: bool = False) -> bool:
        """
        Process a single file for conversion and organization.

        Args:
            file_path: Path to the file to process
            staging_dir: Root staging directory
            delete_original: Whether to delete original files after successful processing

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return False

            original_file_path = file_path
            converted_file_path = None

            # Check if file needs conversion
            converter = self._get_converter(str(file_path))
            if converter:
                print(f"➡️ Converting {file_path.name}")
                md_path = converter.convert(str(file_path))
                if not md_path:
                    print(f"❌ Failed to convert {file_path.name}")
                    return False

                converted_file_path = Path(md_path)
                file_path = converted_file_path  # Use converted file for processing

            # Skip if not a markdown file
            if file_path.suffix.lower() != '.md':
                print(f"⏭️ Skipping non-markdown file: {file_path.name}")
                return False

            # Read file content
            content = self._read_file_content(file_path)
            if not content:
                return False

            # Skip empty files
            if not content.strip():
                print(f"⏭️ Skipping empty file: {file_path.name}")
                return False

            # Extract title and detect content type
            title = self.title_extractor.extract_title_from_content(content, file_path.name)
            content_type = self.content_analyzer.detect_content_type(str(file_path), content)
            folder_type = self.content_analyzer.determine_folder_type(content_type, file_path.name)

            # Extract folder tags from the file path
            folder_tags = self.tag_extractor.extract_folder_tags(file_path, staging_dir)

            # Get file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            # Prepare metadata
            metadata = {
                'created': mtime.isoformat(),
                'status': 'active',
                'source_file': str(original_file_path),  # Keep reference to original
                'source_folders': folder_tags
            }

            # Determine tags based on content type and folder structure
            tags = self.tag_extractor.combine_tags(content_type, folder_tags)

            # Create the target folder structure
            target_folder = self.folder_manager.create_subfolder_structure(file_path, staging_dir, folder_type)
            if not target_folder:
                print(f"❌ Could not determine target folder for {file_path.name}")
                return False

            # Create the note directly in the target folder
            filename = self.vault_manager._title_to_filename(title)
            note_path = os.path.join(target_folder, filename)
            
            # Check if file already exists
            if os.path.exists(note_path):
                print(f"⚠️ Note already exists: {filename}")
                # Still consider this successful, but don't delete original
                return True

            # Format note content with frontmatter
            note_content = self.vault_manager._format_note_content(
                title, content, tags, metadata
            )

            # Write the note
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note_content)

            print(f"✅ Created note: {title} → {folder_type}/{'/'.join(folder_tags) if folder_tags else 'root'}")

            # Move daily notes to daily notes folder
            if content_type == 'daily':
                daily_folder = self.folder_manager.create_daily_notes_folder()
                if daily_folder:
                    daily_path = os.path.join(daily_folder, os.path.basename(note_path))
                    if not os.path.exists(daily_path):
                        os.rename(note_path, daily_path)
                        print(f"📅 Moved daily note to: {daily_folder}")

            # Only delete original files AFTER successful vault storage
            if delete_original and original_file_path != file_path:
                try:
                    original_file_path.unlink()
                    print(f"🗑️ Removed original file: {original_file_path.name}")
                except OSError as e:
                    print(f"⚠️ Could not remove original file {original_file_path.name}: {e}")

            # Clean up converted file if it's different from original
            if converted_file_path and converted_file_path != original_file_path:
                try:
                    converted_file_path.unlink()
                    print(f"🗑️ Cleaned up converted file: {converted_file_path.name}")
                except OSError as e:
                    print(f"⚠️ Could not clean up converted file {converted_file_path.name}: {e}")

            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
