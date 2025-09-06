#!/usr/bin/env python3
"""
Setup script for Obsidian Second Brain system.

This script handles initial configuration and vault setup.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_path)

# Import modules
from config_manager import VaultConfig
from vault_manager import VaultManager


def main():
    """Main setup function."""
    print("="*60)
    print("OBSIDIAN SECOND BRAIN SETUP")
    print("="*60)
    print("This script will help you configure your Obsidian Second Brain system.")
    print()
    
    # Initialize configuration
    config = VaultConfig()
    
    # Check if already configured
    vault_path = config.get_vault_path()
    if vault_path:
        print(f"✓ Vault already configured: {vault_path}")
        response = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Configure vault path
    print("\n1. Configuring vault path...")
    vault_path = config.get_vault_path()
    if not vault_path:
        print("✗ Failed to configure vault path.")
        return
    
    # Validate configuration
    print("\n2. Validating configuration...")
    issues = config.validate_config()
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
        
        response = input("Do you want to continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Setup vault structure
    print("\n3. Setting up vault structure...")
    if not config.setup_vault_structure():
        print("✗ Failed to setup vault structure.")
        return
    
    # Create templates
    print("\n4. Creating templates...")
    create_templates(config)
    
    # Test vault manager
    print("\n5. Testing vault manager...")
    try:
        manager = VaultManager(config)
        print("✓ Vault manager initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing vault manager: {e}")
        return
    
    # Create sample note
    print("\n6. Creating sample note...")
    sample_note = manager.create_note(
        title="Welcome to Your Second Brain",
        content="This is your first note in the Obsidian Second Brain system.\n\nYou can start adding more notes and organizing them using the PARA method.",
        folder_type="inbox",
        tags=["welcome", "getting-started"]
    )
    
    if sample_note:
        print("✓ Sample note created successfully")
    else:
        print("✗ Failed to create sample note")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print(f"Vault location: {vault_path}")
    print("You can now:")
    print("  - Open your vault in Obsidian")
    print("  - Start creating and organizing notes")
    print("  - Use the Python scripts for automation")
    print("\nFor more information, see the README.md file.")


def create_templates(config):
    """Create default templates in the vault."""
    vault_path = config.get_vault_path()
    if not vault_path:
        return
    
    templates_folder = os.path.join(vault_path, config.config["obsidian_config"]["templates_folder"])
    os.makedirs(templates_folder, exist_ok=True)
    
    # Daily note template
    daily_template = """---
title: "{{title}}"
created: "{{date}}"
tags: [daily-note]
---

# {{title}}

## Notes
- 

## Tasks
- [ ] 

## Reflections
- 

## Tomorrow
- 
"""
    
    # Project template
    project_template = """---
title: "{{title}}"
created: "{{date}}"
status: "active"
tags: [project, {{tags}}]
---

# {{title}}

## Overview
Brief description of the project.

## Goals
- [ ] 

## Timeline
- Start: 
- Deadline: 

## Resources
- 

## Notes
{{content}}

## Next Actions
- [ ] 
"""
    
    # Meeting template
    meeting_template = """---
title: "{{title}}"
created: "{{date}}"
tags: [meeting, {{tags}}]
---

# {{title}}

**Date:** {{date}}  
**Time:** {{time}}  
**Attendees:** 

## Agenda
1. 
2. 
3. 

## Discussion
- 

## Decisions
- 

## Action Items
- [ ] 
- [ ] 

## Next Steps
- 
"""
    
    # Book review template
    book_template = """---
title: "{{title}}"
created: "{{date}}"
tags: [book, review, {{tags}}]
---

# {{title}}

**Author:**  
**Published:**  
**Rating:** /5

## Summary
{{content}}

## Key Takeaways
- 

## Quotes
> 

## Related Books
- 

## Action Items
- [ ] 
"""
    
    templates = {
        "daily_note_template.md": daily_template,
        "project_template.md": project_template,
        "meeting_template.md": meeting_template,
        "book_review_template.md": book_template
    }
    
    for filename, content in templates.items():
        template_path = os.path.join(templates_folder, filename)
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Created template: {filename}")


if __name__ == "__main__":
    main()
