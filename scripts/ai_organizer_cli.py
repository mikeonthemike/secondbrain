"""
Command-line interface for the AI-enhanced auto-organizer.
"""

import os
import sys
import argparse
from pathlib import Path

# Add scripts directory to path
scripts_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, scripts_path)

from config_manager import VaultConfig
from vault_manager import VaultManager
from auto_organizer import AIAutoOrganizer


def analyze_note(organizer: AIAutoOrganizer, note_path: str):
    """Analyze a single note or all markdown files in a directory."""
    path = Path(note_path)
    
    # Check if path is a directory
    if path.is_dir():
        print(f"\n📁 Analyzing all markdown files in directory: {note_path}")
        print("=" * 60)
        
        # Find all markdown files in the directory (recursively)
        md_files = list(path.rglob("*.md"))
        if not md_files:
            print(f"❌ No markdown files found in {note_path}")
            return None
        
        print(f"Found {len(md_files)} markdown files to analyze")
        
        results = []
        for md_file in md_files:
            print(f"\n📝 Analyzing: {md_file.name}")
            result = _analyze_single_file(organizer, str(md_file))
            if result:
                results.append(result)
        
        print(f"\n📊 Analysis Summary:")
        print("=" * 60)
        print(f"Total files analyzed: {len(results)}")
        
        # Group by content type
        content_types = {}
        for result in results:
            content_type = result['content_type']
            if content_type not in content_types:
                content_types[content_type] = 0
            content_types[content_type] += 1
        
        print(f"Content type distribution:")
        for content_type, count in content_types.items():
            print(f"  {content_type}: {count} files")
        
        return results
    
    # Handle single file
    elif path.is_file():
        return _analyze_single_file(organizer, note_path)
    
    else:
        print(f"❌ Path not found: {note_path}")
        return None


def _analyze_single_file(organizer: AIAutoOrganizer, file_path: str):
    """Analyze a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = Path(file_path).stem
        analysis = organizer.analyze_content_with_ai(content, title)
        
        print(f"\n📝 Analysis for: {title}")
        print("=" * 50)
        print(f"Content Type: {analysis['content_type']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Priority: {analysis['priority']}")
        print(f"Tags: {', '.join(analysis['tags'])}")
        
        if analysis['key_phrases']:
            print(f"Key Phrases: {', '.join([f'{phrase} ({freq})' for phrase, freq in analysis['key_phrases'][:5]])}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return None


def organize_note(organizer: AIAutoOrganizer, note_path: str):
    """Get organization recommendations for a note or all markdown files in a directory."""
    path = Path(note_path)
    
    # Check if path is a directory
    if path.is_dir():
        print(f"\n🎯 Getting organization recommendations for all markdown files in directory: {note_path}")
        print("=" * 70)
        
        # Find all markdown files in the directory (recursively)
        md_files = list(path.rglob("*.md"))
        if not md_files:
            print(f"❌ No markdown files found in {note_path}")
            return None
        
        print(f"Found {len(md_files)} markdown files to organize")
        
        results = []
        for md_file in md_files:
            print(f"\n🎯 Organizing: {md_file.name}")
            result = _organize_single_file(organizer, str(md_file))
            if result:
                results.append(result)
        
        print(f"\n📊 Organization Summary:")
        print("=" * 70)
        print(f"Total files organized: {len(results)}")
        
        # Group by suggested folder type
        folder_types = {}
        for result in results:
            folder_type = result['folder_type']
            if folder_type not in folder_types:
                folder_types[folder_type] = 0
            folder_types[folder_type] += 1
        
        print(f"Suggested folder distribution:")
        for folder_type, count in folder_types.items():
            print(f"  {folder_type}: {count} files")
        
        return results
    
    # Handle single file
    elif path.is_file():
        return _organize_single_file(organizer, note_path)
    
    else:
        print(f"❌ Path not found: {note_path}")
        return None


def _organize_single_file(organizer: AIAutoOrganizer, file_path: str):
    """Get organization recommendations for a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = Path(file_path).stem
        recommendations = organizer.organize_note(file_path, content, title)
        
        print(f"\n🎯 Organization Recommendations for: {title}")
        print("=" * 50)
        print(f"Content Type: {recommendations['content_type']}")
        print(f"Confidence: {recommendations['confidence']:.2f}")
        print(f"Suggested Folder: {recommendations['folder_type']}")
        print(f"Template: {recommendations['template'] or 'None'}")
        print(f"Tags: {', '.join(recommendations['tags'])}")
        print(f"Priority: {recommendations['priority']}")
        
        if recommendations['suggested_links']:
            print(f"Suggested Links: {', '.join(recommendations['suggested_links'])}")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error organizing {file_path}: {e}")
        return None


