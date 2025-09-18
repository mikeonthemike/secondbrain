# Email Integration Design for Second Brain System

## 🎯 **Core Purpose**
Transform emails into structured knowledge notes in your Obsidian vault, enabling seamless capture of important information, meeting notes, project updates, and reference materials.

## 📧 **Email Sources & Authentication**

### Supported Providers
1. **Gmail** (Primary)
   - OAuth2 authentication
   - Gmail API integration
   - Label-based filtering

2. **Outlook/Office 365** (Secondary)
   - Microsoft Graph API
   - OAuth2 authentication
   - Folder-based filtering

3. **Generic IMAP** (Fallback)
   - Standard IMAP protocol
   - Username/password authentication
   - Folder-based filtering

## 🧠 **Content Classification System**

### Classification Layers

#### 1. **Primary Classification (Content Type)**
```
Email Content → Content Analyzer → Primary Type
```

**Classification Methods:**
- **Keyword Analysis**: Subject line and body content patterns
- **Sender Analysis**: Known contacts and domain patterns
- **Structure Analysis**: Email format and layout patterns
- **Attachment Analysis**: File types and names
- **Date/Time Analysis**: Meeting patterns, recurring events

**Primary Types:**
- **Meeting Notes**: Calendar invites, meeting summaries, follow-ups
- **Project Updates**: Status reports, progress updates, deliverables
- **Reference Materials**: Articles, documentation, resources, newsletters
- **Action Items**: Tasks, assignments, deadlines, follow-ups
- **General Notes**: Miscellaneous important information
- **Automated**: System notifications, alerts, confirmations

#### 2. **Secondary Classification (PARA Method)**
```
Primary Type + Context → PARA Classifier → Folder Assignment
```

**PARA Classification Logic:**
- **Projects**: Active work with deadlines, specific outcomes
- **Areas**: Ongoing responsibilities, recurring themes
- **Resources**: Reference materials, learning content
- **Archive**: Completed items, historical information

#### 3. **Tertiary Classification (Tags & Metadata)**
```
Content + Context → Tag Extractor → Semantic Tags
```

**Tag Categories:**
- **Content Tags**: meeting, project, reference, task, update
- **Project Tags**: Extracted from subject lines and content
- **Priority Tags**: urgent, important, follow-up, review
- **Source Tags**: gmail, outlook, newsletter, automated
- **Date Tags**: 2024-q1, january, weekly, monthly

### Classification Algorithm

#### Step 1: Content Analysis
```python
def analyze_email_content(email):
    # Extract key information
    subject = email.subject.lower()
    body = email.body.lower()
    sender = email.sender.lower()
    
    # Keyword scoring
    meeting_score = calculate_meeting_score(subject, body)
    project_score = calculate_project_score(subject, body)
    reference_score = calculate_reference_score(subject, body)
    
    # Sender analysis
    sender_type = classify_sender(sender)
    
    # Structure analysis
    has_attachments = len(email.attachments) > 0
    is_calendar_invite = 'calendar' in email.headers
    
    return {
        'meeting_score': meeting_score,
        'project_score': project_score,
        'reference_score': reference_score,
        'sender_type': sender_type,
        'has_attachments': has_attachments,
        'is_calendar_invite': is_calendar_invite
    }
```

#### Step 2: Primary Type Classification
```python
def classify_primary_type(analysis):
    scores = {
        'meeting': analysis['meeting_score'] + (10 if analysis['is_calendar_invite'] else 0),
        'project': analysis['project_score'] + (5 if 'project' in analysis['sender_type'] else 0),
        'reference': analysis['reference_score'] + (5 if 'newsletter' in analysis['sender_type'] else 0),
        'action_item': calculate_action_score(analysis),
        'automated': 10 if 'automated' in analysis['sender_type'] else 0
    }
    
    return max(scores, key=scores.get)
```

#### Step 3: PARA Classification
```python
def classify_para_type(primary_type, analysis, user_context):
    if primary_type == 'meeting':
        return 'projects' if has_deadline(analysis) else 'areas'
    elif primary_type == 'project':
        return 'projects' if is_active_project(analysis, user_context) else 'archive'
    elif primary_type == 'reference':
        return 'resources'
    elif primary_type == 'action_item':
        return 'projects' if has_project_context(analysis) else 'inbox'
    else:
        return 'inbox'
```

## 📝 **Note Templates by Classification**

### Meeting Notes Template
```markdown
---
title: "{{subject}}"
created: "{{date}}"
type: "meeting"
source: "email"
sender: "{{sender}}"
participants: ["{{participants}}"]
project: "{{project_name}}"
tags: [meeting, {{project_tags}}, {{priority_tags}}]
---

# {{subject}}

**Date:** {{date}}  
**Time:** {{time}}  
**Attendees:** {{participants}}

## Discussion
{{content}}

## Action Items
- [ ] 

## Decisions
- 

## Next Steps
- 
```

