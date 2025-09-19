#!/usr/bin/env python3
"""
Improved content analyzer tuned for real-world vault content.
Based on analysis of the user's actual vault files.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import yaml


class ImprovedContentAnalyzer:
    """Content analyzer tuned for real-world vault content."""

    def __init__(self):
        """Initialize with patterns tuned for actual vault content."""
        # More realistic content patterns based on actual analysis
        self.content_patterns = {
            'meeting': {
                'keywords': ['meeting', 'call', 'standup', 'review', 'agenda', 'minutes', 'attendees', 'discussion', 'sync'],
                'patterns': [r'\d{1,2}:\d{2}', r'am|pm', r'agenda', r'minutes', r'attendees', r'action items', r'notes from'],
                'weight': 0.7,
                'structure_indicators': ['agenda', 'attendees', 'action items', 'next steps', 'discussion']
            },
            'project': {
                'keywords': ['project', 'milestone', 'deliverable', 'sprint', 'phase', 'deadline', 'timeline', 'implementation', 'development'],
                'patterns': [r'status', r'update', r'progress', r'deadline', r'timeline', r'roadmap', r'plan', r'feature'],
                'weight': 0.8,
                'structure_indicators': ['goals', 'objectives', 'timeline', 'deliverables', 'requirements']
            },
            'decision': {
                'keywords': ['decision', 'decided', 'chose', 'option', 'conclusion', 'recommendation', 'choose', 'select'],
                'patterns': [r'decided', r'chose', r'option', r'conclusion', r'final', r'approved', r'pros', r'cons'],
                'weight': 0.6,
                'structure_indicators': ['pros', 'cons', 'alternatives', 'rationale', 'reasoning']
            },
            'template': {
                'keywords': ['template', 'checklist', 'guide', 'framework', 'process', 'format', 'structure'],
                'patterns': [r'template', r'checklist', r'guide', r'framework', r'process', r'{{', r'}}'],
                'weight': 0.5,
                'structure_indicators': ['{{', '}}', 'checklist', 'steps', 'instructions']
            },
            'daily_note': {
                'keywords': ['daily', 'journal', 'log', 'entry', 'today', 'reflection', 'notes', 'thoughts'],
                'patterns': [r'\d{4}-\d{2}-\d{2}', r'today', r'daily', r'journal', r'reflection', r'thoughts'],
                'weight': 0.9,
                'structure_indicators': ['today', 'yesterday', 'tomorrow', 'reflection', 'thoughts']
            },
            'area': {
                'keywords': ['area', 'responsibility', 'ongoing', 'process', 'standard', 'maintenance', 'routine'],
                'patterns': [r'ongoing', r'process', r'standard', r'responsibility', r'maintenance', r'routine'],
                'weight': 0.6,
                'structure_indicators': ['ongoing', 'process', 'standard', 'responsibility']
            },
            'resource': {
                'keywords': ['note', 'idea', 'thought', 'reference', 'study', 'article', 'information', 'knowledge'],
                'patterns': [r'note', r'idea', r'thought', r'reference', r'study', r'information'],
                'weight': 0.4,
                'structure_indicators': ['reference', 'study', 'research', 'information']
            },
            'technical': {
                'keywords': ['code', 'programming', 'software', 'technical', 'api', 'bug', 'fix', 'implementation', 'function'],
                'patterns': [r'function', r'class', r'method', r'api', r'bug', r'fix', r'code', r'programming'],
                'weight': 0.7,
                'structure_indicators': ['function', 'class', 'method', 'api', 'bug', 'fix']
            }
        }

    def detect_content_type(self, file_path: str, content: str) -> Dict[str, Any]:
        """Enhanced content type detection with better real-world tuning."""
        analysis = {
            'primary_type': 'resource',
            'confidence': 0.0,
            'secondary_types': [],
            'content_indicators': [],
            'filename_indicators': [],
            'context_indicators': [],
            'structure_indicators': []
        }
        
        # Layer 1: Filename analysis (more aggressive)
        filename_score = self._analyze_filename_improved(file_path)
        
        # Layer 2: Content structure analysis
        structure_score = self._analyze_content_structure_improved(content)
        
        # Layer 3: Semantic content analysis (more lenient)
        semantic_score = self._analyze_semantic_content_improved(content)
        
        # Layer 4: Context analysis
        context_score = self._analyze_context_improved(file_path, content)
        
        # Combine scores with adjusted weights
        final_score = self._combine_scores_improved(filename_score, structure_score, 
                                                  semantic_score, context_score)
        
        # Determine primary type and confidence
        if final_score:
            analysis['primary_type'] = max(final_score, key=final_score.get)
            analysis['confidence'] = final_score[analysis['primary_type']]
            
            # Add secondary types (lower threshold)
            sorted_types = sorted(final_score.items(), key=lambda x: x[1], reverse=True)
            analysis['secondary_types'] = [t[0] for t in sorted_types[1:3] if t[1] > 0.1]
        
        return analysis

    def _analyze_filename_improved(self, file_path: str) -> Dict[str, float]:
        """Improved filename analysis with better pattern matching."""
        filename = os.path.basename(file_path).lower()
        
        # Clean up messy filenames more aggressively
        clean_name = self._clean_filename_improved(filename)
        
        # More comprehensive patterns
        patterns = {
            'meeting': r'(meeting|call|standup|review|agenda|sync|discussion)',
            'project': r'(project|milestone|deliverable|sprint|implementation|plan|feature)',
            'template': r'(template|checklist|guide|framework|process|format)',
            'daily_note': r'(\d{4}-\d{2}-\d{2}|daily|journal|log)',
            'decision': r'(decision|chose|option|conclusion|choose)',
            'area': r'(area|responsibility|process|maintenance|routine)',
            'resource': r'(note|idea|reference|study|information|knowledge)',
            'technical': r'(code|programming|software|technical|api|bug|fix|function)'
        }
        
        scores = {}
        for content_type, pattern in patterns.items():
            if re.search(pattern, clean_name):
                scores[content_type] = 0.6  # Lower threshold for filename matches
        
        # Special handling for messy filenames
        if re.search(r'[0-9a-f]{8,}', filename):  # UUID-like patterns
            scores['technical'] = scores.get('technical', 0) + 0.3
        
        if len(filename.split('.')) > 2:  # Multiple extensions
            scores['technical'] = scores.get('technical', 0) + 0.2
        
        return scores

    def _clean_filename_improved(self, filename: str) -> str:
        """More aggressive filename cleaning."""
        # Remove file extension
        clean = os.path.splitext(filename)[0]
        
        # Remove common messy patterns
        clean = re.sub(r'^[0-9]+-', '', clean)  # Remove leading numbers
        clean = re.sub(r'[0-9a-f]{8,}', '', clean)  # Remove UUID-like strings
        clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', clean)  # Replace special chars
        clean = re.sub(r'\s+', ' ', clean)  # Normalize whitespace
        clean = clean.strip()
        
        return clean

    def _analyze_content_structure_improved(self, content: str) -> Dict[str, float]:
        """Improved content structure analysis."""
        structure_indicators = {
            'meeting': {
                'agenda_section': r'#+\s*agenda',
                'attendees_section': r'#+\s*attendees',
                'action_items': r'#+\s*action\s+items',
                'time_mentions': r'\d{1,2}:\d{2}',
                'notes_from': r'notes?\s+from'
            },
            'project': {
                'goals_section': r'#+\s*(goals|objectives)',
                'timeline_section': r'#+\s*(timeline|schedule)',
                'status_section': r'#+\s*status',
                'milestone_mentions': r'milestone|deadline|deliverable',
                'implementation': r'implementation|development|feature'
            },
            'decision': {
                'pros_cons': r'#+\s*(pros|cons|alternatives)',
                'decision_mentions': r'decided|chose|recommendation',
                'rationale_section': r'#+\s*(rationale|reasoning)'
            },
            'template': {
                'template_vars': r'\{\{[^}]+\}\}',
                'checklist_items': r'- \[ \]',
                'steps_section': r'#+\s*steps'
            },
            'daily_note': {
                'date_mentions': r'today|yesterday|tomorrow',
                'reflection_section': r'#+\s*reflection',
                'daily_activities': r'#+\s*(notes|tasks|activities)'
            },
            'technical': {
                'code_blocks': r'```',
                'function_defs': r'function|def\s+\w+',
                'api_mentions': r'api|endpoint|request|response',
                'bug_mentions': r'bug|fix|error|issue'
            }
        }
        
        scores = {}
        for content_type, indicators in structure_indicators.items():
            score = 0
            for indicator, pattern in indicators.items():
                if re.search(pattern, content, re.IGNORECASE):
                    score += 0.15  # Lower threshold
            scores[content_type] = min(score, 1.0)
        
        return scores

    def _analyze_semantic_content_improved(self, content: str) -> Dict[str, float]:
        """More lenient semantic content analysis."""
        content_lower = content.lower()
        scores = {}
        
        for content_type, config in self.content_patterns.items():
            score = 0
            total_indicators = 0
            
            # Check keywords (more lenient)
            for keyword in config['keywords']:
                if keyword in content_lower:
                    score += 0.15  # Higher weight
                total_indicators += 1
            
            # Check regex patterns
            for pattern in config['patterns']:
                if re.search(pattern, content_lower):
                    score += 0.2  # Higher weight
                total_indicators += 1
            
            # Check structure indicators
            for indicator in config['structure_indicators']:
                if indicator in content_lower:
                    score += 0.1
                total_indicators += 1
            
            # More lenient scoring
            if total_indicators > 0:
                normalized_score = min(score / max(total_indicators, 1), 1.0)
                scores[content_type] = normalized_score * config['weight']
        
        return scores

    def _analyze_context_improved(self, file_path: str, content: str) -> Dict[str, float]:
        """Improved context analysis."""
        context_scores = {}
        
        # Analyze folder structure
        path_parts = [part.lower() for part in file_path.split(os.sep)]
        
        # More comprehensive folder-based indicators
        folder_indicators = {
            'meeting': ['meeting', 'standup', 'calls', 'sync'],
            'project': ['project', 'projects', 'work', 'development'],
            'template': ['template', 'templates', 'guides'],
            'daily_note': ['daily', 'journal', 'notes', 'log'],
            'area': ['area', 'areas', 'responsibility'],
            'resource': ['resource', 'resources', 'reference', 'knowledge'],
            'technical': ['code', 'technical', 'development', 'software']
        }
        
        for content_type, indicators in folder_indicators.items():
            if any(word in path_parts for word in indicators):
                context_scores[content_type] = 0.5  # Higher context weight
        
        # Analyze frontmatter if present
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            if 'type' in frontmatter:
                context_scores[frontmatter['type']] = 0.8
            if 'tags' in frontmatter:
                for tag in frontmatter['tags']:
                    if tag in ['meeting', 'project', 'decision', 'template', 'daily', 'area', 'resource', 'technical']:
                        context_scores[tag] = 0.4
        
        return context_scores

    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from content."""
        if not content.startswith("---\n"):
            return None
        
        try:
            end_marker = content.find("\n---\n", 4)
            if end_marker == -1:
                return None
            
            frontmatter_yaml = content[4:end_marker]
            return yaml.safe_load(frontmatter_yaml) or {}
        except Exception:
            return None

    def _combine_scores_improved(self, filename_score: Dict[str, float], 
                                structure_score: Dict[str, float],
                                semantic_score: Dict[str, float], 
                                context_score: Dict[str, float]) -> Dict[str, float]:
        """Improved score combination with adjusted weights."""
        all_types = set(list(filename_score.keys()) + list(structure_score.keys()) + 
                       list(semantic_score.keys()) + list(context_score.keys()))
        
        combined_scores = {}
        for content_type in all_types:
            # Adjusted weights for better real-world performance
            score = (
                filename_score.get(content_type, 0) * 0.3 +  # Higher filename weight
                structure_score.get(content_type, 0) * 0.25 +  # Lower structure weight
                semantic_score.get(content_type, 0) * 0.35 +  # Higher semantic weight
                context_score.get(content_type, 0) * 0.1   # Lower context weight
            )
            if score > 0.05:  # Much lower threshold
                combined_scores[content_type] = min(score, 1.0)
        
        return combined_scores

    def get_content_tags(self, content_type: str, analysis: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate tags with better real-world tuning."""
        base_tags = {
            'daily_note': ['daily', 'daily-note', 'journal'],
            'meeting': ['meeting', 'collaboration'],
            'project': ['project', 'active'],
            'decision': ['decision', 'important'],
            'template': ['template', 'reusable'],
            'area': ['area', 'ongoing'],
            'resource': ['resource', 'reference'],
            'technical': ['technical', 'code']
        }
        
        tags = base_tags.get(content_type, ['resource'])
        
        # More lenient confidence-based tags
        if analysis and analysis.get('confidence', 0) > 0.3:
            tags.append('medium-confidence')
        elif analysis and analysis.get('confidence', 0) < 0.2:
            tags.append('needs-review')
        
        # Add secondary type tags
        if analysis and analysis.get('secondary_types'):
            for secondary_type in analysis['secondary_types']:
                tags.append(f'{secondary_type}-related')
        
        return list(set(tags))

    def generate_rich_metadata(self, content_type: str, content: str, file_path: str, 
                             analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate metadata with better real-world tuning."""
        metadata = {
            'content_type': content_type,
            'confidence': analysis.get('confidence', 0.0) if analysis else 0.0,
            'created': datetime.now().isoformat(),
            'status': 'active',
            'source_file': file_path
        }
        
        # Add content quality indicators
        metadata.update({
            'word_count': len(content.split()),
            'character_count': len(content),
            'reading_time': max(1, round(len(content.split()) / 200)),
            'has_structure': bool(re.search(r'#+\s+', content)),
            'has_tasks': bool(re.search(r'- \[ \]', content)),
            'has_links': bool(re.search(r'\[\[.*?\]\]', content)),
            'has_urls': bool(re.search(r'https?://', content)),
            'task_count': len(re.findall(r'- \[ \]', content)),
            'completed_task_count': len(re.findall(r'- \[x\]', content)),
            'link_count': len(re.findall(r'\[\[.*?\]\]', content)),
            'heading_count': len(re.findall(r'#+\s+', content))
        })
        
        return metadata
