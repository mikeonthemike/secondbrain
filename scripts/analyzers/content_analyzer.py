"""
Enhanced content type analyzer for intelligent file categorization.

Analyzes file content, filenames, structure, and context to determine the appropriate
content type with confidence scoring and rich metadata generation.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import yaml


class ContentAnalyzer:
    """Enhanced content analyzer with multi-layer classification and confidence scoring."""

    def __init__(self):
        """Initialize the enhanced content analyzer with comprehensive detection patterns."""
        # Enhanced content patterns with confidence weights and structure indicators
        self.content_patterns = {
            'meeting': {
                'keywords': ['meeting', 'call', 'conference', 'standup', 'review', 'agenda', 'minutes', 'attendees'],
                'patterns': [r'\d{1,2}:\d{2}', r'am|pm', r'agenda', r'minutes', r'attendees', r'action items'],
                'weight': 0.8,
                'structure_indicators': ['agenda', 'attendees', 'action items', 'next steps']
            },
            'project': {
                'keywords': ['project', 'milestone', 'deliverable', 'sprint', 'phase', 'deadline', 'timeline'],
                'patterns': [r'status', r'update', r'progress', r'deadline', r'timeline', r'roadmap'],
                'weight': 0.9,
                'structure_indicators': ['goals', 'objectives', 'timeline', 'deliverables']
            },
            'decision': {
                'keywords': ['decision', 'decided', 'chose', 'option', 'conclusion', 'recommendation'],
                'patterns': [r'decided', r'chose', r'option', r'conclusion', r'final', r'approved'],
                'weight': 0.7,
                'structure_indicators': ['pros', 'cons', 'alternatives', 'rationale']
            },
            'template': {
                'keywords': ['template', 'checklist', 'guide', 'framework', 'process'],
                'patterns': [r'template', r'checklist', r'guide', r'framework', r'process'],
                'weight': 0.6,
                'structure_indicators': ['{{', '}}', 'checklist', 'steps']
            },
            'daily_note': {
                'keywords': ['daily', 'journal', 'log', 'entry', 'today', 'reflection'],
                'patterns': [r'\d{4}-\d{2}-\d{2}', r'today', r'daily', r'journal', r'reflection'],
                'weight': 0.9,
                'structure_indicators': ['today', 'yesterday', 'tomorrow', 'reflection']
            },
            'area': {
                'keywords': ['area', 'responsibility', 'ongoing', 'process', 'standard'],
                'patterns': [r'ongoing', r'process', r'standard', r'responsibility'],
                'weight': 0.6,
                'structure_indicators': ['ongoing', 'process', 'standard', 'responsibility']
            },
            'resource': {
                'keywords': ['note', 'idea', 'thought', 'reference', 'study', 'article'],
                'patterns': [r'note', r'idea', r'thought', r'reference', r'study'],
                'weight': 0.5,
                'structure_indicators': ['reference', 'study', 'research']
            }
        }

    def detect_content_type(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Enhanced content type detection with confidence scoring and context awareness.
        
        Args:
            file_path: Path to the file
            content: File content to analyze
            
        Returns:
            Dictionary with detailed analysis including primary type, confidence, and indicators
        """
        analysis = {
            'primary_type': 'resource',
            'confidence': 0.0,
            'secondary_types': [],
            'content_indicators': [],
            'filename_indicators': [],
            'context_indicators': [],
            'structure_indicators': []
        }
        
        # Layer 1: Filename analysis
        filename_score = self._analyze_filename(file_path)
        
        # Layer 2: Content structure analysis
        structure_score = self._analyze_content_structure(content)
        
        # Layer 3: Semantic content analysis
        semantic_score = self._analyze_semantic_content(content)
        
        # Layer 4: Context analysis (folder location, metadata)
        context_score = self._analyze_context(file_path, content)
        
        # Combine scores with weights
        final_score = self._combine_scores(filename_score, structure_score, 
                                         semantic_score, context_score)
        
        # Determine primary type and confidence
        if final_score:
            analysis['primary_type'] = max(final_score, key=final_score.get)
            analysis['confidence'] = final_score[analysis['primary_type']]
            
            # Add secondary types (other high-scoring types)
            sorted_types = sorted(final_score.items(), key=lambda x: x[1], reverse=True)
            analysis['secondary_types'] = [t[0] for t in sorted_types[1:3] if t[1] > 0.3]
        
        return analysis

    def _analyze_filename(self, file_path: str) -> Dict[str, float]:
        """Analyze filename for content type indicators."""
        filename = os.path.basename(file_path).lower()
        
        # Clean up messy filenames
        clean_name = self._clean_filename(filename)
        
        # Detect patterns
        patterns = {
            'meeting': r'(meeting|call|standup|review|agenda)',
            'project': r'(project|milestone|deliverable|sprint)',
            'template': r'(template|checklist|guide|framework)',
            'daily_note': r'(\d{4}-\d{2}-\d{2}|daily|journal)',
            'decision': r'(decision|chose|option|conclusion)',
            'area': r'(area|responsibility|process)',
            'resource': r'(note|idea|reference|study)'
        }
        
        # Score based on filename patterns
        scores = {}
        for content_type, pattern in patterns.items():
            if re.search(pattern, clean_name):
                scores[content_type] = 0.8  # High confidence from filename
        
        return scores

    def _clean_filename(self, filename: str) -> str:
        """Clean up messy filenames for better analysis."""
        # Remove file extension
        clean = os.path.splitext(filename)[0]
        
        # Remove common messy patterns
        clean = re.sub(r'[0-9]+-', '', clean)  # Remove leading numbers
        clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', clean)  # Replace special chars with spaces
        clean = re.sub(r'\s+', ' ', clean)  # Normalize whitespace
        clean = clean.strip()
        
        return clean

    def _analyze_content_structure(self, content: str) -> Dict[str, float]:
        """Analyze content structure for type indicators."""
        structure_indicators = {
            'meeting': {
                'agenda_section': r'#+\s*agenda',
                'attendees_section': r'#+\s*attendees',
                'action_items': r'#+\s*action\s+items',
                'time_mentions': r'\d{1,2}:\d{2}'
            },
            'project': {
                'goals_section': r'#+\s*(goals|objectives)',
                'timeline_section': r'#+\s*(timeline|schedule)',
                'status_section': r'#+\s*status',
                'milestone_mentions': r'milestone|deadline|deliverable'
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
            }
        }
        
        scores = {}
        for content_type, indicators in structure_indicators.items():
            score = 0
            for indicator, pattern in indicators.items():
                if re.search(pattern, content, re.IGNORECASE):
                    score += 0.2
            scores[content_type] = min(score, 1.0)
        
        return scores

    def _analyze_semantic_content(self, content: str) -> Dict[str, float]:
        """Analyze semantic content using keyword and pattern matching."""
        content_lower = content.lower()
        scores = {}
        
        for content_type, config in self.content_patterns.items():
            score = 0
            total_indicators = 0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in content_lower:
                    score += 0.1
                total_indicators += 1
            
            # Check regex patterns
            for pattern in config['patterns']:
                if re.search(pattern, content_lower):
                    score += 0.15
                total_indicators += 1
            
            # Check structure indicators
            for indicator in config['structure_indicators']:
                if indicator in content_lower:
                    score += 0.1
                total_indicators += 1
            
            # Normalize score and apply weight
            if total_indicators > 0:
                normalized_score = min(score / total_indicators, 1.0)
                scores[content_type] = normalized_score * config['weight']
        
        return scores

    def _analyze_context(self, file_path: str, content: str) -> Dict[str, float]:
        """Analyze context (folder location, metadata) for classification."""
        context_scores = {}
        
        # Analyze folder structure
        path_parts = [part.lower() for part in file_path.split(os.sep)]
        
        # Folder-based indicators
        if any(word in path_parts for word in ['meeting', 'standup', 'calls']):
            context_scores['meeting'] = 0.7
        if any(word in path_parts for word in ['project', 'projects']):
            context_scores['project'] = 0.6
        if any(word in path_parts for word in ['template', 'templates']):
            context_scores['template'] = 0.8
        if any(word in path_parts for word in ['daily', 'journal', 'notes']):
            context_scores['daily_note'] = 0.7
        if any(word in path_parts for word in ['area', 'areas']):
            context_scores['area'] = 0.6
        if any(word in path_parts for word in ['resource', 'resources']):
            context_scores['resource'] = 0.5
        
        # Analyze frontmatter if present
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            if 'type' in frontmatter:
                context_scores[frontmatter['type']] = 0.9
            if 'tags' in frontmatter:
                for tag in frontmatter['tags']:
                    if tag in ['meeting', 'project', 'decision', 'template', 'daily', 'area', 'resource']:
                        context_scores[tag] = 0.6
        
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

    def _combine_scores(self, filename_score: Dict[str, float], 
                       structure_score: Dict[str, float],
                       semantic_score: Dict[str, float], 
                       context_score: Dict[str, float]) -> Dict[str, float]:
        """Combine all scores with appropriate weights."""
        all_types = set(list(filename_score.keys()) + list(structure_score.keys()) + 
                       list(semantic_score.keys()) + list(context_score.keys()))
        
        combined_scores = {}
        for content_type in all_types:
            # Weighted combination
            score = (
                filename_score.get(content_type, 0) * 0.2 +
                structure_score.get(content_type, 0) * 0.3 +
                semantic_score.get(content_type, 0) * 0.4 +
                context_score.get(content_type, 0) * 0.1
            )
            if score > 0:
                combined_scores[content_type] = min(score, 1.0)
        
        return combined_scores

    def determine_folder_type(self, content_type: str, filename: str, confidence: float = 0.5) -> str:
        """
        Enhanced folder type determination with confidence-based logic.

        Args:
            content_type: Detected content type
            filename: Original filename
            confidence: Confidence score for the classification

        Returns:
            Folder type for organization
        """
        # High confidence classifications
        if confidence > 0.8:
            if content_type == 'daily_note':
                return 'daily_notes'
            elif content_type == 'meeting':
                return 'projects'  # Meetings are usually project-related
            elif content_type == 'project':
                return 'projects'
            elif content_type == 'decision':
                return 'projects'  # Decisions are usually project-related
            elif content_type == 'template':
                return 'templates'
            elif content_type == 'area':
                return 'areas'
        
        # Medium confidence - use filename and content hints
        elif confidence > 0.5:
            # Check filename for additional clues
            if any(word in filename.lower() for word in ['meeting', 'call', 'standup']):
                return 'projects'
            elif any(word in filename.lower() for word in ['template', 'checklist']):
                return 'templates'
            elif re.search(r'\d{4}-\d{2}-\d{2}', filename):
                return 'daily_notes'
            elif any(word in filename.lower() for word in ['area', 'responsibility']):
                return 'areas'
        
        # Low confidence - default to resources
        return 'resources'

    def get_content_tags(self, content_type: str, analysis: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Enhanced tag generation based on content type and analysis.

        Args:
            content_type: The detected content type
            analysis: Full analysis results for additional context

        Returns:
            List of intelligent tags for the content type
        """
        base_tags = {
            'daily_note': ['daily', 'daily-note', 'journal'],
            'meeting': ['meeting', 'collaboration'],
            'project': ['project', 'active'],
            'decision': ['decision', 'important'],
            'template': ['template', 'reusable'],
            'area': ['area', 'ongoing'],
            'resource': ['resource', 'reference']
        }
        
        tags = base_tags.get(content_type, ['resource'])
        
        # Add confidence-based tags
        if analysis and analysis.get('confidence', 0) > 0.8:
            tags.append('high-confidence')
        elif analysis and analysis.get('confidence', 0) < 0.5:
            tags.append('needs-review')
        
        # Add secondary type tags
        if analysis and analysis.get('secondary_types'):
            for secondary_type in analysis['secondary_types']:
                tags.append(f'{secondary_type}-related')
        
        return list(set(tags))  # Remove duplicates

    def generate_rich_metadata(self, content_type: str, content: str, file_path: str, 
                             analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate rich metadata for frontmatter."""
        metadata = {
            'content_type': content_type,
            'confidence': analysis.get('confidence', 0.0) if analysis else 0.0,
            'created': datetime.now().isoformat(),
            'status': 'active',
            'source_file': file_path
        }
        
        # Add type-specific metadata
        if content_type == 'meeting':
            metadata.update({
                'meeting_type': self._detect_meeting_type(content),
                'attendees': self._extract_attendees(content),
                'action_items_count': len(re.findall(r'- \[ \]', content)),
                'has_agenda': bool(re.search(r'#+\s*agenda', content, re.IGNORECASE))
            })
        elif content_type == 'project':
            metadata.update({
                'project_phase': self._detect_project_phase(content),
                'deadline': self._extract_deadline(content),
                'stakeholders': self._extract_stakeholders(content),
                'has_timeline': bool(re.search(r'timeline|schedule|roadmap', content, re.IGNORECASE))
            })
        elif content_type == 'decision':
            metadata.update({
                'decision_status': self._detect_decision_status(content),
                'alternatives_considered': self._count_alternatives(content),
                'rationale_strength': self._assess_rationale_strength(content)
            })
        elif content_type == 'template':
            metadata.update({
                'template_type': self._detect_template_type(content),
                'has_variables': bool(re.search(r'\{\{[^}]+\}\}', content)),
                'complexity': self._assess_template_complexity(content)
            })
        
        # Add content quality indicators
        metadata.update({
            'word_count': len(content.split()),
            'has_structure': bool(re.search(r'#+\s+', content)),
            'has_links': bool(re.search(r'\[\[.*?\]\]', content)),
            'has_tasks': bool(re.search(r'- \[ \]', content))
        })
        
        return metadata

    def _detect_meeting_type(self, content: str) -> str:
        """Detect specific type of meeting."""
        content_lower = content.lower()
        if 'standup' in content_lower or 'daily' in content_lower:
            return 'standup'
        elif 'review' in content_lower:
            return 'review'
        elif 'planning' in content_lower or 'sprint' in content_lower:
            return 'planning'
        else:
            return 'general'

    def _extract_attendees(self, content: str) -> List[str]:
        """Extract attendee names from content."""
        attendees = []
        # Look for attendees section
        attendees_match = re.search(r'#+\s*attendees?\s*\n(.*?)(?:\n#|\Z)', content, re.IGNORECASE | re.DOTALL)
        if attendees_match:
            attendees_text = attendees_match.group(1)
            # Extract names (simple pattern)
            names = re.findall(r'[-*]\s*([A-Za-z\s]+)', attendees_text)
            attendees.extend([name.strip() for name in names])
        return attendees

    def _detect_project_phase(self, content: str) -> str:
        """Detect project phase from content."""
        content_lower = content.lower()
        if any(word in content_lower for word in ['planning', 'kickoff', 'initiation']):
            return 'planning'
        elif any(word in content_lower for word in ['development', 'implementation', 'building']):
            return 'development'
        elif any(word in content_lower for word in ['testing', 'qa', 'review']):
            return 'testing'
        elif any(word in content_lower for word in ['deployment', 'launch', 'release']):
            return 'deployment'
        else:
            return 'unknown'

    def _extract_deadline(self, content: str) -> Optional[str]:
        """Extract deadline from content."""
        # Look for date patterns
        date_patterns = [
            r'deadline[:\s]+(\d{4}-\d{2}-\d{2})',
            r'due[:\s]+(\d{4}-\d{2}-\d{2})',
            r'by[:\s]+(\d{4}-\d{2}-\d{2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_stakeholders(self, content: str) -> List[str]:
        """Extract stakeholder names from content."""
        stakeholders = []
        # Look for stakeholder mentions
        stakeholder_patterns = [
            r'stakeholders?[:\s]*(.*?)(?:\n|$)',
            r'team[:\s]*(.*?)(?:\n|$)',
            r'@([A-Za-z\s]+)'
        ]
        for pattern in stakeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    stakeholders.extend([name.strip() for name in match.split(',')])
        return list(set(stakeholders))

    def _detect_decision_status(self, content: str) -> str:
        """Detect decision status."""
        content_lower = content.lower()
        if any(word in content_lower for word in ['decided', 'approved', 'final']):
            return 'final'
        elif any(word in content_lower for word in ['pending', 'under review']):
            return 'pending'
        elif any(word in content_lower for word in ['draft', 'proposed']):
            return 'draft'
        else:
            return 'unknown'

    def _count_alternatives(self, content: str) -> int:
        """Count alternatives considered."""
        alternatives = re.findall(r'alternative|option|choice', content, re.IGNORECASE)
        return len(alternatives)

    def _assess_rationale_strength(self, content: str) -> str:
        """Assess strength of decision rationale."""
        rationale_indicators = ['because', 'since', 'therefore', 'rationale', 'reasoning']
        count = sum(1 for indicator in rationale_indicators if indicator in content.lower())
        if count >= 3:
            return 'strong'
        elif count >= 1:
            return 'moderate'
        else:
            return 'weak'

    def _detect_template_type(self, content: str) -> str:
        """Detect template type."""
        content_lower = content.lower()
        if 'checklist' in content_lower:
            return 'checklist'
        elif 'process' in content_lower:
            return 'process'
        elif 'guide' in content_lower:
            return 'guide'
        else:
            return 'general'

    def _assess_template_complexity(self, content: str) -> str:
        """Assess template complexity."""
        variable_count = len(re.findall(r'\{\{[^}]+\}\}', content))
        if variable_count > 5:
            return 'complex'
        elif variable_count > 2:
            return 'moderate'
        else:
            return 'simple'
