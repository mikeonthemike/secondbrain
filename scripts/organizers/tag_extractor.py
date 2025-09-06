"""
Tag extraction utilities for file organization.

Extracts tags from folder hierarchy and content to provide
proper categorization and linking in the vault.
"""

import re
from pathlib import Path
from typing import List


class TagExtractor:
    """Extracts tags from file paths and content."""

    def __init__(self):
        """Initialize the tag extractor."""
        pass

    def extract_folder_tags(self, file_path: Path, staging_dir: Path) -> List[str]:
        """
        Extract folder names as tags from the relative path.
        
        Args:
            file_path: Path to the file
            staging_dir: Root staging directory
            
        Returns:
            List of folder names as tags
        """
        try:
            # Get relative path from staging directory
            rel_path = file_path.relative_to(staging_dir)
            # Get all parent directories (excluding the file itself)
            folder_parts = rel_path.parts[:-1]
            # Convert to tags (lowercase, replace spaces/hyphens with underscores)
            tags = []
            for part in folder_parts:
                tag = part.lower().replace(' ', '_').replace('-', '_')
                # Remove special characters
                tag = re.sub(r'[^a-zA-Z0-9_]', '', tag)
                if tag:
                    tags.append(tag)
            return tags
        except ValueError:
            # File is not relative to staging directory
            return []

    def extract_content_tags(self, content: str) -> List[str]:
        """
        Extract tags from content patterns.

        Args:
            content: File content to analyze

        Returns:
            List of extracted tags
        """
        tags = []
        
        # Look for hashtag patterns
        hashtag_pattern = r'#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, content)
        tags.extend(hashtags)
        
        # Look for @ mentions
        mention_pattern = r'@([a-zA-Z0-9_]+)'
        mentions = re.findall(mention_pattern, content)
        tags.extend(mentions)
        
        return list(set(tags))  # Remove duplicates

    def combine_tags(self, content_type: str, folder_tags: List[str], content_tags: List[str] = None) -> List[str]:
        """
        Combine different types of tags into a final tag list.

        Args:
            content_type: Type of content (project, resource, etc.)
            folder_tags: Tags extracted from folder structure
            content_tags: Tags extracted from content (optional)

        Returns:
            Combined list of tags
        """
        tags = [content_type] + folder_tags
        
        if content_tags:
            tags.extend(content_tags)
        
        # Add type-specific tags
        if content_type == 'daily':
            tags.append('daily-note')
        elif content_type == 'project':
            tags.append('project')
        elif content_type == 'area':
            tags.append('area')
        else:
            tags.append('resource')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags

    def sanitize_tag(self, tag: str) -> str:
        """
        Sanitize a tag to ensure it's valid.

        Args:
            tag: Tag to sanitize

        Returns:
            Sanitized tag
        """
        # Remove special characters and normalize
        tag = re.sub(r'[^a-zA-Z0-9_-]', '', tag)
        tag = tag.lower().strip()
        return tag
