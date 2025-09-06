"""
Content type analyzer for categorizing files.

Analyzes file content and filenames to determine the appropriate
content type (project, resource, area, daily) for proper organization.
"""

import os
import re
from typing import Dict, List


class ContentAnalyzer:
    """Analyzes content to determine file categorization."""

    def __init__(self):
        """Initialize the content analyzer with detection patterns."""
        # Content type detection patterns
        self.content_patterns = {
            'project': [r'project', r'goal', r'timeline', r'deadline', r'milestone'],
            'resource': [r'note', r'idea', r'thought', r'reference', r'study'],
            'area': [r'area', r'responsibility', r'ongoing', r'process'],
            'daily': [r'daily', r'journal', r'log', r'entry', r'\d{4}-\d{2}-\d{2}']
        }

    def detect_content_type(self, file_path: str, content: str) -> str:
        """
        Detect the content type based on filename and content patterns.

        Args:
            file_path: Path to the file
            content: File content to analyze

        Returns:
            Content type: 'project', 'resource', 'area', 'daily', or 'inbox'
        """
        filename = os.path.basename(file_path).lower()
        content_lower = content.lower()

        # Check for daily note patterns in filename
        if any(pattern in filename for pattern in ['daily', 'journal', 'log']) or \
           re.search(r'\d{4}-\d{2}-\d{2}', filename):
            return 'daily'

        # Check content patterns
        for content_type, patterns in self.content_patterns.items():
            if any(re.search(pattern, content_lower) for pattern in patterns):
                return content_type

        # Default to resource for general notes
        return 'resource'

    def determine_folder_type(self, content_type: str, filename: str) -> str:
        """
        Determine the appropriate folder type for the content.

        Args:
            content_type: Detected content type
            filename: Original filename

        Returns:
            Folder type for organization
        """
        if content_type == 'daily':
            return 'inbox'  # Daily notes go to inbox first, then moved to daily notes folder
        elif content_type == 'project':
            return 'projects'
        elif content_type == 'area':
            return 'areas'
        else:
            return 'resources'

    def get_content_tags(self, content_type: str) -> List[str]:
        """
        Get appropriate tags based on content type.

        Args:
            content_type: The detected content type

        Returns:
            List of tags for the content type
        """
        if content_type == 'daily':
            return ['daily', 'daily-note']
        elif content_type == 'project':
            return ['project', 'project']
        elif content_type == 'area':
            return ['area', 'area']
        else:
            return ['resource', 'resource']
