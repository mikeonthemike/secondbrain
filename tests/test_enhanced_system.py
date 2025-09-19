#!/usr/bin/env python3
"""
Test script for the enhanced content analyzer and frontmatter system.
Tests against the user's actual vault to demonstrate improvements.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from analyzers.content_analyzer import ContentAnalyzer
from vault_manager import VaultManager

def test_enhanced_system(vault_path: str, sample_size: int = 10):
    """Test the enhanced system against the user's vault."""
    print(f"🧪 Testing Enhanced Content Analysis System")
    print(f"📁 Vault Path: {vault_path}")
    print(f"📊 Sample Size: {sample_size}")
    print("=" * 60)
    
    # Initialize the enhanced analyzer
    analyzer = ContentAnalyzer()
    
    # Find markdown files in the vault
    vault_path = Path(vault_path)
    if not vault_path.exists():
        print(f"❌ Vault path does not exist: {vault_path}")
        return
    
    md_files = list(vault_path.rglob("*.md"))
    print(f"📄 Found {len(md_files)} markdown files")
    
    if not md_files:
        print("❌ No markdown files found in vault")
        return
    
    # Test on a sample of files
    sample_files = md_files[:sample_size]
    results = []
    
    print(f"\n🔍 Analyzing {len(sample_files)} sample files...")
    print("-" * 60)
    
    for i, file_path in enumerate(sample_files, 1):
        print(f"\n📄 File {i}/{len(sample_files)}: {file_path.name}")
        print(f"   Path: {file_path.relative_to(vault_path)}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Analyze with enhanced system
            analysis = analyzer.detect_content_type(str(file_path), content)
            
            # Generate enhanced tags
            tags = analyzer.get_content_tags(
                analysis['primary_type'], 
                analysis
            )
            
            # Generate rich metadata
            metadata = analyzer.generate_rich_metadata(
                analysis['primary_type'],
                content,
                str(file_path),
                analysis
            )
            
            # Store results
            result = {
                'file_path': str(file_path.relative_to(vault_path)),
                'analysis': analysis,
                'tags': tags,
                'metadata': metadata
            }
            results.append(result)
            
            # Display results
            print(f"   🎯 Content Type: {analysis['primary_type']} (confidence: {analysis['confidence']:.2f})")
            if analysis['secondary_types']:
                print(f"   🔗 Secondary Types: {', '.join(analysis['secondary_types'])}")
            print(f"   🏷️  Tags: {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
            print(f"   📊 Word Count: {metadata.get('word_count', 0)}")
            print(f"   ⏱️  Reading Time: {metadata.get('reading_time', 0)} min")
            
            # Show type-specific metadata
            if analysis['primary_type'] == 'meeting':
                print(f"   👥 Attendees: {metadata.get('attendees', [])}")
                print(f"   ✅ Action Items: {metadata.get('action_items_count', 0)}")
            elif analysis['primary_type'] == 'project':
                print(f"   📅 Deadline: {metadata.get('deadline', 'None')}")
                print(f"   👥 Stakeholders: {metadata.get('stakeholders', [])}")
            elif analysis['primary_type'] == 'decision':
                print(f"   🎯 Status: {metadata.get('decision_status', 'Unknown')}")
                print(f"   💪 Rationale: {metadata.get('rationale_strength', 'Unknown')}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing file: {e}")
            continue
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Content type distribution
    content_types = {}
    confidence_scores = []
    total_tags = []
    
    for result in results:
        content_type = result['analysis']['primary_type']
        content_types[content_type] = content_types.get(content_type, 0) + 1
        confidence_scores.append(result['analysis']['confidence'])
        total_tags.extend(result['tags'])
    
    print(f"\n📈 Content Type Distribution:")
    for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {content_type}: {count} files")
    
    print(f"\n🎯 Confidence Scores:")
    print(f"   Average: {sum(confidence_scores)/len(confidence_scores):.2f}")
    print(f"   High (>0.8): {sum(1 for c in confidence_scores if c > 0.8)}")
    print(f"   Medium (0.5-0.8): {sum(1 for c in confidence_scores if 0.5 <= c <= 0.8)}")
    print(f"   Low (<0.5): {sum(1 for c in confidence_scores if c < 0.5)}")
    
    # Tag analysis
    from collections import Counter
    tag_counts = Counter(total_tags)
    print(f"\n🏷️  Most Common Tags:")
    for tag, count in tag_counts.most_common(10):
        print(f"   {tag}: {count}")
    
    # Quality metrics
    structured_files = sum(1 for r in results if r['metadata'].get('has_structure', False))
    linked_files = sum(1 for r in results if r['metadata'].get('has_links', False))
    task_files = sum(1 for r in results if r['metadata'].get('has_tasks', False))
    
    print(f"\n📊 Content Quality:")
    print(f"   Structured files: {structured_files}/{len(results)} ({structured_files/len(results)*100:.1f}%)")
    print(f"   Files with links: {linked_files}/{len(results)} ({linked_files/len(results)*100:.1f}%)")
    print(f"   Files with tasks: {task_files}/{len(results)} ({task_files/len(results)*100:.1f}%)")
    
    # Save detailed results
    output_file = "enhanced_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'vault_path': str(vault_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'total_files_analyzed': len(results),
            'results': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("\n✅ Enhanced system test completed!")
    
    return results

def demonstrate_frontmatter_generation():
    """Demonstrate the enhanced frontmatter generation."""
    print("\n" + "=" * 60)
    print("📝 FRONTMATTER GENERATION DEMO")
    print("=" * 60)
    
    # Sample content for demonstration
    sample_content = """# Weekly Team Standup

## Attendees
- John Smith
- Jane Doe
- Mike Johnson

## Agenda
1. Review last week's progress
2. Discuss blockers
3. Plan this week's tasks

## Action Items
- [ ] Update project documentation
- [ ] Review code changes
- [ ] Schedule client meeting

## Notes
Great progress on the new feature. Need to address the performance issue before Friday's deadline.
"""
    
    # Initialize analyzer and vault manager
    analyzer = ContentAnalyzer()
    vault_manager = VaultManager()
    
    # Analyze content
    analysis = analyzer.detect_content_type("sample_standup.md", sample_content)
    tags = analyzer.get_content_tags(analysis['primary_type'], analysis)
    
    # Generate enhanced frontmatter
    frontmatter = vault_manager._generate_enhanced_frontmatter(
        "Weekly Team Standup",
        sample_content,
        tags,
        None,
        analysis
    )
    
    # Format as YAML
    yaml_content = vault_manager._format_yaml_frontmatter(frontmatter)
    
    print("📄 Sample Content:")
    print(sample_content[:200] + "...")
    
    print(f"\n🎯 Analysis Results:")
    print(f"   Content Type: {analysis['primary_type']}")
    print(f"   Confidence: {analysis['confidence']:.2f}")
    print(f"   Tags: {', '.join(tags)}")
    
    print(f"\n📝 Generated Frontmatter:")
    print("---")
    print(yaml_content)
    print("---")

if __name__ == "__main__":
    # Test against the user's vault
    vault_path = r"C:\Users\micha\Documents\Michael\all the things"
    
    print("🚀 Enhanced Content Analysis System Test")
    print("=" * 60)
    
    # Run the test
    results = test_enhanced_system(vault_path, sample_size=15)
    
    # Demonstrate frontmatter generation
    demonstrate_frontmatter_generation()
    
    print("\n🎉 Test completed! Check the results above and the generated JSON file for detailed analysis.")
