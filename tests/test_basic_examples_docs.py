from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs" / "examples" / "basic"
EXAMPLES_DIR = REPO_ROOT / "src" / "pei_docker" / "examples" / "basic"
EXAMPLES_README = REPO_ROOT / "src" / "pei_docker" / "examples" / "README.md"

SOURCE_RE = re.compile(r"^Source:\s+`([^`]+)`\s*$", re.MULTILINE)
SUPPORTING_FILE_RE = re.compile(r"Supporting file:\s+`([^`]+)`")
FENCED_BLOCK_RE = re.compile(r"```(?P<lang>[^\n`]*)\n(?P<body>.*?)```", re.DOTALL)
README_BASIC_ROW_RE = re.compile(
    r"\|\s*`basic/(?P<name>[^`]+)/`\s*\|\s*[^|]+\|\s*\[(?P<title>[^\]]+)\]\((?P<link>[^)]+)\)\s*\|"
)


@dataclass(frozen=True)
class BasicExampleDoc:
    path: Path
    source_relpath: str
    title: str
    yaml_block: str
    supporting_files: tuple[str, ...]

    @property
    def example_name(self) -> str:
        return Path(self.source_relpath).parent.name

    @property
    def source_path(self) -> Path:
        return REPO_ROOT / "src" / "pei_docker" / self.source_relpath


def _iter_fenced_blocks(markdown: str) -> list[tuple[str, str]]:
    return [
        (match.group("lang").strip(), match.group("body").strip())
        for match in FENCED_BLOCK_RE.finditer(markdown)
    ]


def _extract_yaml_block(markdown: str, doc_path: Path) -> str:
    for language, body in _iter_fenced_blocks(markdown):
        if language == "yaml":
            return body
    raise AssertionError(f"No YAML code block found in {doc_path}")


def _parse_doc(doc_path: Path) -> BasicExampleDoc:
    markdown = doc_path.read_text(encoding="utf-8")
    source_match = SOURCE_RE.search(markdown)
    if source_match is None:
        raise AssertionError(f"Missing Source line in {doc_path}")

    yaml_block = _extract_yaml_block(markdown, doc_path)
    title = markdown.splitlines()[0].lstrip("#").strip()
    supporting_files = tuple(SUPPORTING_FILE_RE.findall(markdown))

    return BasicExampleDoc(
        path=doc_path,
        source_relpath=source_match.group(1),
        title=title,
        yaml_block=yaml_block,
        supporting_files=supporting_files,
    )


def _load_basic_docs() -> list[BasicExampleDoc]:
    return [_parse_doc(path) for path in sorted(DOCS_DIR.glob("*.md"))]


def _load_yaml_text(text: str) -> object:
    return yaml.safe_load(text)


def test_basic_docs_map_to_packaged_examples() -> None:
    docs = _load_basic_docs()
    example_names = {path.name for path in EXAMPLES_DIR.iterdir() if path.is_dir()}

    assert docs, "Expected at least one basic example docs page"

    for doc in docs:
        assert doc.source_path.is_file(), f"Missing packaged example file for {doc.path}"
        assert doc.example_name in example_names


def test_basic_docs_supporting_files_exist() -> None:
    for doc in _load_basic_docs():
        for relative_path in doc.supporting_files:
            packaged_path = REPO_ROOT / "src" / "pei_docker" / relative_path
            assert packaged_path.exists(), (
                f"Supporting file referenced in {doc.path} does not exist: "
                f"{relative_path}"
            )


def test_basic_docs_yaml_matches_packaged_config() -> None:
    for doc in _load_basic_docs():
        packaged_yaml = doc.source_path.read_text(encoding="utf-8")
        assert _load_yaml_text(doc.yaml_block) == _load_yaml_text(packaged_yaml)


def test_examples_readme_basic_catalog_stays_in_sync() -> None:
    readme_text = EXAMPLES_README.read_text(encoding="utf-8")
    table_rows = list(README_BASIC_ROW_RE.finditer(readme_text))
    docs_by_name = {doc.example_name: doc for doc in _load_basic_docs()}

    assert table_rows, "Expected at least one Basic examples row in examples README"
    assert {match.group("name") for match in table_rows} == set(docs_by_name)

    for match in table_rows:
        example_name = match.group("name")
        linked_doc = (EXAMPLES_README.parent / match.group("link")).resolve()
        doc = docs_by_name[example_name]

        assert linked_doc == doc.path.resolve()
        assert match.group("title") == doc.title