def batch_organize(organizer: AIAutoOrganizer, folder_path: str):
    """Organize all notes in a folder."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    md_files = list(folder.glob("*.md"))
    if not md_files:
        print(f"📁 No markdown files found in {folder_path}")
        return
    
    print(f"\n�� Organizing {len(md_files)} notes in {folder_path}...")
    
    notes = []
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            notes.append({
                'path': str(file_path),
                'content': content,
                'title': file_path.stem
            })
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
    
    results = organizer.batch_organize_notes(notes)
    
    print(f"\n📊 Batch Organization Results:")
    print("=" * 50)
    
    success_count = 0
    for result in results:
        if 'error' in result:
            print(f"❌ {Path(result['note_path']).name}: {result['error']}")
        else:
            rec = result['recommendation']
            print(f"✅ {Path(result['note_path']).name}: {rec['content_type']} → {rec['folder_type']} (conf: {rec['confidence']:.2f})")
            success_count += 1
    
    print(f"\n📈 Summary: {success_count}/{len(results)} notes organized successfully")


def show_stats(organizer: AIAutoOrganizer):
    """Show organization statistics."""
    stats = organizer.get_organization_stats()
    
    print("\n📊 AI Auto-Organizer Statistics")
    print("=" * 50)
    print(f"AI Available: {'✅ Yes' if stats['ai_available'] else '❌ No'}")
    print(f"Total Classifications: {stats['total_classifications']}")
    print(f"Confidence Threshold: {stats['confidence_threshold']}")
    print(f"Content Categories: {len(stats['content_categories'])}")
    
    if stats['user_preferences']:
        print(f"\nUser Preferences:")
        for category, prefs in stats['user_preferences'].items():
            print(f"  {category}: {prefs['count']} corrections")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="AI-Enhanced Auto-Organizer CLI")
    parser.add_argument("--analyze", help="Analyze a specific note file")
    parser.add_argument("--organize", help="Get organization recommendations for a note")
    parser.add_argument("--batch", help="Organize all notes in a folder")
    parser.add_argument("--stats", action="store_true", help="Show organization statistics")
    parser.add_argument("--config", help="Path to AI organizer config file")
    
    args = parser.parse_args()
    
    try:
        # Initialize components
        config = VaultConfig()
        vault_manager = VaultManager(config)
        organizer = AIAutoOrganizer(config, vault_manager)
        
        # Load learning data
        organizer.load_learning_data()
        
        if args.analyze:
            analyze_note(organizer, args.analyze)
        
        elif args.organize:
            organize_note(organizer, args.organize)
        
        elif args.batch:
            batch_organize(organizer, args.batch)
        
        elif args.stats:
            show_stats(organizer)
        
        else:
            print("AI-Enhanced Auto-Organizer")
            print("Use --help for available options")
            print("\nExamples:")
            print("  python ai_organizer_cli.py --analyze notes/my_note.md")
            print("  python ai_organizer_cli.py --organize notes/my_note.md")
            print("  python ai_organizer_cli.py --batch notes/")
            print("  python ai_organizer_cli.py --stats")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
