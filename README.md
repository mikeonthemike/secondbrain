# Obsidian Second Brain System

A Python implementation of the Building a Second Brain (BASB) methodology using Obsidian and flat markdown files. This system provides local-first knowledge management with powerful automation capabilities.

## Features

- **Local-First**: All data stored in markdown files on your machine
- **Obsidian Integration**: Leverages Obsidian's powerful linking and visualization
- **Configurable Vaults**: Work with any Obsidian vault location
- **Python Automation**: Bulk operations, data import, and system maintenance
- **PARA Method**: Implements the proven PARA organization system
- **Templates**: Pre-built templates for common note types
- **Migration Tools**: Easy transition from other note-taking systems

## Quick Start

1. **Install dependencies**:
   ```bash
   # Bash (Linux/macOS/Git Bash)
   pip install -r requirements.txt
   
   # Windows PowerShell
   pip install -r requirements.txt
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

```bash
# Create a new note
# Bash (Linux/macOS/Git Bash)
python scripts/vault_manager.py --create-note "My Note" --folder inbox

# Windows PowerShell (recommended)
py scripts/vault_manager.py --create-note "My Note" --folder inbox

# Windows Command Prompt
python scripts/vault_manager.py --create-note "My Note" --folder inbox

# Create daily note
# Bash
python scripts/vault_manager.py --daily-note

# Windows PowerShell
py scripts/vault_manager.py --daily-note

# List all notes
# Bash
python scripts/vault_manager.py --list

# Windows PowerShell
py scripts/vault_manager.py --list

# Configure vault path
# Bash
python scripts/config_manager.py --vault-path "/path/to/vault"

# Windows PowerShell
py scripts/config_manager.py --vault-path "C:\path\to\vault"
```

### Python API

```python
from scripts import VaultConfig, VaultManager

# Initialize
config = VaultConfig()
manager = VaultManager(config)

# Create a note
note_path = manager.create_note(
    title="My Note",
    content="Note content",
    folder_type="inbox",
    tags=["productivity", "notes"]
)

# Create daily note
daily_note = manager.create_daily_note()

# List notes
notes = manager.list_notes(folder_type="inbox")

# Update note
manager.update_note(note_path, {
    "content": "Updated content",
    "frontmatter": {"status": "completed"}
})
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

- **Email Import**: Convert emails to markdown notes
- **Web Clipping**: Import web content with source attribution
- **Daily Note Generation**: Automated daily note creation
- **MOC Generation**: Automatic Map of Content creation
- **Migration Tools**: Import from other note-taking systems

## Best Practices

1. **Capture Everything**: Use the inbox for rapid note-taking
2. **Organize with PARA**: Structure notes by Projects, Areas, Resources, Archive
3. **Link Liberally**: Use `[[wikilinks]]` to connect related ideas
4. **Use Templates**: Leverage templates for consistency
5. **Regular Reviews**: Weekly inbox processing and monthly cleanup
6. **Progressive Summarization**: Highlight key points and extract insights

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

## Migrating existing notes to Obsidian

### .txt
1. Manually

2. Bulk migration

## Development

### Project Structure

```
secondbrain/
├── scripts/                     # Python automation scripts
├── templates/                   # Markdown templates
├── config/                      # Configuration files
├── vault/                       # Default vault (optional)
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