### Project Update Template
```markdown
---
title: "{{subject}}"
created: "{{date}}"
type: "project-update"
source: "email"
sender: "{{sender}}"
project: "{{project_name}}"
status: "{{update_status}}"
tags: [project, update, {{project_tags}}, {{priority_tags}}]
---

# {{subject}}

**Project:** {{project_name}}  
**From:** {{sender}}  
**Date:** {{date}}  
**Status:** {{update_status}}

## Update Summary
{{content}}

## Key Points
- 

## Progress
- [x] Completed items
- [ ] In progress
- [ ] Blocked items

## Next Actions
- [ ] 

## Related Notes
- 
```

### Reference Material Template
```markdown
---
title: "{{subject}}"
created: "{{date}}"
type: "reference"
source: "email"
sender: "{{sender}}"
url: "{{extracted_urls}}"
tags: [reference, {{content_tags}}, {{priority_tags}}]
---

# {{subject}}

**Source:** {{sender}}  
**Date:** {{date}}  
**URLs:** {{extracted_urls}}

## Summary
{{content}}

## Key Takeaways
- 

## Related Topics
- 

## Action Items
- [ ] 
```

## ⚙️ **Configuration System**

### Email Import Settings
```json
{
  "email_import": {
    "enabled": true,
    "providers": {
      "gmail": {
        "enabled": true,
        "credentials_file": "credentials/gmail_credentials.json",
        "token_file": "credentials/gmail_token.json",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
      },
      "outlook": {
        "enabled": false,
        "tenant_id": "",
        "client_id": "",
        "client_secret": ""
      }
    },
    "filters": {
      "labels": ["To Process", "Second Brain"],
      "keywords": ["meeting", "project", "update", "important"],
      "senders": ["boss@company.com", "notifications@project.com"],
      "date_range_days": 30
    },
    "classification": {
      "auto_classify": true,
      "confidence_threshold": 0.7,
      "fallback_type": "general",
      "user_override": true,
      "learning_enabled": true
    },
    "processing": {
      "extract_attachments": true,
      "download_images": false,
      "max_email_size_mb": 10,
      "preserve_formatting": true
    }
  }
}
```

### Classification Rules
```json
{
  "classification_rules": {
    "meeting": {
      "keywords": ["meeting", "call", "conference", "standup", "review"],
      "patterns": ["\\d{1,2}:\\d{2}", "am|pm", "agenda", "minutes"],
      "senders": ["calendar@", "meeting@", "zoom@"],
      "templates": ["calendar_invite", "meeting_summary"]
    },
    "project": {
      "keywords": ["project", "milestone", "deliverable", "sprint", "phase"],
      "patterns": ["status", "update", "progress", "deadline"],
      "senders": ["project@", "pm@", "manager@"],
      "templates": ["project_update", "milestone_report"]
    },
    "reference": {
      "keywords": ["article", "newsletter", "blog", "tutorial", "guide"],
      "patterns": ["read more", "learn more", "tutorial", "guide"],
      "senders": ["newsletter@", "blog@", "learning@"],
      "templates": ["reference_material", "learning_resource"]
    }
  }
}
```

## 🔧 **Technical Implementation**

### Core Components
1. **`scripts/email_import.py`** - Main orchestrator
2. **`scripts/email_parsers/gmail_parser.py`** - Gmail API integration
3. **`scripts/email_parsers/outlook_parser.py`** - Outlook integration
4. **`scripts/email_parsers/imap_parser.py`** - Generic IMAP support
5. **`scripts/email_processors/content_analyzer.py`** - Content analysis
6. **`scripts/email_processors/classifier.py`** - Classification engine
7. **`scripts/email_processors/note_creator.py`** - Note generation

### Data Flow
```
Email Provider → Parser → Content Analyzer → Classifier → Note Creator → Vault Manager → Obsidian
```

### Classification Pipeline
```
Raw Email → Content Extraction → Feature Analysis → Classification Rules → Confidence Scoring → Type Assignment → PARA Mapping → Template Selection → Note Creation
```

## 🎨 **User Experience**

### Command Line Interface
```bash
# Import emails with auto-classification
python scripts/email_import.py --provider gmail --auto-classify

# Import specific email by ID
python scripts/email_import.py --provider gmail --email-id "12345"

# Import from date range with classification preview
python scripts/email_import.py --provider gmail --since "2024-01-01" --preview

# Train classification model
python scripts/email_import.py --train-classifier --provider gmail
```

### Interactive Mode
```bash
python scripts/email_import.py --interactive
# Shows list of emails with classification suggestions
# User can override classifications
# Preview notes before creation
```

## 🔒 **Security & Privacy**

### Authentication
- **OAuth2** for Gmail and Outlook (no password storage)
- **Encrypted credentials** storage
- **Token refresh** handling
- **Minimal permissions** (read-only access)

### Data Handling
- **Local processing** only (no cloud storage)
- **Temporary files** cleanup
- **Sensitive data** filtering options
- **Attachment scanning** for security

## 📊 **Success Metrics**

### Classification Accuracy
- [ ] 90%+ accuracy on meeting vs. non-meeting emails
- [ ] 85%+ accuracy on project vs. reference classification
- [ ] 80%+ accuracy on PARA folder assignment
- [ ] User override rate < 20%

### Functionality
- [ ] Import emails from Gmail, Outlook, and IMAP
- [ ] Automatically classify content types
- [ ] Extract and process attachments
- [ ] Create properly structured notes
- [ ] Handle authentication se