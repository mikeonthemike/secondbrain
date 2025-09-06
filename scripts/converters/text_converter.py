"""
Simple text file converter for plain text files.

Handles basic text file conversion with proper encoding detection
and fallback mechanisms for different text encodings.
"""

import os
from typing import Optional
from pathlib import Path
from .base_converter import BaseConverter


class TextConverter(BaseConverter):
    """Converter for plain text files."""

    def __init__(self):
        """Initialize the text converter."""
        super().__init__()
        self.supported_extensions = {'.txt'}

    def convert(self, file_path: str) -> Optional[str]:
        """
        Convert a plain text file to Markdown.

        Args:
            file_path: Path to the text file to convert

        Returns:
            Path to the converted Markdown file, or None if conversion failed
        """
        if not self.can_convert(file_path):
            return None

        md_path = self.get_output_path(file_path)

        # Try to read with UTF-8 encoding first
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fall back to latin-1 encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ Error reading text file {file_path}: {e}")
                return None

        # Write the content to the markdown file
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Converted {os.path.basename(file_path)} (txt → markdown)")
            return md_path
        except Exception as e:
            print(f"❌ Error writing markdown file {md_path}: {e}")
            return None
