"""
Title extraction utilities for file content.

Extracts meaningful titles from file content and filenames,
with fallback mechanisms for different content types.
"""

import os
import re
from typing import Optional


class TitleExtractor:
    """Extracts titles from file content and filenames."""

    def __init__(self):
        """Initialize the title extractor."""
        pass

    def sanitize_filename(self, name: str) -> str:
        """
        Remove unwanted characters and normalize spaces.

        Args:
            name: Filename to sanitize

        Returns:
            Sanitized filename
        """
        name = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)  # keep safe chars
        name = name.strip().replace(" ", "_")
        return name

    def extract_title_from_content(self, content: str, filename: str) -> str:
        """
        Extract a meaningful title from content or filename.

        Args:
            content: File content
            filename: Original filename

        Returns:
            Extracted title
        """
        # Try to find first heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        # Try to find first line that looks like a title
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not line.startswith('#') and len(line) < 100:
                return line

        # Fall back to filename
        base_name = os.path.splitext(filename)[0]
        return self.sanitize_filename(base_name).replace('_', ' ').title()

    def extract_title_from_filename(self, filename: str) -> str:
        """
        Extract title from filename only.

        Args:
            filename: Original filename

        Returns:
            Extracted title from filename
        """
        base_name = os.path.splitext(filename)[0]
        return self.sanitize_filename(base_name).replace('_', ' ').title()

    def clean_title(self, title: str) -> str:
        """
        Clean and normalize a title.

        Args:
            title: Title to clean

        Returns:
            Cleaned title
        """
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        title = re.sub(r'^(note|document|file):\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*$', '', title)
        
        return title.strip()
