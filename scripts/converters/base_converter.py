"""
Base converter class defining the interface for file format converters.

All specific converters should inherit from this base class to ensure
consistent behavior and interface across different conversion methods.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path


class BaseConverter(ABC):
    """Abstract base class for file format converters."""

    def __init__(self):
        """Initialize the converter."""
        self.supported_extensions = set()

    @abstractmethod
    def convert(self, file_path: str) -> Optional[str]:
        """
        Convert a file to Markdown format.

        Args:
            file_path: Path to the file to convert

        Returns:
            Path to the converted Markdown file, or None if conversion failed
        """
        pass

    def can_convert(self, file_path: str) -> bool:
        """
        Check if this converter can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this converter can handle the file
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_extensions

    def get_output_path(self, file_path: str) -> str:
        """
        Generate the output path for a converted file.

        Args:
            file_path: Path to the input file

        Returns:
            Path for the output Markdown file
        """
        return str(Path(file_path).with_suffix('.md'))
