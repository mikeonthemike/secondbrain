"""
Core vault management for Obsidian Second Brain system.

Handles note creation, organization, and basic vault operations.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import yaml

try:
    from .config_manager import VaultConfig
except ImportError:
    from config_manager import VaultConfig


class VaultManager:
    """Manages Obsidian vault operations and note management."""
    
    def __init__(self, config: Optional[VaultConfig] = None):
        """
        Initialize vault manager.
        
        Args:
            config: VaultConfig instance. If None, creates a new one.
        """
        self.config = config or VaultConfig()
        self.vault_path = self.config.get_vault_path()
        
        if not self.vault_path:
            raise ValueError("No vault path configured. Run setup first.")
    
    def create_note(self, 
                   title: str, 
                   content: str = "", 
                   folder_type: str = "inbox",
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   template: Optional[str] = None) -> Optional[str]:
        """
        Create a new note in the vault.
        
        Args:
            title: Note title
            content: Note content
            folder_type: Type of folder (inbox, projects, areas, resources, archive)
            tags: List of tags to add
            metadata: Additional metadata for frontmatter
            template: Template to use for the note
            
        Returns:
            Path to created note, or None if failed
        """
        try:
            # Get folder path
            folder_path = self.config.get_folder_path(folder_type)
            if not folder_path:
                print(f"Invalid folder type: {folder_type}")
                return None
            
            # Create filename from title
            filename = self._title_to_filename(title)
            file_path = os.path.join(folder_path, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                print(f"Note already exists: {file_path}")
                return file_path
            
            # Prepare content
            if template:
                content = self._apply_template(template, title, content, tags, metadata)
            else:
                content = self._format_note_content(title, content, tags, metadata)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Created note: {filename}")
            return file_path
            
        except Exception as e:
            print(f"✗ Error creating note: {e}")
            return None
    
    def _title_to_filename(self, title: str) -> str:
        """Convert title to valid filename."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with hyphens
        filename = re.sub(r'\s+', '-', filename)
        # Remove multiple hyphens
        filename = re.sub(r'-+', '-', filename)
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        # Add .md extension
        return f"{filename}.md"
    
    def _format_note_content(self, 
                           title: str, 
                           content: str, 
                           tags: Optional[List[str]] = None,
                           metadata: Optional[Dict[str, Any]] = None,
                           content_analysis: Optional[Dict[str, Any]] = None) -> str:
        """Enhanced note content formatting with rich frontmatter."""
        # Generate comprehensive frontmatter
        frontmatter = self._generate_enhanced_frontmatter(
            title, content, tags, metadata, content_analysis
        )
        
        # Format as YAML with proper ordering
        yaml_content = self._format_yaml_frontmatter(frontmatter)
        
        # Combine frontmatter and content
        return f"---\n{yaml_content}---\n\n{content}\n"

    def _generate_enhanced_frontmatter(self, 
                                     title: str, 
                                     content: str, 
                                     tags: Optional[List[str]] = None,
                                     metadata: Optional[Dict[str, Any]] = None,
                                     content_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive frontmatter with intelligent metadata."""
        now = datetime.now()
        
        # Base frontmatter structure
        frontmatter = {
            # Core identification
            "title": title,
            "id": self._generate_note_id(title, now),
            
            # Timestamps
            "created": now.isoformat(),
            "modified": now.isoformat(),
            "created_date": now.strftime("%Y-%m-%d"),
            "created_time": now.strftime("%H:%M"),
            
            # Status and workflow
            "status": "active",
            "type": "note",
            "priority": "medium",
            
            # Content analysis
            "word_count": len(content.split()),
            "character_count": len(content),
            "reading_time": self._calculate_reading_time(content),
        }
        
        # Add content analysis if available
        if content_analysis:
            frontmatter.update({
                "content_type": content_analysis.get('primary_type', 'resource'),
                "confidence": content_analysis.get('confidence', 0.0),
                "secondary_types": content_analysis.get('secondary_types', []),
                "analysis_timestamp": now.isoformat()
            })
            
            # Add type-specific metadata
            self._add_type_specific_metadata(frontmatter, content_analysis, content)
        
        # Add intelligent tags
        if tags:
            frontmatter["tags"] = self._enhance_tags(tags, content_analysis, content)
        else:
            frontmatter["tags"] = self._generate_intelligent_tags(content, content_analysis)
        
        # Add content quality indicators
        frontmatter.update(self._assess_content_quality(content))
        
        # Add organizational metadata
        frontmatter.update(self._generate_organizational_metadata(content, title))
        
        # Add user-provided metadata
        if metadata:
            frontmatter.update(metadata)
        
        # Add Obsidian-specific metadata
        frontmatter.update(self._generate_obsidian_metadata(content, title))
        
        return frontmatter

    def _generate_note_id(self, title: str, timestamp: datetime) -> str:
        """Generate a unique note ID."""
        # Create a readable ID from title and timestamp
        clean_title = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower())
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')
        return f"{clean_title}-{timestamp.strftime('%Y%m%d-%H%M')}"

    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        words = len(content.split())
        # Average reading speed: 200 words per minute
        return max(1, round(words / 200))

    def _add_type_specific_metadata(self, frontmatter: Dict[str, Any], 
                                  content_analysis: Dict[str, Any], 
                                  content: str) -> None:
        """Add metadata specific to content type."""
        content_type = content_analysis.get('primary_type', 'resource')
        
        if content_type == 'meeting':
            frontmatter.update({
                "meeting_type": self._detect_meeting_type(content),
                "attendees": self._extract_attendees(content),
                "action_items_count": len(re.findall(r'- \[ \]', content)),
                "has_agenda": bool(re.search(r'#+\s*agenda', content, re.IGNORECASE)),
                "meeting_date": self._extract_meeting_date(content),
                "duration": self._estimate_meeting_duration(content)
            })
        elif content_type == 'project':
            frontmatter.update({
                "project_phase": self._detect_project_phase(content),
                "deadline": self._extract_deadline(content),
                "stakeholders": self._extract_stakeholders(content),
                "has_timeline": bool(re.search(r'timeline|schedule|roadmap', content, re.IGNORECASE)),
                "project_status": self._assess_project_status(content),
                "completion_percentage": self._estimate_completion(content)
            })
        elif content_type == 'decision':
            frontmatter.update({
                "decision_status": self._detect_decision_status(content),
                "alternatives_considered": self._count_alternatives(content),
                "rationale_strength": self._assess_rationale_strength(content),
                "decision_date": self._extract_decision_date(content),
                "impact_level": self._assess_decision_impact(content)
            })
        elif content_type == 'template':
            frontmatter.update({
                "template_type": self._detect_template_type(content),
                "has_variables": bool(re.search(r'\{\{[^}]+\}\}', content)),
                "complexity": self._assess_template_complexity(content),
                "usage_count": 0,  # Will be updated as template is used
                "last_used": None
            })
        elif content_type == 'daily_note':
            frontmatter.update({
                "date": self._extract_note_date(content),
                "mood": self._detect_mood(content),
                "key_events": self._extract_key_events(content),
                "reflection_quality": self._assess_reflection_quality(content),
                "productivity_score": self._assess_productivity(content)
            })

    def _enhance_tags(self, base_tags: List[str], 
                     content_analysis: Optional[Dict[str, Any]], 
                     content: str) -> List[str]:
        """Enhance tags with intelligent additions."""
        enhanced_tags = list(base_tags)  # Start with base tags
        
        # Add confidence-based tags
        if content_analysis:
            confidence = content_analysis.get('confidence', 0.0)
            if confidence > 0.8:
                enhanced_tags.append('high-confidence')
            elif confidence < 0.5:
                enhanced_tags.append('needs-review')
            
            # Add secondary type tags
            for secondary_type in content_analysis.get('secondary_types', []):
                enhanced_tags.append(f'{secondary_type}-related')
        
        # Add content-based tags
        enhanced_tags.extend(self._generate_content_based_tags(content))
        
        # Add temporal tags
        enhanced_tags.extend(self._generate_temporal_tags())
        
        # Add quality tags
        enhanced_tags.extend(self._generate_quality_tags(content))
        
        return list(set(enhanced_tags))  # Remove duplicates

    def _generate_intelligent_tags(self, content: str, 
                                 content_analysis: Optional[Dict[str, Any]]) -> List[str]:
        """Generate intelligent tags when none are provided."""
        tags = []
        
        # Base tags from content analysis
        if content_analysis:
            content_type = content_analysis.get('primary_type', 'resource')
            tags.append(content_type)
            
            # Add confidence tag
            confidence = content_analysis.get('confidence', 0.0)
            if confidence > 0.8:
                tags.append('high-confidence')
            elif confidence < 0.5:
                tags.append('needs-review')
        
        # Content-based tags
        tags.extend(self._generate_content_based_tags(content))
        
        # Temporal tags
        tags.extend(self._generate_temporal_tags())
        
        # Quality tags
        tags.extend(self._generate_quality_tags(content))
        
        return list(set(tags))

    def _generate_content_based_tags(self, content: str) -> List[str]:
        """Generate tags based on content analysis."""
        tags = []
        content_lower = content.lower()
        
        # Topic-based tags
        topic_patterns = {
            'work': ['work', 'job', 'career', 'professional', 'business'],
            'personal': ['personal', 'family', 'health', 'fitness', 'hobby'],
            'technical': ['code', 'programming', 'software', 'technical', 'api'],
            'creative': ['creative', 'design', 'art', 'writing', 'ideas'],
            'learning': ['learn', 'study', 'research', 'education', 'course'],
            'planning': ['plan', 'strategy', 'goal', 'objective', 'roadmap'],
            'review': ['review', 'retrospective', 'analysis', 'evaluation'],
            'urgent': ['urgent', 'asap', 'critical', 'emergency', 'deadline']
        }
        
        for tag, patterns in topic_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                tags.append(tag)
        
        # Structure-based tags
        if re.search(r'#+\s+', content):
            tags.append('structured')
        if re.search(r'- \[ \]', content):
            tags.append('has-tasks')
        if re.search(r'\[\[.*?\]\]', content):
            tags.append('has-links')
        if re.search(r'https?://', content):
            tags.append('has-urls')
        
        return tags

    def _generate_temporal_tags(self) -> List[str]:
        """Generate temporal tags based on current date."""
        now = datetime.now()
        tags = []
        
        # Year and month
        tags.append(f'year-{now.year}')
        tags.append(f'month-{now.strftime("%B").lower()}')
        
        # Quarter
        quarter = (now.month - 1) // 3 + 1
        tags.append(f'q{quarter}-{now.year}')
        
        # Day of week
        tags.append(f'day-{now.strftime("%A").lower()}')
        
        # Season (approximate)
        if now.month in [12, 1, 2]:
            tags.append('winter')
        elif now.month in [3, 4, 5]:
            tags.append('spring')
        elif now.month in [6, 7, 8]:
            tags.append('summer')
        else:
            tags.append('autumn')
        
        return tags

    def _generate_quality_tags(self, content: str) -> List[str]:
        """Generate quality-based tags."""
        tags = []
        
        word_count = len(content.split())
        if word_count > 1000:
            tags.append('long-form')
        elif word_count < 100:
            tags.append('brief')
        
        if re.search(r'#+\s+', content):
            tags.append('well-structured')
        
        if len(re.findall(r'- \[ \]', content)) > 5:
            tags.append('task-heavy')
        
        if len(re.findall(r'\[\[.*?\]\]', content)) > 3:
            tags.append('well-linked')
        
        return tags

    def _assess_content_quality(self, content: str) -> Dict[str, Any]:
        """Assess content quality and return metrics."""
        return {
            "has_structure": bool(re.search(r'#+\s+', content)),
            "has_tasks": bool(re.search(r'- \[ \]', content)),
            "has_links": bool(re.search(r'\[\[.*?\]\]', content)),
            "has_urls": bool(re.search(r'https?://', content)),
            "has_images": bool(re.search(r'!\[.*?\]\(.*?\)', content)),
            "has_code": bool(re.search(r'```', content)),
            "task_count": len(re.findall(r'- \[ \]', content)),
            "completed_task_count": len(re.findall(r'- \[x\]', content)),
            "link_count": len(re.findall(r'\[\[.*?\]\]', content)),
            "heading_count": len(re.findall(r'#+\s+', content)),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "readability_score": self._calculate_readability_score(content)
        }

    def _generate_organizational_metadata(self, content: str, title: str) -> Dict[str, Any]:
        """Generate organizational metadata."""
        return {
            "folder_suggestion": self._suggest_folder(content, title),
            "moc_candidates": self._find_moc_candidates(content),
            "related_topics": self._extract_related_topics(content),
            "key_phrases": self._extract_key_phrases(content),
            "summary": self._generate_summary(content)
        }

    def _generate_obsidian_metadata(self, content: str, title: str) -> Dict[str, Any]:
        """Generate Obsidian-specific metadata."""
        return {
            "aliases": self._generate_aliases(title),
            "cssclass": self._suggest_css_class(content),
            "publish": False,
            "tags": self._extract_existing_tags(content),
            "file_links": self._extract_file_links(content),
            "backlinks": []  # Will be populated by Obsidian
        }

    def _format_yaml_frontmatter(self, frontmatter: Dict[str, Any]) -> str:
        """Format frontmatter as properly ordered YAML."""
        # Define the preferred order for frontmatter fields
        field_order = [
            'title', 'id', 'type', 'content_type', 'status', 'priority',
            'created', 'modified', 'created_date', 'created_time',
            'confidence', 'secondary_types', 'analysis_timestamp',
            'tags', 'aliases', 'cssclass',
            'word_count', 'character_count', 'reading_time',
            'has_structure', 'has_tasks', 'has_links', 'has_urls',
            'readability_score', 'task_count', 'completed_task_count',
            'folder_suggestion', 'moc_candidates', 'related_topics',
            'summary', 'key_phrases'
        ]
        
        # Create ordered frontmatter
        ordered_frontmatter = {}
        
        # Add fields in preferred order
        for field in field_order:
            if field in frontmatter:
                ordered_frontmatter[field] = frontmatter[field]
        
        # Add remaining fields
        for key, value in frontmatter.items():
            if key not in ordered_frontmatter:
                ordered_frontmatter[key] = value
        
        # Format as YAML
        return yaml.dump(ordered_frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _apply_template(self, 
                       template_name: str, 
                       title: str, 
                       content: str,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Apply template to note content."""
        template_path = self.config.get_template_path(template_name)
        if not template_path:
            print(f"Template not found: {template_name}")
            return self._format_note_content(title, content, tags, metadata)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace template variables
            template_content = template_content.replace("{{title}}", title)
            template_content = template_content.replace("{{content}}", content)
            template_content = template_content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            template_content = template_content.replace("{{time}}", datetime.now().strftime("%H:%M"))
            
            if tags:
                tags_str = " ".join([f"#{tag}" for tag in tags])
                template_content = template_content.replace("{{tags}}", tags_str)
            
            return template_content
            
        except Exception as e:
            print(f"Error applying template: {e}")
            return self._format_note_content(title, content, tags, metadata)
    
    def get_note(self, note_path: str) -> Optional[Dict[str, Any]]:
        """
        Read and parse a note file.
        
        Args:
            note_path: Path to the note file
            
        Returns:
            Dictionary with note data, or None if failed
        """
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            frontmatter, body = self._parse_frontmatter(content)
            
            return {
                "path": note_path,
                "frontmatter": frontmatter,
                "content": body,
                "title": frontmatter.get("title", os.path.basename(note_path))
            }
            
        except Exception as e:
            print(f"Error reading note: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from note content."""
        if not content.startswith("---\n"):
            return {}, content
        
        try:
            # Find end of frontmatter
            end_marker = content.find("\n---\n", 4)
            if end_marker == -1:
                return {}, content
            
            frontmatter_yaml = content[4:end_marker]
            body = content[end_marker + 5:]
            
            frontmatter = yaml.safe_load(frontmatter_yaml) or {}
            return frontmatter, body
            
        except Exception as e:
            print(f"Error parsing frontmatter: {e}")
            return {}, content
    
    def update_note(self, note_path: str, updates: Dict[str, Any]) -> bool:
        """
        Update a note with new content or metadata.
        
        Args:
            note_path: Path to the note file
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            note_data = self.get_note(note_path)
            if not note_data:
                return False
            
            # Update frontmatter
            if "frontmatter" in updates:
                note_data["frontmatter"].update(updates["frontmatter"])
            
            # Update content
            if "content" in updates:
                note_data["content"] = updates["content"]
            
            # Update metadata
            note_data["frontmatter"]["updated"] = datetime.now().isoformat()
            
            # Write back to file
            new_content = self._format_note_content(
                note_data["frontmatter"].get("title", ""),
                note_data["content"],
                note_data["frontmatter"].get("tags"),
                note_data["frontmatter"]
            )
            
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Updated note: {os.path.basename(note_path)}")
            return True
            
        except Exception as e:
            print(f"✗ Error updating note: {e}")
            return False
    
    def move_note(self, note_path: str, new_folder_type: str) -> bool:
        """
        Move a note to a different folder.
        
        Args:
            note_path: Current path to the note
            new_folder_type: Type of folder to move to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_folder_path = self.config.get_folder_path(new_folder_type)
            if not new_folder_path:
                print(f"Invalid folder type: {new_folder_type}")
                return False
            
            filename = os.path.basename(note_path)
            new_path = os.path.join(new_folder_path, filename)
            
            # Check if target file already exists
            if os.path.exists(new_path):
                print(f"Target file already exists: {new_path}")
                return False
            
            # Move file
            os.rename(note_path, new_path)
            print(f"✓ Moved note to: {new_folder_type}")
            return True
            
        except Exception as e:
            print(f"✗ Error moving note: {e}")
            return False
    
    def list_notes(self, folder_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List notes in the vault.
        
        Args:
            folder_type: Filter by folder type
            tags: Filter by tags
            
        Returns:
            List of note dictionaries
        """
        notes = []
        
        if folder_type:
            folder_path = self.config.get_folder_path(folder_type)
            if not folder_path:
                return notes
            search_paths = [folder_path]
        else:
            # Search all PARA folders
            search_paths = []
            for folder_name in self.config.config["para_structure"].values():
                folder_path = os.path.join(self.vault_path, folder_name)
                if os.path.exists(folder_path):
                    search_paths.append(folder_path)
        
        for search_path in search_paths:
            for filename in os.listdir(search_path):
                if filename.endswith('.md'):
                    note_path = os.path.join(search_path, filename)
                    note_data = self.get_note(note_path)
                    if note_data:
                        # Filter by tags if specified
                        if tags:
                            note_tags = note_data["frontmatter"].get("tags", [])
                            if not any(tag in note_tags for tag in tags):
                                continue
                        
                        notes.append(note_data)
        
        return notes
    
    def create_daily_note(self, date: Optional[datetime] = None) -> Optional[str]:
        """
        Create a daily note for the specified date.
        
        Args:
            date: Date for the note. If None, uses today.
            
        Returns:
            Path to created note, or None if failed
        """
        if not date:
            date = datetime.now()
        
        title = date.strftime("%Y-%m-%d")
        content = f"# {date.strftime('%A, %B %d, %Y')}\n\n## Notes\n\n## Tasks\n\n## Reflections\n"
        
        return self.create_note(
            title=title,
            content=content,
            folder_type="inbox",  # Will be moved to daily notes folder
            template="daily_note_template.md"
        )
    
    def create_moc(self, topic: str, notes: List[str]) -> Optional[str]:
        """
        Create a Map of Content (MOC) for a topic.
        
        Args:
            topic: Topic name
            notes: List of note titles to include
            
        Returns:
            Path to created MOC, or None if failed
        """
        content = f"# {topic} - Map of Content\n\n"
        
        for note in notes:
            content += f"- [[{note}]]\n"
        
        content += "\n## Related Topics\n\n"
        content += "- \n"
        
        return self.create_note(
            title=f"{topic} - MOC",
            content=content,
            folder_type="mocs",
            tags=["moc", topic.lower()]
        )

    # Enhanced frontmatter helper methods
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
        attendees_match = re.search(r'#+\s*attendees?\s*\n(.*?)(?:\n#|\Z)', content, re.IGNORECASE | re.DOTALL)
        if attendees_match:
            attendees_text = attendees_match.group(1)
            names = re.findall(r'[-*]\s*([A-Za-z\s]+)', attendees_text)
            attendees.extend([name.strip() for name in names])
        return attendees

    def _extract_meeting_date(self, content: str) -> Optional[str]:
        """Extract meeting date from content."""
        date_patterns = [
            r'meeting\s+date[:\s]+(\d{4}-\d{2}-\d{2})',
            r'date[:\s]+(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _estimate_meeting_duration(self, content: str) -> Optional[int]:
        """Estimate meeting duration in minutes."""
        duration_patterns = [
            r'(\d+)\s*minutes?',
            r'(\d+)\s*mins?',
            r'duration[:\s]+(\d+)'
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

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

    def _assess_project_status(self, content: str) -> str:
        """Assess project status."""
        content_lower = content.lower()
        if any(word in content_lower for word in ['completed', 'finished', 'done']):
            return 'completed'
        elif any(word in content_lower for word in ['on hold', 'paused', 'suspended']):
            return 'on_hold'
        elif any(word in content_lower for word in ['active', 'in progress', 'ongoing']):
            return 'active'
        else:
            return 'unknown'

    def _estimate_completion(self, content: str) -> int:
        """Estimate project completion percentage."""
        # Look for completion indicators
        completion_patterns = [
            r'(\d+)%\s*complete',
            r'(\d+)\s*percent',
            r'completion[:\s]+(\d+)'
        ]
        for pattern in completion_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return min(100, max(0, int(match.group(1))))
        return 0

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

    def _extract_decision_date(self, content: str) -> Optional[str]:
        """Extract decision date from content."""
        date_patterns = [
            r'decided[:\s]+(\d{4}-\d{2}-\d{2})',
            r'decision\s+date[:\s]+(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _assess_decision_impact(self, content: str) -> str:
        """Assess decision impact level."""
        content_lower = content.lower()
        if any(word in content_lower for word in ['high', 'critical', 'major', 'significant']):
            return 'high'
        elif any(word in content_lower for word in ['medium', 'moderate', 'some']):
            return 'medium'
        elif any(word in content_lower for word in ['low', 'minor', 'minimal']):
            return 'low'
        else:
            return 'unknown'

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

    def _extract_note_date(self, content: str) -> Optional[str]:
        """Extract date from daily note content."""
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            return date_match.group(1)
        return None

    def _detect_mood(self, content: str) -> Optional[str]:
        """Detect mood from daily note content."""
        mood_indicators = {
            'positive': ['happy', 'great', 'excellent', 'amazing', 'wonderful'],
            'negative': ['sad', 'bad', 'terrible', 'awful', 'disappointed'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'decent']
        }
        content_lower = content.lower()
        for mood, indicators in mood_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return mood
        return None

    def _extract_key_events(self, content: str) -> List[str]:
        """Extract key events from daily note content."""
        events = []
        # Look for bullet points or numbered lists
        event_patterns = [
            r'[-*]\s*(.+)',
            r'\d+\.\s*(.+)'
        ]
        for pattern in event_patterns:
            matches = re.findall(pattern, content)
            events.extend([match.strip() for match in matches[:5]])  # Limit to 5 events
        return events

    def _assess_reflection_quality(self, content: str) -> str:
        """Assess quality of reflection in daily note."""
        reflection_indicators = ['learned', 'realized', 'understood', 'discovered', 'insight']
        count = sum(1 for indicator in reflection_indicators if indicator in content.lower())
        if count >= 3:
            return 'high'
        elif count >= 1:
            return 'medium'
        else:
            return 'low'

    def _assess_productivity(self, content: str) -> int:
        """Assess productivity score from daily note."""
        productivity_indicators = ['completed', 'finished', 'accomplished', 'achieved', 'done']
        count = sum(1 for indicator in productivity_indicators if indicator in content.lower())
        return min(10, count * 2)  # Scale to 1-10

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate simple readability score."""
        words = content.split()
        sentences = len(re.findall(r'[.!?]+', content))
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / sentences
        # Simple scoring: fewer words per sentence = higher readability
        return max(0.0, min(1.0, 1.0 - (avg_words_per_sentence - 10) / 20))

    def _suggest_folder(self, content: str, title: str) -> str:
        """Suggest appropriate folder based on content."""
        content_lower = content.lower()
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['meeting', 'call', 'standup']):
            return 'projects'
        elif any(word in title_lower for word in ['template', 'checklist']):
            return 'templates'
        elif re.search(r'\d{4}-\d{2}-\d{2}', title):
            return 'daily_notes'
        elif any(word in content_lower for word in ['project', 'milestone', 'deadline']):
            return 'projects'
        elif any(word in content_lower for word in ['area', 'responsibility', 'ongoing']):
            return 'areas'
        else:
            return 'resources'

    def _find_moc_candidates(self, content: str) -> List[str]:
        """Find potential MOC (Map of Content) candidates."""
        # Look for topics that might need MOCs
        topics = []
        # Extract headings as potential MOC topics
        headings = re.findall(r'#+\s+(.+)', content)
        for heading in headings:
            if len(heading) > 3 and not heading.lower().startswith(('agenda', 'attendees', 'action')):
                topics.append(heading.strip())
        return topics[:3]  # Return top 3 candidates

    def _extract_related_topics(self, content: str) -> List[str]:
        """Extract related topics from content."""
        # Look for topic mentions
        topics = []
        topic_patterns = [
            r'related to[:\s]+(.+)',
            r'topics[:\s]+(.+)',
            r'see also[:\s]+(.+)'
        ]
        for pattern in topic_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                topics.extend([t.strip() for t in match.split(',')])
        return topics[:5]  # Return top 5 topics

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content."""
        # Simple key phrase extraction
        words = content.lower().split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        key_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count frequency
        from collections import Counter
        word_counts = Counter(key_words)
        return [word for word, count in word_counts.most_common(10)]

    def _generate_summary(self, content: str) -> str:
        """Generate a simple summary of content."""
        # Take first paragraph or first 200 characters
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            summary = paragraphs[0]
            if len(summary) > 200:
                summary = summary[:200] + '...'
            return summary
        return content[:200] + '...' if len(content) > 200 else content

    def _generate_aliases(self, title: str) -> List[str]:
        """Generate aliases for the title."""
        aliases = []
        
        # Add lowercase version
        aliases.append(title.lower())
        
        # Add version without special characters
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        aliases.append(clean_title.strip())
        
        # Add abbreviated version
        words = title.split()
        if len(words) > 1:
            abbreviation = ''.join([word[0].upper() for word in words])
            aliases.append(abbreviation)
        
        return list(set(aliases))

    def _suggest_css_class(self, content: str) -> str:
        """Suggest CSS class based on content type."""
        content_lower = content.lower()
        if 'meeting' in content_lower or 'agenda' in content_lower:
            return 'meeting-note'
        elif 'project' in content_lower or 'milestone' in content_lower:
            return 'project-note'
        elif 'template' in content_lower or 'checklist' in content_lower:
            return 'template-note'
        elif 'daily' in content_lower or 'journal' in content_lower:
            return 'daily-note'
        else:
            return 'general-note'

    def _extract_existing_tags(self, content: str) -> List[str]:
        """Extract existing tags from content."""
        tags = re.findall(r'#([a-zA-Z0-9_-]+)', content)
        return list(set(tags))

    def _extract_file_links(self, content: str) -> List[str]:
        """Extract file links from content."""
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        return list(set(links))


def main():
    """Command-line interface for vault management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Obsidian Second Brain Vault Manager")
    parser.add_argument("--create-note", help="Create a new note")
    parser.add_argument("--folder", default="inbox", help="Folder type for new note")
    parser.add_argument("--list", action="store_true", help="List notes")
    parser.add_argument("--daily-note", action="store_true", help="Create daily note")
    
    args = parser.parse_args()
    
    try:
        manager = VaultManager()
        
        if args.create_note:
            manager.create_note(args.create_note, folder_type=args.folder)
        elif args.list:
            notes = manager.list_notes()
            for note in notes:
                print(f"- {note['title']} ({note['path']})")
        elif args.daily_note:
            manager.create_daily_note()
        else:
            print("Use --help for available options")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Run setup first to configure vault path.")


if __name__ == "__main__":
    main()
