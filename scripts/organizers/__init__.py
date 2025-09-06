"""
File organization modules for the Second Brain system.

This package provides tools for organizing files into appropriate
folder structures and extracting metadata like tags from file paths.
"""

from .folder_manager import FolderManager
from .tag_extractor import TagExtractor

__all__ = ['FolderManager', 'TagExtractor']
