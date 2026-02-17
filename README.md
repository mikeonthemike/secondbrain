# Obsidian Second Brain System

A Python implementation of the Building a Second Brain (BASB) methodology using Obsidian and flat markdown files. This system provides local-first knowledge management with powerful AI-enhanced automation capabilities.

## Features

- **Local-First**: All data stored in markdown files on your machine - zero vendor lock-in
- **Obsidian Integration**: Leverages Obsidian's powerful linking and visualization
- **AI-Powered Organization**: Intelligent content classification and auto-organization
- **PARA Method**: Implements the proven PARA organization system (Projects, Areas, Resources, Archive)
- **Smart Content Analysis**: Multi-layer content classification with confidence scoring
- **Bulk Processing**: Convert and organize large amounts of content efficiently
- **Templates**: Pre-built templates for common note types
- **Migration Tools**: Easy transition from other note-taking systems
- **Configurable Vaults**: Work with any Obsidian vault location

## Quick Start

1. **Install dependencies**:
   ```bash
   # Bash (Linux/macOS/Git Bash)
   pip install -r requirements.txt
   
   # Windows PowerShell
   pip install -r requirements.txt
   ```

   **Optional AI Features**: For AI-enhanced organization and content analysis:
   ```bash
   # Install additional AI dependencies
   pip install openai sentence-transformers scikit-learn numpy
   ```

2. **Run setup**:
   ```bash
   # Bash (Linux/macOS/Git Bash)
   python setup.py
   # or use the launcher script
   python run_setup.py
   
   # Windows PowerShell (recommended)
   py setup.py
   # or use the launcher script
   py run_setup.py
   
   # Windows Command Prompt
   python setup.py
   # or use the launcher script
   python run_setup.py
   ```

3. **Open in Obsidian**:
   - Open your configured vault in Obsidian
   - Start creating and organizing notes

## Usage

### Command Line Interface

#### Basic Note Management
```bash
# Create different types of notes
# Bash (Linux/macOS/Git Bash)
python second_brain.py --create-note "My Note" --folder inbox
python second_brain.py --create-project "Website Redesign" --tags "web,active"
python second_brain.py --create-area "Health & Fitness" --tags "personal,ongoing"
python second_brain.py --create-resource "Python Best Practices" --tags "programming,reference"

# Windows PowerShell (recommended)
py second_brain.py --create-note "My Note" --folder inbox
py second_brain.py --create-project "Website Redesign" --tags "web,active"
py second_brain.py --create-area "Health & Fitness" --tags "personal,ongoing"
py second_brain.py --create-resource "Python Best Practices" --tags "programming,reference"

# Create daily note
# Bash
python second_brain.py --daily-note

# Windows PowerShell
py second_brain.py --daily-note

# List all notes and get vault information
# Bash
python second_brain.py --list
python second_brain.py --info

# Windows PowerShell
py second_brain.py --list
py second_brain.py --info
```

#### AI-Powered Organization
```bash
# Analyze and organize content with AI
# Bash
python scripts/ai_organizer_cli.py --analyze "/path/to/vault"
python scripts/ai_organizer_cli.py --organize-notes --folder inbox

# Windows PowerShell
py scripts/ai_organizer_cli.py --analyze "C:\path\to\vault"
py scripts/ai_organizer_cli.py --organize-notes --folder inbox
```

#### Bulk Processing
```bash
# Convert and process multiple files
# Bash
python scripts/bulk_converter.py --input-dir "/path/to/files" --output-dir "/path/to/vault"

# Windows PowerShell
py scripts/bulk_converter.py --input-dir "C:\path\to\files" --output-dir "C:\path\to\vault"
```

#### Configuration
```bash
# Configure vault path
# Bash
python scripts/config_manager.py --vault-path "/path/to/vault"

# Windows PowerShell
py scripts/config_manager.py --vault-path "C:\path\to\vault"
```

### Python API

#### Basic Usage
```python
from second_brain import SecondBrain

# Initialize the Second Brain system
brain = SecondBrain()

# Create different types of notes
project_note = brain.create_project_note(
    title="Website Redesign",
    description="Complete redesign of company website",
    deadline="2024-03-01",
    tags=["web", "active"]
)

area_note = brain.create_area_note(
    title="Health & Fitness",
    description="Personal health and fitness tracking",
    tags=["personal", "ongoing"]
)

resource_note = brain.create_resource_note(
    title="Python Best Practices",
    content="Collection of Python coding best practices",
    source="https://docs.python.org/3/tutorial/",
    tags=["programming", "reference"]
)

# Create daily note
daily_note = brain.create_daily_note()

# List and manage notes
notes = brain.list_notes(folder_type="projects")
vault_info = brain.get_vault_info()
```

