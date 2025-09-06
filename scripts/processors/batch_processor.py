"""
Batch processing logic for multiple files.

Handles processing of multiple files with statistics tracking,
progress reporting, and error handling.
"""

from pathlib import Path
from typing import Dict, List, Set
from .file_processor import FileProcessor
from vault_manager import VaultManager


class BatchProcessor:
    """Handles batch processing of multiple files."""

    def __init__(self, config, vault_manager: VaultManager):
        """
        Initialize the batch processor.

        Args:
            config: VaultConfig instance
            vault_manager: VaultManager instance
        """
        self.config = config
        self.vault_manager = vault_manager
        self.file_processor = FileProcessor(config, vault_manager)
        
        # Supported file extensions for conversion
        self.supported_extensions = {'.txt', '.rtf', '.docx', '.md'}

    def get_files_to_process(self, staging_dir: Path) -> List[Path]:
        """
        Get list of files to process from staging directory.

        Args:
            staging_dir: Root staging directory

        Returns:
            List of file paths to process
        """
        files = []
        for file_path in staging_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                files.append(file_path)
        return files

    def process_files(self, staging_dir: Path, delete_originals: bool = False) -> Dict[str, int]:
        """
        Process all files in the staging directory.

        Args:
            staging_dir: Path to staging directory
            delete_originals: Whether to delete original files after processing

        Returns:
            Dictionary with processing statistics
        """
        stats = {
            'processed': 0,
            'converted': 0,
            'created': 0,
            'errors': 0
        }

        staging_path = Path(staging_dir)
        if not staging_path.exists():
            print(f"❌ Staging directory not found: {staging_path}")
            return stats

        print(f"🔄 Processing files in: {staging_path}")
        print("=" * 60)

        # Get files to process
        files_to_process = self.get_files_to_process(staging_path)

        # Process all files
        for file_path in files_to_process:
            # Show relative path for better context
            try:
                rel_path = file_path.relative_to(staging_path)
                print(f"\n📄 Processing: {rel_path}")
            except ValueError:
                print(f"\n📄 Processing: {file_path.name}")

            # Track if file was converted
            was_converted = file_path.suffix.lower() in ['.txt', '.rtf', '.docx']

            if self.file_processor.process_file(str(file_path), staging_path, delete_originals):
                stats['processed'] += 1
                if was_converted:
                    stats['converted'] += 1
                stats['created'] += 1
            else:
                stats['errors'] += 1

        print("\n" + "=" * 60)
        print("📊 Processing Summary:")
        print(f"  • Files processed: {stats['processed']}")
        print(f"  • Files converted: {stats['converted']}")
        print(f"  • Notes created: {stats['created']}")
        print(f"  • Errors: {stats['errors']}")

        return stats

    def dry_run(self, staging_dir: Path) -> Dict[str, int]:
        """
        Perform a dry run to show what would be processed.

        Args:
            staging_dir: Path to staging directory

        Returns:
            Dictionary with file counts
        """
        staging_path = Path(staging_dir)
        if not staging_path.exists():
            print(f"❌ Staging directory not found: {staging_path}")
            return {'total': 0, 'convertible': 0, 'markdown': 0}

        print("🔍 DRY RUN MODE - No changes will be made")
        print("=" * 60)

        files_to_process = self.get_files_to_process(staging_path)
        
        convertible_count = 0
        markdown_count = 0
        
        for file_path in files_to_process:
            print(f"📄 Would process: {file_path.name}")
            if file_path.suffix.lower() in ['.txt', '.rtf', '.docx']:
                convertible_count += 1
            elif file_path.suffix.lower() == '.md':
                markdown_count += 1

        stats = {
            'total': len(files_to_process),
            'convertible': convertible_count,
            'markdown': markdown_count
        }

        print(f"\n📊 Would process {stats['total']} files:")
        print(f"  • Convertible files: {stats['convertible']}")
        print(f"  • Markdown files: {stats['markdown']}")

        return stats
