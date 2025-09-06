"""
Pandoc-based converter for complex file formats.

Handles conversion of various file formats (docx, rtf, html, etc.) using
the pandoc command-line tool with proper path detection and error handling.
"""

import os
import subprocess
from typing import Optional
from pathlib import Path
from .base_converter import BaseConverter


class PandocConverter(BaseConverter):
    """Converter for complex file formats using pandoc."""

    def __init__(self):
        """Initialize the pandoc converter."""
        super().__init__()
        self.supported_extensions = {
            '.rtf', '.docx', '.doc', '.html', '.htm', 
            '.odt', '.epub', '.tex', '.md'
        }
        
        # Format mapping for pandoc
        self.format_map = {
            '.rtf': 'rtf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.html': 'html',
            '.htm': 'html',
            '.odt': 'odt',
            '.epub': 'epub',
            '.tex': 'latex',
            '.md': 'markdown'
        }

    def _find_pandoc(self) -> Optional[str]:
        """
        Find the pandoc executable in common locations.

        Returns:
            Path to pandoc executable, or None if not found
        """
        pandoc_paths = [
            "pandoc",  # In PATH
            os.path.expanduser("~/AppData/Local/Pandoc/pandoc.exe"),  # Windows user install
            "C:/Program Files/Pandoc/pandoc.exe",  # Windows system install
            "/usr/local/bin/pandoc",  # macOS/Linux
            "/usr/bin/pandoc"  # Linux
        ]

        for path in pandoc_paths:
            try:
                if path == "pandoc":
                    # Test if pandoc is in PATH
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    return path
                elif os.path.exists(path):
                    # Test if pandoc is in a specific location
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    return path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return None

    def convert(self, file_path: str) -> Optional[str]:
        """
        Convert a file to Markdown using pandoc.

        Args:
            file_path: Path to the file to convert

        Returns:
            Path to the converted Markdown file, or None if conversion failed
        """
        if not self.can_convert(file_path):
            return None

        # Find pandoc executable
        pandoc_cmd = self._find_pandoc()
        if not pandoc_cmd:
            print("❌ Pandoc not found. Please install pandoc:")
            print("   Windows: winget install --id JohnMacFarlane.Pandoc")
            print("   Or download from: https://pandoc.org/installing.html")
            return None

        # Determine input format
        file_ext = Path(file_path).suffix.lower()
        input_format = self.format_map.get(file_ext)
        if not input_format:
            print(f"❌ Unsupported file format: {file_ext}")
            return None

        # Generate output path
        md_path = self.get_output_path(file_path)

        # Perform conversion
        try:
            subprocess.run(
                [pandoc_cmd, file_path, "-f", input_format, "-t", "markdown", "-o", md_path],
                check=True
            )
            print(f"✅ Converted {os.path.basename(file_path)} ({input_format} → markdown)")
            return md_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error converting {file_path} with format '{input_format}': {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error during conversion: {e}")
            return None
