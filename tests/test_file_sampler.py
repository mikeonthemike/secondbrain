import json
from pathlib import Path

import shutil

from scripts.analyzers.file_sampler import FileSampler


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def setup_vault(tmp_path: Path) -> None:
    # Files with and without frontmatter
    write_file(tmp_path / "root_note.md", "---\ntags: []\n---\nHello world\n")
    write_file(tmp_path / "notes" / "meeting.md", "Meeting agenda and attendees\n")
    write_file(tmp_path / "notes" / "research.yml", "title: Study\n")
    write_file(tmp_path / "projects" / "proj1.md", "Project milestone and deadline\n")
    write_file(tmp_path / "projects" / "proj2.md", "Some content\n")


def test_scan_and_characteristics(tmp_path):
    setup_vault(tmp_path)
    sampler = FileSampler(root_directory=tmp_path)
    files = sampler.scan_files()
    assert len(files) == 5
    # Ensure stable ordering by relative path
    rels = [p.resolve().relative_to(tmp_path).as_posix() for p in files]
    assert rels == sorted(rels)

    ch = sampler.analyze_file_characteristics(files[0])
    assert ch.extension in {"md", "yml", "yaml"}
    assert ch.directory in {"root", "notes", "projects"}


def test_frontmatter_detection(tmp_path):
    fm_file = tmp_path / "a.md"
    write_file(fm_file, "---\nkey: value\n---\nBody\n")
    non_fm = tmp_path / "b.md"
    write_file(non_fm, "not frontmatter\n---\n")

    sampler = FileSampler(root_directory=tmp_path)
    ch_fm = sampler.analyze_file_characteristics(fm_file)
    ch_non = sampler.analyze_file_characteristics(non_fm)
    assert ch_fm.has_frontmatter is True
    assert ch_non.has_frontmatter is False


def test_determinism_with_seed(tmp_path):
    setup_vault(tmp_path)
    s1 = FileSampler(root_directory=tmp_path, rng=None)
    s1.scan_files()
    # Two samplers with same seed should pick the same selection
    from random import Random

    s1.rng = Random(123)
    sample1, _ = s1.diverse_sample(3)

    s2 = FileSampler(root_directory=tmp_path, rng=Random(123))
    s2.scan_files()
    sample2, _ = s2.diverse_sample(3)

    assert [p.as_posix() for p in sample1] == [p.as_posix() for p in sample2]


def test_stratified_exact_size(tmp_path):
    setup_vault(tmp_path)
    sampler = FileSampler(root_directory=tmp_path)
    sampler.scan_files()
    sample, _ = sampler.stratified_sample(4, strata_key="directory")
    assert len(sample) == 4

