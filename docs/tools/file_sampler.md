### File Sampler CLI

Deterministic sampling and analysis of Markdown/YAML files for Obsidian migration planning.

#### Install
- Ensure Python 3.9+ and repo requirements are installed.

#### Run
```bash
python -m scripts.analyzers.file_sampler --root /path/to/vault \
  --sample-size 120 \
  --strategy diverse \
  --seed 42 \
  --output-dir ./out
```

Outputs written to `out/`:
- `sample_analysis.md`: Obsidian-ready report
- `obsidian_template.md`: Frontmatter template suggestions
- `sample.json`: Machine-readable selection and characteristics

#### Strategies
- **dir**: Proportional stratified sampling by top-level directory
- **char**: Proportional stratified sampling by `--strata-key` (directory, extension, size_category, age, length, has_frontmatter)
- **diverse**: Farthest-point greedy selection across characteristics (seeded)

#### Common flags
- `--exclude-dirs ".git node_modules dist build venv"`
- `--include-ext md yml yaml`
- `--max-candidates 500` (diverse performance)
- `--max-read-bytes 2048` (content window)
- `--follow-symlinks` (opt-in)
- `--log-level DEBUG` for verbose logs

#### Notes
- Sorting and `--seed` provide repeatable results.
- Frontmatter detection requires `---` at the very start and a closing `---` within the read window.
