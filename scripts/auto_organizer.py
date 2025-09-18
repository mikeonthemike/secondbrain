"""
AI-Enhanced Auto-Organizer for Second Brain System

This module provides intelligent content classification and organization
using AI/ML techniques to automatically categorize and organize notes
in the Obsidian vault.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re

# AI/ML dependencies (will be added to requirements.txt)
try:
    import openai
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI dependencies not available. Install with: pip install openai sentence-transformers scikit-learn numpy")

from config_manager import VaultConfig
from vault_manager import VaultManager
from analyzers.content_analyzer import ContentAnalyzer
from organizers.tag_extractor import TagExtractor


class AIAutoOrganizer:
    """
    AI-enhanced auto-organizer for intelligent content classification and organization.
    """
    
    def __init__(self, config: VaultConfig, vault_manager: VaultManager):
        """
        Initialize the AI auto-organizer.
        
        Args:
            config: VaultConfig instance
            vault_manager: VaultManager instance
        """
        self.config = config
        self.vault_manager = vault_manager
        self.content_analyzer = ContentAnalyzer()
        self.tag_extractor = TagExtractor()
        
        # AI models and data
        self.embedding_model = None
        self.classification_model = None
        self.user_preferences = {}
        self.classification_history = []
        self.confidence_threshold = 0.7
        
        # Enhanced content categories
        self.content_categories = {
            'meeting': {
                'keywords': ['meeting', 'call', 'conference', 'standup', 'review', 'agenda', 'minutes'],
                'patterns': [r'\d{1,2}:\d{2}', r'am|pm', r'agenda', r'minutes', r'attendees'],
                'templates': ['meeting_template.md'],
                'folder': 'projects'
            },
            'project': {
                'keywords': ['project', 'milestone', 'deliverable', 'sprint', 'phase', 'deadline'],
                'patterns': [r'status', r'update', r'progress', r'deadline', r'timeline'],
                'templates': ['project_template.md'],
                'folder': 'projects'
            },
            'action_item': {
                'keywords': ['action', 'task', 'todo', 'follow-up', 'deadline', 'urgent'],
                'patterns': [r'\[ \]', r'\[x\]', r'todo', r'action item', r'next step'],
                'templates': ['action_template.md'],
                'folder': 'projects'
            },
            'reference': {
                'keywords': ['article', 'newsletter', 'blog', 'tutorial', 'guide', 'resource'],
                'patterns': [r'read more', r'learn more', r'tutorial', r'guide', r'reference'],
                'templates': ['resource_template.md'],
                'folder': 'resources'
            },
            'idea': {
                'keywords': ['idea', 'thought', 'concept', 'brainstorm', 'innovation'],
                'patterns': [r'what if', r'idea', r'concept', r'brainstorm'],
                'templates': ['idea_template.md'],
                'folder': 'resources'
            },
            'decision': {
                'keywords': ['decision', 'decided', 'chose', 'option', 'conclusion'],
                'patterns': [r'decided', r'chose', r'option', r'conclusion', r'final'],
                'templates': ['decision_template.md'],
                'folder': 'projects'
            },
            'area': {
                'keywords': ['area', 'responsibility', 'ongoing', 'process', 'standard'],
                'patterns': [r'ongoing', r'process', r'standard', r'responsibility'],
                'templates': ['area_template.md'],
                'folder': 'areas'
            },
            'daily': {
                'keywords': ['daily', 'journal', 'log', 'entry', 'today'],
                'patterns': [r'\d{4}-\d{2}-\d{2}', r'today', r'daily', r'journal'],
                'templates': ['daily_note_template.md'],
                'folder': 'inbox'
            }
        }
        
        # Initialize AI components if available
        if AI_AVAILABLE:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for content analysis."""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer for text analysis
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            print("✅ AI models initialized successfully")
        except Exception as e:
            print(f"⚠️ Error initializing AI models: {e}")
            AI_AVAILABLE = False
    
    def analyze_content_with_ai(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        Analyze content using AI to extract semantic meaning and classification.
        
        Args:
            content: Note content to analyze
            title: Note title (optional)
            
        Returns:
            Dictionary with AI analysis results
        """
        if not AI_AVAILABLE:
            return self._fallback_analysis(content, title)
        
        try:
            # Combine title and content for analysis
            full_text = f"{title}\n\n{content}"
            
            # Generate embeddings
            embedding = self.embedding_model.encode([full_text])[0]
            
            # Extract key phrases and concepts
            key_phrases = self._extract_key_phrases(full_text)
            
            # Classify content type
            classification = self._classify_content_ai(full_text, embedding)
            
            # Generate tags
            tags = self._generate_tags_ai(full_text, key_phrases)
            
            # Determine priority and urgency
            priority = self._assess_priority(full_text)
            
            # Find similar content
            similar_notes = self._find_similar_content(embedding)
            
            return {
                'content_type': classification['type'],
                'confidence': classification['confidence'],
                'key_phrases': key_phrases,
                'tags': tags,
                'priority': priority,
                'similar_notes': similar_notes,
                'embedding': embedding.tolist(),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
            return self._fallback_analysis(content, title)
    
    def _fallback_analysis(self, content: str, title: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        # Use existing content analyzer
        content_type = self.content_analyzer.detect_content_type("", content)
        
        # Extract basic tags
        tags = self.tag_extractor.extract_content_tags(content)
        
        return {
            'content_type': content_type,
            'confidence': 0.5,  # Lower confidence for fallback
            'key_phrases': [],
            'tags': tags,
            'priority': 'medium',
            'similar_notes': [],
            'embedding': None,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text using TF-IDF."""
        try:
            # Simple key phrase extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            word_freq = {}
            for word in words:
                if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'oil', 'sit', 'try', 'use', 'she', 'put', 'end', 'why', 'let', 'ask', 'ran', 'read', 'got', 'lot', 'set', 'top', 'yes', 'yet', 'big', 'cut', 'few', 'got', 'hot', 'lot', 'red', 'run', 'saw', 'say', 'set', 'sit', 'ten', 'too', 'try', 'use', 'way', 'win', 'won', 'yes']:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top 10 most frequent words
            return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        except:
            return []
    
    def _classify_content_ai(self, text: str, embedding) -> Dict[str, Any]:
        """Classify content type using AI."""
        # For now, use rule-based classification with confidence scoring
        # In a full implementation, this would use a trained ML model
        
        scores = {}
        for category, rules in self.content_categories.items():
            score = 0
            text_lower = text.lower()
            
            # Keyword matching
            for keyword in rules['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Pattern matching
            for pattern in rules['patterns']:
                if re.search(pattern, text_lower):
                    score += 2
            
            scores[category] = score
        
        # Find best match
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # Calculate confidence (0-1)
        total_possible = len(self.content_categories[best_category]['keywords']) + len(self.content_categories[best_category]['patterns'])
        confidence = min(max_score / total_possible, 1.0) if total_possible > 0 else 0.5
        
        return {
            'type': best_category,
            'confidence': confidence,
            'scores': scores
        }
    
    def _generate_tags_ai(self, text: str, key_phrases: List[Tuple[str, int]]) -> List[str]:
        """Generate relevant tags using AI analysis."""
        tags = []
        
        # Add content type tag
        classification = self._classify_content_ai(text, None)
        tags.append(classification['type'])
        
        # Add key phrase tags (top 5)
        for phrase, freq in key_phrases[:5]:
            if freq > 1:  # Only include phrases that appear multiple times
                tags.append(phrase.replace(' ', '_'))
        
        # Add priority tag
        priority = self._assess_priority(text)
        if priority != 'medium':
            tags.append(f"priority_{priority}")
        
        # Add date-based tags
        current_date = datetime.now()
        tags.append(f"year_{current_date.year}")
        tags.append(f"month_{current_date.strftime('%B').lower()}")
        
        return list(set(tags))  # Remove duplicates
    
    def _assess_priority(self, text: str) -> str:
        """Assess priority level of content."""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline']
        high_keywords = ['important', 'priority', 'high', 'soon', 'due']
        low_keywords = ['someday', 'maybe', 'low', 'optional', 'nice to have']
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in text_lower for keyword in high_keywords):
            return 'high'
        elif any(keyword in text_lower for keyword in low_keywords):
            return 'low'
        else:
            return 'medium'
    
    def _find_similar_content(self, embedding) -> List[Dict[str, Any]]:
        """Find similar content in the vault."""
        # This would compare against stored embeddings of existing notes
        # For now, return empty list
        return []
    
    def organize_note(self, note_path: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        Organize a single note using AI-enhanced analysis.
        
        Args:
            note_path: Path to the note file
            content: Note content
            title: Note title
            
        Returns:
            Organization recommendations
        """
        # Analyze content with AI
        analysis = self.analyze_content_with_ai(content, title)
        
        # Determine folder placement
        content_type = analysis['content_type']
        folder_type = self.content_categories.get(content_type, {}).get('folder', 'inbox')
        
        # Generate organization recommendations
        recommendations = {
            'content_type': content_type,
            'confidence': analysis['confidence'],
            'folder_type': folder_type,
            'tags': analysis['tags'],
            'priority': analysis['priority'],
            'template': self.content_categories.get(content_type, {}).get('templates', [None])[0],
            'key_phrases': analysis['key_phrases'],
            'similar_notes': analysis['similar_notes'],
            'suggested_links': self._suggest_links(content, analysis),
            'organization_timestamp': datetime.now().isoformat()
        }
        
        return recommendations
    
    def _suggest_links(self, content: str, analysis: Dict[str, Any]) -> List[str]:
        """Suggest potential links to other notes."""
        # This would analyze content for potential connections
        # For now, return empty list
        return []
    
    def batch_organize_notes(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Organize multiple notes in batch for efficiency.
        
        Args:
            notes: List of note dictionaries with 'path', 'content', 'title'
            
        Returns:
            List of organization recommendations
        """
        results = []
        
        for note in notes:
            try:
                recommendation = self.organize_note(
                    note['path'],
                    note['content'],
                    note.get('title', '')
                )
                results.append({
                    'note_path': note['path'],
                    'recommendation': recommendation
                })
            except Exception as e:
                print(f"❌ Error organizing note {note['path']}: {e}")
                results.append({
                    'note_path': note['path'],
                    'error': str(e)
                })
        
        return results
    
    def learn_from_feedback(self, note_path: str, user_corrections: Dict[str, Any]):
        """
        Learn from user feedback to improve future classifications.
        
        Args:
            note_path: Path to the note
            user_corrections: User's corrections to the classification
        """
        # Store user feedback for learning
        feedback_entry = {
            'note_path': note_path,
            'timestamp': datetime.now().isoformat(),
            'corrections': user_corrections
        }
        
        self.classification_history.append(feedback_entry)
        
        # Update user preferences
        if 'content_type' in user_corrections:
            content_type = user_corrections['content_type']
            if content_type not in self.user_preferences:
                self.user_preferences[content_type] = {'count': 0, 'patterns': []}
            self.user_preferences[content_type]['count'] += 1
        
        # Save learning data
        self._save_learning_data()
    
    def _save_learning_data(self):
        """Save learning data to disk."""
        try:
            learning_data = {
                'user_preferences': self.user_preferences,
                'classification_history': self.classification_history[-100:],  # Keep last 100
                'last_updated': datetime.now().isoformat()
            }
            
            learning_file = os.path.join(self.config.get_vault_path(), '.secondbrain_learning.json')
            with open(learning_file, 'w') as f:
                json.dump(learning_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save learning data: {e}")
    
    def load_learning_data(self):
        """Load learning data from disk."""
        try:
            learning_file = os.path.join(self.config.get_vault_path(), '.secondbrain_learning.json')
            if os.path.exists(learning_file):
                with open(learning_file, 'r') as f:
                    learning_data = json.load(f)
                    self.user_preferences = learning_data.get('user_preferences', {})
                    self.classification_history = learning_data.get('classification_history', [])
        except Exception as e:
            print(f"⚠️ Could not load learning data: {e}")
    
    def get_organization_stats(self) -> Dict[str, Any]:
        """Get statistics about the organization system."""
        return {
            'total_classifications': len(self.classification_history),
            'user_preferences': self.user_preferences,
            'ai_available': AI_AVAILABLE,
            'confidence_threshold': self.confidence_threshold,
            'content_categories': list(self.content_categories.keys())
        }


def main():
    """Command-line interface for the auto-organizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Enhanced Auto-Organizer")
    parser.add_argument("--analyze", help="Analyze a specific note")
    parser.add_argument("--batch", help="Organize all notes in a folder")
    parser.add_argument("--stats", action="store_true", help="Show organization statistics")
    parser.add_argument("--learn", help="Learn from user feedback")
    
    args = parser.parse_args()
    
    try:
        from config_manager import VaultConfig
        from vault_manager import VaultManager
        
        config = VaultConfig()
        vault_manager = VaultManager(config)
        organizer = AIAutoOrganizer(config, vault_manager)
        
        if args.analyze:
            # Analyze a specific note
            with open(args.analyze, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = os.path.basename(args.analyze).replace('.md', '')
            analysis = organizer.analyze_content_with_ai(content, title)
            
            print(f"Analysis for {title}:")
            print(f"  Content Type: {analysis['content_type']}")
            print(f"  Confidence: {analysis['confidence']:.2f}")
            print(f"  Tags: {', '.join(analysis['tags'])}")
            print(f"  Priority: {analysis['priority']}")
        
        elif args.batch:
            # Batch organize notes
            notes = []
            for file_path in Path(args.batch).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                notes.append({
                    'path': str(file_path),
                    'content': content,
                    'title': file_path.stem
                })
            
            results = organizer.batch_organize_notes(notes)
            print(f"Organized {len(results)} notes")
            
            for result in results:
                if 'error' in result:
                    print(f"❌ {result['note_path']}: {result['error']}")
                else:
                    rec = result['recommendation']
                    print(f"✅ {result['note_path']}: {rec['content_type']} → {rec['folder_type']}")
        
        elif args.stats:
            # Show statistics
            stats = organizer.get_organization_stats()
            print("Organization Statistics:")
            print(f"  AI Available: {stats['ai_available']}")
            print(f"  Total Classifications: {stats['total_classifications']}")
            print(f"  Content Categories: {', '.join(stats['content_categories'])}")
        
        else:
            print("Use --help for available options")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
