#!/usr/bin/env python3
"""
Launcher script for Obsidian Second Brain setup.

This script ensures proper module imports when running setup directly.
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add scripts directory to path
scripts_dir = os.path.join(current_dir, 'scripts')
sys.path.insert(0, scripts_dir)

# Now import and run setup
from setup import main

if __name__ == "__main__":
    main()