#### AI-Enhanced Organization
```python
from scripts.auto_organizer import AIAutoOrganizer

# Initialize AI organizer
organizer = AIAutoOrganizer()

# Analyze content with AI
analysis = organizer.analyze_content_with_ai(
    content="Meeting notes from today's standup...",
    title="Daily Standup"
)

# Organize notes automatically
results = organizer.organize_notes(["note1.md", "note2.md"])

# Learn from user feedback
organizer.learn_from_feedback("note1.md", {
    "content_type": "meeting",
    "tags": ["standup", "team"]
})
```

#### Content Analysis
```python
from scripts.analyzers.content_analyzer import ContentAnalyzer

# Initialize content analyzer
analyzer = ContentAnalyzer()

# Analyze a note
analysis = analyzer.detect_content_type("path/to/note.md", content)
print(f"Content type: {analysis['primary_type']}")
print(f"Confidence: {analysis['confidence']}")
print(f"Tags: {analysis['tags']}")
```

## Vault Structure

```
vault/
├── 00-Inbox/                   # Quick capture area
├── 01-Projects/                # Active projects
├── 02-Areas/                   # Ongoing responsibilities
├── 03-Resources/               # Reference materials
├── 04-Archive/                 # Completed items
├── 05-Templates/               # Note templates
├── 06-Daily-Notes/             # Daily notes
├── 07-MOCs/                    # Maps of Content
└── 99-Attachments/             # Media files
```

## Configuration

The system uses a flexible configuration system:

- **Environment Variables**: `OBSIDIAN_VAULT_PATH`
- **Config File**: `config/vault_config.json`
- **Command Line**: `--vault-path` argument
- **Interactive Setup**: First-run configuration wizard

## Templates

Pre-built templates for common note types:
- Daily notes
- Project notes
- Meeting notes
- Book reviews
- Maps of Content (MOCs)

## Automation Scripts

### Core Automation
- **AI Auto-Organizer**: Intelligent content classification and organization
- **Content Analyzer**: Multi-layer content type detection with confidence scoring
- **Bulk Converter**: Process and convert multiple files efficiently
- **Daily Note Generation**: Automated daily note creation
- **MOC Generation**: Automatic Map of Content creation

### Data Import & Migration
- **Email Import**: Convert emails to markdown notes (planned)
- **Web Clipping**: Import web content with source attribution (planned)
- **Migration Tools**: Import from other note-taking systems (planned)

### AI-Enhanced Features
- **Smart Tagging**: Automatic tag generation based on content analysis
- **Content Classification**: AI-powered categorization of notes
- **Similarity Detection**: Find related content across your vault
- **Learning System**: Improves over time based on user feedback

## AI-Enhanced Features

### Smart Content Analysis
The system uses advanced AI to automatically:
- **Classify Content Types**: Detect meetings, projects, decisions, resources, and more
- **Generate Tags**: Automatically suggest relevant tags based on content
- **Extract Key Phrases**: Identify important concepts and topics
- **Assess Priority**: Determine content urgency and importance
- **Find Similar Content**: Discover related notes across your vault

### Learning System
The AI learns from your feedback to improve over time:
- **User Corrections**: Learn from your manual corrections
- **Pattern Recognition**: Identify your organizational preferences
- **Adaptive Classification**: Improve accuracy based on your vault's content

### Bulk Processing
Efficiently handle large amounts of content:
- **Batch Conversion**: Convert multiple files at once
- **Staging System**: Preview changes before applying them
- **Progress Tracking**: Monitor processing status
- **Error Handling**: Robust error recovery and reporting

## Best Practices

1. **Capture Everything**: Use the inbox for rapid note-taking
2. **Organize with PARA**: Structure notes by Projects, Areas, Resources, Archive
3. **Link Liberally**: Use `[[wikilinks]]` to connect related ideas
4. **Use Templates**: Leverage templates for consistency
5. **Regular Reviews**: Weekly inbox processing and monthly cleanup
6. **Progressive Summarization**: Highlight key points and extract insights
7. **AI-Assisted Organization**: Let the system suggest tags and categories
8. **Feedback Loop**: Correct AI suggestions to improve future accuracy

## Platform-Specific Instructions

### Bash (Linux/macOS/Git Bash)

