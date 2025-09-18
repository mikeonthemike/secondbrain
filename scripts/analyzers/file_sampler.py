"""
File sampling CLI for knowledge base organization and Obsidian migration planning.

Features
- Scans a root directory for markdown/yaml files with excludes
- Extracts per-file characteristics for stratified or diverse sampling
- Provides three sampling strategies: directory, characteristic, diverse
- Deterministic with a seed and stable file ordering
- Generates a markdown analysis report and Obsidian frontmatter suggestions
- Exports a machine-readable JSON of sampled files and characteristics

Usage
  python -m scripts.analyzers.file_sampler --help
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import random
import re
from collections import Counter, defaultdict


# -------------------------
# CLI and configuration
# -------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sample and analyze markdown/yaml files for Obsidian migration.",
    )
    parser.add_argument("--root", type=Path, required=True, help="Root directory to scan")
    parser.add_argument("--sample-size", type=int, default=100, help="Number of files to sample")
    parser.add_argument(
        "--strategy",
        choices=["dir", "char", "diverse"],
        default="diverse",
        help="Sampling strategy: by top-level directory, by a characteristic, or diverse",
    )
    parser.add_argument(
        "--strata-key",
        choices=[
            "directory",
            "extension",
            "size_category",
            "age",
            "length",
            "has_frontmatter",
        ],
        default="directory",
        help="Characteristic to stratify by when using --strategy=char",
    )
    parser.add_argument(
        "--include-ext",
        nargs="*",
        default=["md", "yml", "yaml"],
        help="File extensions (without dot) to include",
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        default=[".git", "node_modules", "dist", "build", "venv", ".venv", "__pycache__"],
        help="Directory names to exclude from scanning",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to write reports and JSON output",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional explicit path for JSON output (defaults to output-dir/sample.json)",
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed for determinism")
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=500,
        help="Max candidate files to consider per-step in diverse sampling (performance)",
    )
    parser.add_argument(
        "--max-read-bytes",
        type=int,
        default=2048,
        help="Maximum number of bytes to read from each file for content analysis",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symlinks during scanning (disabled by default for safety)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )
    return parser.parse_args()


# -------------------------
# File and characteristics
# -------------------------


@dataclass(frozen=True)
class FileCharacteristics:
    depth: int
    directory: str
    extension: str
    size_category: str
    age: str
    length: str
    has_frontmatter: bool
    content_hints: Tuple[str, ...]


class FileSampler:
    def __init__(
        self,
        root_directory: Path,
        include_extensions: Optional[Sequence[str]] = None,
        exclude_dir_names: Optional[Sequence[str]] = None,
        max_read_bytes: int = 2048,
        follow_symlinks: bool = False,
        rng: Optional[random.Random] = None,
        max_candidates: int = 500,
    ) -> None:
        self.root_dir: Path = root_directory.resolve()
        self.include_extensions: Set[str] = {
            (ext.lower().lstrip(".")) for ext in (include_extensions or ["md", "yml", "yaml"])
        }
        self.exclude_dir_names: Set[str] = set(exclude_dir_names or [])
        self.max_read_bytes: int = int(max_read_bytes)
        self.follow_symlinks: bool = bool(follow_symlinks)
        self.rng: random.Random = rng or random.Random()
        self.max_candidates: int = int(max_candidates)

        self.files: List[Path] = []

    def scan_files(self) -> List[Path]:
        """Scan for files with included extensions, respecting excludes. Stable sorted order."""
        scanned: List[Path] = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir, followlinks=self.follow_symlinks):
            # Filter excluded directories in-place for os.walk pruning
            dirnames[:] = [d for d in dirnames if d not in self.exclude_dir_names]
            for filename in filenames:
                path = Path(dirpath) / filename
                # Skip if extension not included
                ext = path.suffix.lower().lstrip(".")
                if ext not in self.include_extensions:
                    continue
                # Contain traversal within root
                try:
                    path.resolve().relative_to(self.root_dir)
                except Exception:
                    continue
                scanned.append(path)
        # Stable ordering
        scanned.sort(key=lambda p: p.resolve().relative_to(self.root_dir).as_posix())
        self.files = scanned
        logging.info("Found %d files", len(self.files))
        return self.files

    def analyze_file_characteristics(self, file_path: Path) -> FileCharacteristics:
        """Extract characteristics from a file for sampling."""
        relative_path = file_path.resolve().relative_to(self.root_dir)
        depth = max(0, len(relative_path.parts) - 1)
        directory = relative_path.parts[0] if len(relative_path.parts) > 1 else "root"

        try:
            stat = file_path.stat()
            size_bytes = stat.st_size
            mod_time = datetime.fromtimestamp(stat.st_mtime)
        except PermissionError:
            size_bytes = 0
            mod_time = datetime.fromtimestamp(0)

        if size_bytes < 1024:
            size_category = "small"
        elif size_bytes < 10240:
            size_category = "medium"
        else:
            size_category = "large"

        age_days = (datetime.now() - mod_time).days
        if age_days < 30:
            age = "recent"
        elif age_days < 365:
            age = "this_year"
        else:
            age = "old"

        extension = file_path.suffix.lower().lstrip(".")

        # Content analysis
        has_frontmatter = False
        length = "unknown"
        content_hints: List[str] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(self.max_read_bytes)
            has_frontmatter = self._has_yaml_frontmatter(content)

            # Word count estimate from the window
            word_count = len(content.split())
            if word_count < 100:
                length = "short"
            elif word_count < 500:
                length = "medium"
            else:
                length = "long"

            # Simple keyword detection for content type hints
            content_lower = content.lower()
            keywords = {
                "meeting": ["meeting", "agenda", "minutes", "attendees"],
                "project": ["project", "milestone", "deadline", "task"],
                "research": ["research", "study", "analysis", "findings"],
                "personal": ["personal", "family", "health", "finance"],
                "todo": ["todo", "task", "action", "- [ ]", "checkbox"],
            }
            for category, terms in keywords.items():
                if any(term in content_lower for term in terms):
                    content_hints.append(category)
        except PermissionError:
            logging.warning("Permission denied reading %s", file_path)

        return FileCharacteristics(
            depth=depth,
            directory=directory,
            extension=extension,
            size_category=size_category,
            age=age,
            length=length,
            has_frontmatter=has_frontmatter,
            content_hints=tuple(sorted(set(content_hints))),
        )

    @staticmethod
    def _has_yaml_frontmatter(text: str) -> bool:
        if not text.startswith("---"):
            return False
        # Require a closing --- on its own line within the window
        # Accept both \n---\n and \r\n---\r\n patterns
        match = re.search(r"\n---(\r?\n|$)", text[3:])
        return match is not None

    # -------------------------
    # Sampling strategies
    # -------------------------

    def stratified_sample(
        self, sample_size: int, strata_key: str = "directory"
    ) -> Tuple[List[Path], Dict[Path, FileCharacteristics]]:
        if not self.files:
            self.scan_files()
        all_chars: Dict[Path, FileCharacteristics] = {
            p: self.analyze_file_characteristics(p) for p in self.files
        }
        strata: Dict[str, List[Path]] = defaultdict(list)
        for p, ch in all_chars.items():
            value = getattr(ch, strata_key, "unknown")
            # Multi-valued not supported for strata; convert tuple to a deterministic joined label
            if isinstance(value, (tuple, list)):
                value = ",".join(value) if value else "none"
            strata[str(value)].append(p)

        total = len(self.files)
        k = min(sample_size, total)
        # Proportional allocation with remainder distribution (largest remainder method)
        allocations: Dict[str, int] = {}
        remainders: List[Tuple[float, str]] = []
        running_sum = 0
        for label, files in strata.items():
            proportion = len(files) / total if total > 0 else 0
            exact = k * proportion
            base = int(exact)
            allocations[label] = min(base, len(files))
            running_sum += allocations[label]
            remainders.append((exact - base, label))

        # Distribute remaining slots
        remaining = k - running_sum
        for _, label in sorted(remainders, key=lambda x: x[0], reverse=True):
            if remaining <= 0:
                break
            if allocations[label] < len(strata[label]):
                allocations[label] += 1
                remaining -= 1

        sampled: List[Path] = []
        for label, files in strata.items():
            n = allocations.get(label, 0)
            if n <= 0:
                continue
            chosen = self._rng_sample(files, n)
            sampled.extend(chosen)

        # Guard against any overfill
        sampled = sampled[:k]
        return sampled, all_chars

    def diverse_sample(self, sample_size: int) -> Tuple[List[Path], Dict[Path, FileCharacteristics]]:
        if not self.files:
            self.scan_files()
        all_chars: Dict[Path, FileCharacteristics] = {
            p: self.analyze_file_characteristics(p) for p in self.files
        }

        if not all_chars:
            return [], all_chars

        k = min(sample_size, len(self.files))
        remaining: List[Path] = list(self.files)
        # Start with a deterministic but seeded element: pick from a stable list using rng
        first_index = self.rng.randrange(len(remaining))
        selected: List[Path] = [remaining.pop(first_index)]

        # Maintain each candidate's min distance to the selected set for faster farthest-point sampling
        min_distance: Dict[Path, float] = {p: self._distance(all_chars[p], all_chars[selected[0]]) for p in remaining}

        while len(selected) < k and remaining:
            # Optionally restrict to a subset of candidates for performance
            pool = self._rng_sample(remaining, min(self.max_candidates, len(remaining)))
            # Choose the candidate with the largest min distance
            best_file: Optional[Path] = None
            best_score: float = -1.0
            for p in pool:
                score = min_distance.get(p, 0.0)
                if score > best_score:
                    best_score = score
                    best_file = p
            if best_file is None:
                best_file = pool[0]
            selected.append(best_file)
            # Remove from remaining
            remaining.remove(best_file)
            # Update min distances with the new selected file
            for p in remaining:
                d = self._distance(all_chars[p], all_chars[best_file])
                if p not in min_distance:
                    min_distance[p] = d
                else:
                    if d < min_distance[p]:
                        min_distance[p] = d

        return selected, all_chars

    def _rng_sample(self, population: Sequence[Path], k: int) -> List[Path]:
        # Use rng without modifying global state, on a copy for deterministic behavior
        if k <= 0:
            return []
        if k >= len(population):
            return list(population)
        indices = list(range(len(population)))
        self.rng.shuffle(indices)
        chosen_indices = indices[:k]
        return [population[i] for i in sorted(chosen_indices)]

    # -------------------------
    # Distances and helpers
    # -------------------------

    @staticmethod
    def _ordinal_map(value: str, order: Sequence[str]) -> int:
        try:
            return list(order).index(value)
        except ValueError:
            return 0

    def _distance(self, a: FileCharacteristics, b: FileCharacteristics) -> float:
        # Weighted mixed-type distance
        # depth: absolute difference (cap at 5)
        depth_d = min(abs(a.depth - b.depth), 5) / 5.0

        # directory: 0/1
        dir_d = 0.0 if a.directory == b.directory else 1.0

        # size_category, length, age as ordinal distances
        size_order = ("small", "medium", "large")
        length_order = ("short", "medium", "long")
        age_order = ("recent", "this_year", "old")
        size_d = abs(self._ordinal_map(a.size_category, size_order) - self._ordinal_map(b.size_category, size_order)) / 2.0
        length_d = abs(self._ordinal_map(a.length, length_order) - self._ordinal_map(b.length, length_order)) / 2.0
        age_d = abs(self._ordinal_map(a.age, age_order) - self._ordinal_map(b.age, age_order)) / 2.0

        # has_frontmatter: 0/1
        fm_d = 0.0 if a.has_frontmatter == b.has_frontmatter else 1.0

        # extension: 0/1
        ext_d = 0.0 if a.extension == b.extension else 1.0

        # content_hints: Jaccard distance
        set_a, set_b = set(a.content_hints), set(b.content_hints)
        union = len(set_a | set_b)
        inter = len(set_a & set_b)
        hints_d = 0.0 if union == 0 else 1.0 - (inter / union)

        # Weights (tunable)
        w_depth = 0.5
        w_dir = 1.0
        w_size = 0.5
        w_length = 0.5
        w_age = 0.5
        w_fm = 0.5
        w_ext = 0.5
        w_hints = 1.0

        total = (
            w_depth * depth_d
            + w_dir * dir_d
            + w_size * size_d
            + w_length * length_d
            + w_age * age_d
            + w_fm * fm_d
            + w_ext * ext_d
            + w_hints * hints_d
        )
        return float(total)

    # -------------------------
    # Reporting
    # -------------------------

    def create_obsidian_sample_report(
        self,
        sampled_files: Sequence[Path],
        characteristics: Dict[Path, FileCharacteristics],
        output_file: Path,
    ) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# File Sample Analysis for Obsidian Migration\n\n")
            f.write(f"Sample size: {len(sampled_files)} files\n")
            f.write(f"Total files: {len(self.files)} files\n\n")

            f.write("## Recommended Obsidian Structure\n\n")

            directories = [characteristics[file].directory for file in sampled_files]
            dir_counter = Counter(directories)

            f.write("### Suggested Maps of Content (MOCs)\n")
            for directory, count in dir_counter.most_common():
                if count > 2:
                    f.write(f"- [[{directory.replace('_', ' ').title()} MOC]] - {count} files in sample\n")
            f.write("\n")

            f.write("### Suggested Tag Hierarchy\n")
            content_hints: List[str] = []
            for file in sampled_files:
                content_hints.extend(characteristics[file].content_hints)
            hint_counter = Counter(content_hints)
            for hint, count in hint_counter.most_common():
                f.write(f"- `#{hint}` - appears in {count} sample files\n")
            f.write("\n")

            f.write("## Sample Characteristics\n\n")
            char_keys = ["directory", "size_category", "age", "length", "has_frontmatter"]
            for key in char_keys:
                values = [getattr(characteristics[file], key, "unknown") for file in sampled_files]
                counter = Counter(values)
                f.write(f"### {key.replace('_', ' ').title()}\n")
                for value, count in counter.most_common():
                    f.write(f"- {value}: {count}\n")
                f.write("\n")

            f.write("## Sample Files Analysis\n\n")
            for file_path in sorted(sampled_files, key=lambda p: p.resolve().relative_to(self.root_dir).as_posix()):
                relative_path = file_path.resolve().relative_to(self.root_dir)
                chars = characteristics[file_path]

                clean_name = re.sub(r"[^\w\s-]", "", relative_path.stem)
                clean_name = re.sub(r"[-\s]+", "-", clean_name)

                f.write(f"### {relative_path}\n")
                f.write(f"**Suggested Obsidian name**: `{clean_name}.md`\n\n")
                f.write(f"**Current location**: `{chars.directory}/`\n")
                f.write(
                    f"**Characteristics**: {chars.size_category} size, {chars.length} length, {chars.age}\n"
                )
                f.write(
                    "**Has YAML frontmatter** ✅ (good for Obsidian)\n"
                    if chars.has_frontmatter
                    else "**No frontmatter** - consider adding for better organization\n"
                )
                if chars.content_hints:
                    suggested_tags = [f"#{hint}" for hint in chars.content_hints]
                    f.write(f"**Suggested tags**: {', '.join(suggested_tags)}\n")
                f.write(
                    f"**Potential links**: Look for connections to other files in `{chars.directory}`\n"
                )
                f.write("\n---\n\n")

    def suggest_obsidian_frontmatter_template(
        self,
        sampled_files: Sequence[Path],
        characteristics: Dict[Path, FileCharacteristics],
        output_file: Path,
    ) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        common_dirs = Counter([characteristics[f].directory for f in sampled_files])
        common_hints = Counter()
        for f in sampled_files:
            common_hints.update(characteristics[f].content_hints)

        template = (
            "---\n"
            "tags: []\n"
            "created: {{date}}\n"
            "modified: {{date}}\n"
            "status: \n"
            "type: \n"
            "---\n\n"
            "# {{title}}\n\n"
            "## Links\n\n- \n\n"
            "## Tags\n\n- \n\n"
            "## Notes\n\n"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Obsidian Template Suggestions\n\n")
            f.write("## Frontmatter Template\n")
            f.write("Based on your sample analysis, here's a suggested template:\n\n")
            f.write("```markdown\n")
            f.write(template)
            f.write("```\n\n")
            f.write("## Common Tags to Consider\n")
            for hint, count in common_hints.most_common(10):
                f.write(f"- `#{hint}` (appears {count} times in sample)\n")
            f.write("\n## Common Categories\n")
            for directory, count in common_dirs.most_common():
                f.write(f"- `{directory}` ({count} files)\n")

    # -------------------------
    # JSON output
    # -------------------------

    def write_json(
        self,
        sampled_files: Sequence[Path],
        characteristics: Dict[Path, FileCharacteristics],
        output_file: Path,
    ) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for p in sampled_files:
            rel = p.resolve().relative_to(self.root_dir).as_posix()
            ch = characteristics[p]
            data.append(
                {
                    "path": str(p),
                    "relative": rel,
                    "characteristics": {
                        "depth": ch.depth,
                        "directory": ch.directory,
                        "extension": ch.extension,
                        "size_category": ch.size_category,
                        "age": ch.age,
                        "length": ch.length,
                        "has_frontmatter": ch.has_frontmatter,
                        "content_hints": list(ch.content_hints),
                    },
                }
            )
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"root": str(self.root_dir), "sample": data}, f, indent=2)


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    rng = random.Random(args.seed)
    sampler = FileSampler(
        root_directory=args.root,
        include_extensions=args.include_ext,
        exclude_dir_names=args.exclude_dirs,
        max_read_bytes=args.max_read_bytes,
        follow_symlinks=args.follow_symlinks,
        rng=rng,
        max_candidates=args.max_candidates,
    )

    sampler.scan_files()
    if not sampler.files:
        logging.error("No files found under %s with extensions: %s", args.root, ", ".join(args.include_ext))
        return 2

    if args.strategy == "dir":
        sampled, chars = sampler.stratified_sample(args.sample_size, strata_key="directory")
    elif args.strategy == "char":
        sampled, chars = sampler.stratified_sample(args.sample_size, strata_key=args.strata_key)
    else:
        sampled, chars = sampler.diverse_sample(args.sample_size)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_md = args.output_dir / "sample_analysis.md"
    template_md = args.output_dir / "obsidian_template.md"
    json_path = args.json_out if args.json_out is not None else args.output_dir / "sample.json"

    sampler.create_obsidian_sample_report(sampled, chars, report_md)
    sampler.suggest_obsidian_frontmatter_template(sampled, chars, template_md)
    sampler.write_json(sampled, chars, json_path)

    logging.info("Analysis written to %s", report_md)
    logging.info("Template suggestions written to %s", template_md)
    logging.info("JSON sample written to %s", json_path)
    logging.info("Selected %d files for manual review", len(sampled))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

