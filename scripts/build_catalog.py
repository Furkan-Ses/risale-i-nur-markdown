#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = ROOT / "sources" / "official-markdown-mirror" / "obsidian-markdown"
BOOKS_ROOT = ROOT / "books"
GENERATED_ROOT = ROOT / "generated"
GENERATED_JSON_ROOT = GENERATED_ROOT / "json"
INDEX_ROOT = ROOT / "indexes"
BOOK_INDEX_ROOT = INDEX_ROOT / "books"


BOOK_DIR_RE = re.compile(r"^(?P<order>\d+)\s+(?P<title>.+)$")
FILE_ORDER_RE = re.compile(r"^(?P<order>\d+)\s+(?P<title>.+)$")
TRANSLATION_TABLE = str.maketrans(
    {
        "ı": "i",
        "İ": "I",
        "ğ": "g",
        "Ğ": "G",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
        "â": "a",
        "Â": "A",
        "î": "i",
        "Î": "I",
        "û": "u",
        "Û": "U",
        "'": "",
        "’": "",
    }
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}, text

    raw_meta = text[4:end].splitlines()
    meta: dict[str, str] = {}
    for line in raw_meta:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')

    body = text[end + len(marker) :]
    return meta, body


def slugify(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.lower()
    ascii_only = re.sub(r"[^a-z0-9]+", "-", ascii_only)
    return ascii_only.strip("-")


def title_key(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"\([^)]*\)", "", ascii_only)
    return re.sub(r"[^a-z0-9]+", "", ascii_only)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_title(path: Path) -> str:
    text = read_text(path)
    meta, body = parse_frontmatter(text)
    title = meta.get("title")
    if title:
        return title

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    match = FILE_ORDER_RE.match(path.stem)
    if match:
        return match.group("title")
    return path.stem


def repo_link(target: Path, current_dir: Path) -> str:
    return Path(os.path.relpath(target, current_dir))


def collect_books() -> list[dict[str, object]]:
    books: list[dict[str, object]] = []

    for book_dir in sorted(UPSTREAM_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue
        match = BOOK_DIR_RE.match(book_dir.name)
        if not match:
            continue

        order = int(match.group("order"))
        title = match.group("title")
        book_slug = slugify(title)
        markdown_files = sorted(book_dir.glob("*.md"))
        index_file = next((path for path in markdown_files if path.stem.startswith("00")), None)

        book_meta: dict[str, str] = {}
        if index_file is not None:
            book_meta, _ = parse_frontmatter(read_text(index_file))

        sections = []
        for path in markdown_files:
            if index_file is not None and path == index_file:
                continue

            section_title = extract_title(path)
            file_match = FILE_ORDER_RE.match(path.stem)
            section_order = int(file_match.group("order")) if file_match else 999
            sections.append(
                {
                    "id": f"{order:02d}-{section_order:03d}-{slugify(section_title)}",
                    "order": section_order,
                    "title": section_title,
                    "title_key": title_key(section_title),
                    "path": path.relative_to(ROOT).as_posix(),
                }
            )

        books.append(
            {
                "id": f"{order:02d}-{book_slug}",
                "order": order,
                "title": title,
                "slug": book_slug,
                "path": book_dir.relative_to(ROOT).as_posix(),
                "index_path": index_file.relative_to(ROOT).as_posix() if index_file else None,
                "section_count": len(sections),
                "source_name": book_meta.get("source_name") or book_meta.get("source name"),
                "source_url": book_meta.get("source_url") or book_meta.get("source url"),
                "sections": sections,
            }
        )

    return books


def collect_reference_sources() -> list[dict[str, object]]:
    references: list[dict[str, object]] = []
    if not BOOKS_ROOT.exists():
        return references

    for book_dir in sorted(BOOKS_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue

        by_heading_dir = book_dir / "by_heading"
        merged_files = sorted(
            path for path in book_dir.glob("*.md") if path.name != "README.source.md"
        )
        if not merged_files or not by_heading_dir.exists():
            continue

        merged_path = merged_files[0]
        section_files = sorted(by_heading_dir.glob("*.md"))
        reference_slug = slugify(book_dir.name)
        merged_title = merged_path.stem
        references.append(
            {
                "id": f"reading-book-{reference_slug}",
                "slug": reference_slug,
                "title": merged_title,
                "merged_title": merged_title,
                "merged_path": merged_path.relative_to(ROOT).as_posix(),
                "section_dir": by_heading_dir.relative_to(ROOT).as_posix(),
                "section_count": len(section_files),
                "source_readme": (book_dir / "README.source.md").relative_to(ROOT).as_posix(),
                "sections": [
                    {
                        "title": extract_title(path),
                        "path": path.relative_to(ROOT).as_posix(),
                    }
                    for path in section_files
                ],
            }
        )

    return references


def write_catalog(books: list[dict[str, object]], references: list[dict[str, object]]) -> None:
    GENERATED_JSON_ROOT.mkdir(parents=True, exist_ok=True)
    catalog = {
        "sources": [
            {
                "id": "source-mirror",
                "title": "Source mirror",
                "license": "CC BY-ND 4.0",
                "provenance_readme": "sources/official-markdown-mirror/README.upstream.md",
                "path": "sources/official-markdown-mirror/obsidian-markdown",
                "structure": "Obsidian-style hierarchy with top-level contents and per-book 00 index files.",
            },
            {
                "id": "reading-layer-books",
                "title": "Reading layer books",
                "license": "Repository-local text source",
                "path": "books",
                "structure": "Merged book files plus stable by_heading split files for human reading and downstream indexing.",
            },
        ],
        "books": books,
        "reference_sources": references,
    }
    (GENERATED_JSON_ROOT / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_top_level_index(books: list[dict[str, object]], references: list[dict[str, object]]) -> None:
    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    rows = [
        "# Corpus Index",
        "",
        "Bu indeks, okuma katmanı, AI katmanı ve kaynak aynası arasında net geçiş sağlayan gezinme katmanıdır.",
        "",
        "## İndeks mantığı",
        "",
        "1. **Kaynak aynası:** `sources/official-markdown-mirror/obsidian-markdown/` altında korunan giriş yapısı",
        "2. **Okuma katmanı:** `books/` altında birleşik kitap dosyaları ve `by_heading/` bölümleri",
        "3. **AI katmanı:** `ai/` altında frontmatter, manifest ve passage dosyaları",
        "4. **Makine kataloğu:** `generated/json/catalog.json`",
        "",
        "## Kaynak aynası kitapları",
        "",
        "| # | Kitap | Bölüm | Kaynak indeks | Repo indeksi |",
        "| --- | --- | ---: | --- | --- |",
    ]

    for book in books:
        book_dir = ROOT / str(book["path"])
        index_path = ROOT / str(book["index_path"]) if book["index_path"] else None
        generated_index = BOOK_INDEX_ROOT / f"{book['order']:02d}-{book['slug']}.md"
        upstream_link = (
            f"[{Path(str(book['index_path'])).name}]({repo_link(index_path, INDEX_ROOT).as_posix()})"
            if index_path
            else "-"
        )
        generated_link = f"[{generated_index.name}]({repo_link(generated_index, INDEX_ROOT).as_posix()})"
        rows.append(
            f"| {book['order']} | {book['title']} | {book['section_count']} | {upstream_link} | {generated_link} |"
        )

    rows.extend(
        [
            "",
            "## Okuma katmanı kitapları",
            "",
            "| Kaynak | Birleşik dosya | Bölüm klasörü |",
            "| --- | --- | --- |",
        ]
    )

    for reference in references:
        merged_path = ROOT / str(reference["merged_path"])
        section_dir = ROOT / str(reference["section_dir"])
        rows.append(
            "| "
            f"{reference['title']} | "
            f"[{Path(str(reference['merged_path'])).name}]({repo_link(merged_path, INDEX_ROOT).as_posix()}) | "
            f"[{Path(str(reference['section_dir'])).name}]({repo_link(section_dir, INDEX_ROOT).as_posix()}) |"
        )

    rows.extend(
        [
            "",
            "## Generated assets",
            "",
            "- `generated/json/catalog.json`: kitap ve bölüm kataloğu",
            "- `generated/json/all-upstream-public-summary.json`: tüm kaynak karşılaştırmaları için toplu uyum özeti",
            "- `generated/json/books/`: kitap bazlı official scrape ve karşılaştırma verileri",
            "- `reports/comparisons/all-upstream-public-summary.md`: insan-okur toplu özet raporu",
            "- `reports/comparisons/books/`: kitap bazlı karşılaştırma raporları",
        ]
    )

    (INDEX_ROOT / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_book_indexes(books: list[dict[str, object]]) -> None:
    BOOK_INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    for stale_file in BOOK_INDEX_ROOT.glob("*.md"):
        stale_file.unlink()

    references = {str(reference["slug"]): reference for reference in collect_reference_sources()}

    for book in books:
        current_index = BOOK_INDEX_ROOT / f"{book['order']:02d}-{book['slug']}.md"
        source_dir = ROOT / str(book["path"])
        source_index = ROOT / str(book["index_path"]) if book["index_path"] else None

        rows = [
            f"# {book['title']}",
            "",
            f"- Kaynak aynası klasörü: `{book['path']}`",
            f"- Bölüm sayısı: **{book['section_count']}**",
        ]

        if source_index is not None:
            rows.append(
                f"- Kaynak aynası indeksi: [{source_index.name}]({repo_link(source_index, BOOK_INDEX_ROOT).as_posix()})"
            )
        if book.get("source_name"):
            rows.append(f"- Kaynak: {book['source_name']}")
        if book.get("source_url"):
            rows.append(f"- Kaynak URL: {book['source_url']}")

        rows.extend(
            [
                "",
                "| # | Bölüm | Dosya |",
                "| --- | --- | --- |",
            ]
        )

        for section in book["sections"]:
            section_path = ROOT / str(section["path"])
            rows.append(
                f"| {section['order']} | {section['title']} | "
                f"[{section_path.name}]({repo_link(section_path, BOOK_INDEX_ROOT).as_posix()}) |"
            )

        reference = references.get(str(book["slug"]))
        if reference:
            canonical_merged = ROOT / str(reference["merged_path"])
            canonical_section_dir = ROOT / str(reference["section_dir"])
            rows.extend(
                [
                    "",
                    "## Okuma katmanı kopyası",
                    "",
                    f"- Birleşik kitap dosyası: [{canonical_merged.name}]({repo_link(canonical_merged, BOOK_INDEX_ROOT).as_posix()})",
                    f"- Bölüm klasörü: [{canonical_section_dir.name}]({repo_link(canonical_section_dir, BOOK_INDEX_ROOT).as_posix()})",
                    "",
                    "| # | Kayıt | Dosya |",
                    "| --- | --- | --- |",
                ]
            )
            for order, section in enumerate(reference["sections"], start=1):
                path = ROOT / str(section["path"])
                rows.append(
                    f"| {order} | {section['title']} | "
                    f"[{path.name}]({repo_link(path, BOOK_INDEX_ROOT).as_posix()}) |"
                )

        current_index.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    books = collect_books()
    references = collect_reference_sources()
    write_catalog(books, references)
    write_top_level_index(books, references)
    write_book_indexes(books)
    print(f"Wrote catalog for {len(books)} books.")


if __name__ == "__main__":
    main()
