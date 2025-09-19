#!/usr/bin/env python3
"""
Test script to verify the Notion dependency removal works correctly.
"""

import sys
import os

def test_imports():
    """Test that all imports work without Notion dependencies."""
    print("Testing imports...")
    
    try:
        # Test second_brain.py imports
        from second_brain import SecondBrain
        print("✓ SecondBrain import successful")
        
        # Test that it can be instantiated (will show config issues if any)
        brain = SecondBrain()
        print("✓ SecondBrain instantiation successful")
        
        # Test vault info
        info = brain.get_vault_info()
        if "error" in info:
            print(f"⚠️  Vault not configured: {info['error']}")
        else:
            print(f"✓ Vault configured: {info['vault_path']}")
            print(f"✓ Total notes: {info['total_notes']}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_no_notion_dependencies():
    """Test that no Notion dependencies are present."""
    print("\nTesting for Notion dependencies...")
    
    # Check second_brain.py for notion imports
    with open('second_brain.py', 'r') as f:
        content = f.read()
        
    if 'notion_client' in content:
        print("✗ Found notion_client import in second_brain.py")
        return False
    elif 'notion-client' in content:
        print("✗ Found notion-client reference in second_brain.py")
        return False
    else:
        print("✓ No Notion dependencies found in second_brain.py")
    
    # Check requirements.txt for notion dependencies
    with open('requirements.txt', 'r') as f:
        content = f.read()
        
    if 'notion' in content.lower():
        print("✗ Found Notion dependencies in requirements.txt")
        return False
    else:
        print("✓ No Notion dependencies found in requirements.txt")
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("TESTING NOTION DEPENDENCY REMOVAL")
    print("=" * 50)
    
    # Test 1: Check for Notion dependencies
    no_notion = test_no_notion_dependencies()
    
    # Test 2: Test imports and basic functionality
    imports_work = test_imports()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    if no_notion and imports_work:
        print("✅ ALL TESTS PASSED")
        print("✓ Notion dependencies successfully removed")
        print("✓ System is ready for local-first Obsidian workflow")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not no_notion:
            print("✗ Notion dependencies still present")
        if not imports_work:
            print("✗ Import or functionality issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
