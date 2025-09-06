"""
Main bulk converter orchestrator for the Second Brain system.

This is the simplified main entry point that coordinates all the
decomposed modules for file conversion and organization.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add the scripts directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from config_manager import VaultConfig
from vault_manager import VaultManager
from processors import BatchProcessor


class BulkConverter:
    """Main orchestrator for bulk file conversion."""

    def __init__(self, staging_dir: str, vault_config: Optional[VaultConfig] = None):
        """
        Initialize the bulk converter.

        Args:
            staging_dir: Path to directory containing files to convert
            vault_config: VaultConfig instance. If None, creates a new one.
        """
        self.staging_dir = Path(staging_dir)
        self.config = vault_config or VaultConfig()
        self.vault_manager = VaultManager(self.config)
        self.batch_processor = BatchProcessor(self.config, self.vault_manager)

    def process_files(self, delete_originals: bool = False) -> dict:
        """
        Process all files in the staging directory.

        Args:
            delete_originals: Whether to delete original files after processing

        Returns:
            Dictionary with processing statistics
        """
        return self.batch_processor.process_files(self.staging_dir, delete_originals)

    def dry_run(self) -> dict:
        """
        Perform a dry run to show what would be processed.

        Returns:
            Dictionary with file counts
        """
        return self.batch_processor.dry_run(self.staging_dir)


def main():
    """Command-line interface for bulk file conversion."""
    parser = argparse.ArgumentParser(
        description="Bulk file conversion for Obsidian Second Brain system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bulk_converter.py /path/to/staging
  python bulk_converter.py /path/to/staging --dry-run
  python bulk_converter.py /path/to/staging --delete-originals
        """
    )

    parser.add_argument(
        'staging_dir',
        help='Path to directory containing files to convert'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without making changes'
    )

    parser.add_argument(
        '--delete-originals',
        action='store_true',
        help='Delete original files after successful conversion (DESTRUCTIVE - use with caution)'
    )

    parser.add_argument(
        '--vault-path',
        help='Override vault path from configuration'
    )

    args = parser.parse_args()

    try:
        # Initialize configuration
        config = VaultConfig()

        # Override vault path if provided
        if args.vault_path:
            config.update_config({"vault_path": args.vault_path})

        # Validate vault configuration
        issues = config.validate_config()
        if issues:
            print("❌ Configuration issues found:")
            for issue in issues:
                print(f"  • {issue}")
            print("\nRun setup first or use --vault-path to specify vault location.")
            return 1

        # Initialize converter
        converter = BulkConverter(args.staging_dir, config)

        if args.dry_run:
            stats = converter.dry_run()
            return 0

        # Process files
        delete_originals = args.delete_originals
        
        # Add confirmation for destructive operations
        if delete_originals:
            print("⚠️  WARNING: You have enabled --delete-originals")
            print("   This will PERMANENTLY DELETE your original files after conversion!")
            print("   Make sure you have backups before proceeding.")
            response = input("\n   Are you sure you want to continue? (type 'yes' to confirm): ")
            if response.lower() != 'yes':
                print("   Operation cancelled. Original files will be kept.")
                delete_originals = False
        
        stats = converter.process_files(delete_originals=delete_originals)

        if stats['errors'] > 0:
            print(f"\n⚠️  Completed with {stats['errors']} errors")
            return 1
        else:
            print(f"\n✅ Successfully processed {stats['processed']} files")
            return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