```bash
# Check Python installation
python --version
python3 --version

# Install dependencies
pip install -r requirements.txt
# or
pip3 install -r requirements.txt

# Run commands
python setup.py
python scripts/vault_manager.py --create-note "My Note"
```

### Windows PowerShell

```powershell
# Check Python installation
py --version
python --version

# Install dependencies
pip install -r requirements.txt

# Run commands (py launcher recommended)
py setup.py
py scripts/vault_manager.py --create-note "My Note"

# Alternative: Use python directly
python setup.py
python scripts/vault_manager.py --create-note "My Note"
```

### Troubleshooting

#### Bash (Linux/macOS/Git Bash)
If you get "command not found" errors:

1. **Check if Python is installed**:
   ```bash
   python --version
   python3 --version
   ```

2. **Check if Python is in PATH**:
   ```bash
   which python
   which python3
   ```

3. **Install Python if missing**:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3 python3-pip
   
   # macOS (with Homebrew)
   brew install python3
   ```

#### Windows PowerShell
If you get "command not found" errors:

1. **Check if Python is installed**:
   ```powershell
   py --version
   python --version
   ```

2. **Check if Python is in PATH**:
   ```powershell
   where py
   where python
   ```

3. **If Python is not in PATH**:
   - Reinstall Python with "Add to PATH" option checked
   - Manually add Python to your PATH environment variable
   - Use the full path: `C:\Python39\python.exe setup.py`

## Recent Changes

### Version 2.0 - Major Architecture Update

**🔄 Completed Changes:**
- ✅ **Removed Notion Dependencies**: Completely eliminated Notion API dependencies for true local-first operation
- ✅ **Enhanced SecondBrain Class**: Added specialized note creation methods for Projects, Areas, Resources, and Archive
- ✅ **AI-Powered Organization**: Implemented intelligent content classification and auto-organization
- ✅ **Smart Content Analysis**: Multi-layer content type detection with confidence scoring
- ✅ **Bulk Processing Tools**: Added efficient batch conversion and processing capabilities
- ✅ **Enhanced CLI**: New specialized commands for different note types
- ✅ **Learning System**: AI that improves over time based on user feedback

**🚀 New Features:**
- **AI Auto-Organizer**: Intelligent content classification using machine learning
- **Content Analyzer**: Advanced content type detection with rich metadata generation
- **Bulk Converter**: Process and convert multiple files efficiently
- **Smart Tagging**: Automatic tag generation based on content analysis
- **Similarity Detection**: Find related content across your vault
- **Staging System**: Preview changes before applying them

**📁 New Project Structure:**
- Added `analyzers/` module for content analysis
- Added `organizers/` module for intelligent organization
- Added `processors/` module for file processing
- Added `converters/` module for format conversion
- Enhanced CLI tools and automation scripts

## Migrating existing notes to Obsidian

### .txt
1. **Manual Migration**: Copy and paste content into new notes
2. **Bulk Migration**: Use the bulk converter tool for large-scale migration

### Other Platforms
- **Notion**: Migration tools planned for future release
- **Evernote**: Migration tools planned for future release
- **OneNote**: Migration tools planned for future release

## Development

### Project Structure

```
secondbrain/
├── scripts/                     # Python automation scripts
│   ├── analyzers/              # Content analysis modules
│   │   ├── content_analyzer.py # Enhanced content type detection
│   │   └── improved_content_analyzer.py # Real-world tuned analyzer
│   ├── organizers/             # Organization and tagging modules
│   │   ├── folder_manager.py   # Folder structure management
│   │   └── tag_extractor.py    # Smart tag extraction
│   ├── processors/             # File processing modules
│   │   ├── batch_processor.py  # Bulk file processing
│   │   └── file_processor.py   # Individual file processing
│   ├── converters/             # File format conversion
│   │   ├── base_converter.py   # Base conversion framework
│   │   ├── pandoc_converter.py # Pandoc-based conversion
│   │   └── text_converter.py   # Text file conversion
│   ├── auto_organizer.py       # AI-enhanced organization
│   ├── ai_organizer_cli.py     # AI organizer command-line interface
│   ├── bulk_converter.py       # Bulk file conversion tool
│   ├── config_manager.py       # Configuration management
│   └── vault_manager.py        # Core vault operations
├── templates/                   # Markdown templates
├── config/                      # Configuration files
├── vault/                       # Default vault (optional)
├── second_brain.py              # Main Second Brain interface
├── setup.py                     # Initial setup script
└── requirements.txt             # Python dependencies
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License. 