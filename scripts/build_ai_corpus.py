#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOKS_ROOT = ROOT / "books"
SUMMARY_PATH = ROOT / "generated" / "json" / "all-upstream-public-summary.json"
BOOK_COMPARISON_ROOT = ROOT / "generated" / "json" / "books"
AI_ROOT = ROOT / "ai"
AI_BOOKS_ROOT = AI_ROOT / "books"
AI_MANIFESTS_ROOT = AI_ROOT / "manifests"
AI_PASSAGES_ROOT = AI_ROOT / "passages"

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FILE_PREFIX_RE = re.compile(r"^(?P<order>\d+)\s*[- ]\s*(?P<title>.+)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
SEPARATOR_RE = re.compile(r"^\s*(?:---|\*\*\*|\*\s*\*\s*\*)\s*$")
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

TARGET_WORDS = 420
MIN_WORDS = 180
MAX_WORDS = 700


@dataclass
class ContentBlock:
    order: int
    headings: list[str]
    text: str
    kind: str


def slugify(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"[^a-z0-9]+", "-", ascii_only)
    return ascii_only.strip("-")


def title_key(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"\([^)]*\)", "", ascii_only)
    return re.sub(r"[^a-z0-9]+", "", ascii_only)


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
    return meta, text[end + len(marker) :]


def extract_title(path: Path, body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    match = FILE_PREFIX_RE.match(path.stem)
    if match:
        return match.group("title")
    return path.stem


def yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def write_frontmatter(data: dict[str, object], body: str) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    return "\n".join(lines)


def normalize_written_path(path: Path) -> Path:
    if path.exists():
        return path
    fallback = path.with_name(f"{path.stem} 2{path.suffix}")
    if fallback.exists():
        fallback.rename(path)
    return path


def collect_books() -> list[dict[str, object]]:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    summary_map = {str(item["slug"]): item for item in summary["books"]}
    books: list[dict[str, object]] = []
    for book_dir in sorted(BOOKS_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue
        slug = book_dir.name
        by_heading_dir = book_dir / "by_heading"
        merged_candidates = sorted(
            path for path in book_dir.glob("*.md") if path.name != "README.source.md"
        )
        if not by_heading_dir.exists() or not merged_candidates:
            continue
        merged_path = merged_candidates[0]
        summary_item = summary_map.get(slug, {})
        books.append(
            {
                "slug": slug,
                "title": merged_path.stem,
                "dir": book_dir,
                "merged_path": merged_path,
                "by_heading_dir": by_heading_dir,
                "summary": summary_item,
                "comparison": load_book_comparison(slug),
            }
        )
    return books


def load_book_comparison(slug: str) -> dict[str, dict[str, object]]:
    path = BOOK_COMPARISON_ROOT / f"{slug}-public-comparison.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    mapping: dict[str, dict[str, object]] = {}
    for section in payload.get("sections", []):
        mapping[title_key(str(section["title"]))] = section
    return mapping


def parse_blocks(section_title: str, body: str) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    current_lines: list[str] = []
    headings = [section_title]
    current_order = 0
    fence_lines: list[str] | None = None

    def flush_paragraph(kind: str = "paragraph") -> None:
        nonlocal current_lines, current_order
        text = "\n".join(line.rstrip() for line in current_lines).strip()
        current_lines = []
        if not text:
            return
        current_order += 1
        blocks.append(ContentBlock(order=current_order, headings=list(headings), text=text, kind=kind))

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if fence_lines is not None:
            fence_lines.append(line)
            if stripped.startswith("```"):
                flush_paragraph()
                current_order += 1
                blocks.append(
                    ContentBlock(
                        order=current_order,
                        headings=list(headings),
                        text="\n".join(fence_lines).strip(),
                        kind="fence",
                    )
                )
                fence_lines = None
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            fence_lines = [line]
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            headings = headings[:level - 1] + [title]
            continue

        if not stripped:
            flush_paragraph()
            continue

        if SEPARATOR_RE.match(stripped):
            flush_paragraph()
            continue

        current_lines.append(line)

    flush_paragraph()
    if fence_lines:
        current_order += 1
        blocks.append(
            ContentBlock(
                order=current_order,
                headings=list(headings),
                text="\n".join(fence_lines).strip(),
                kind="fence",
            )
        )
    return blocks


def make_chunk(
    book: dict[str, object],
    section: dict[str, object],
    chunk_index: int,
    blocks: list[ContentBlock],
    ai_section_path: Path,
) -> dict[str, object]:
    heading_paths = []
    seen = set()
    for block in blocks:
        key = tuple(block.headings)
        if key not in seen:
            seen.add(key)
            heading_paths.append(list(block.headings))

    text = "\n\n".join(block.text for block in blocks).strip()
    context_path = " > ".join(heading_paths[0]) if heading_paths else section["title"]
    embedding_lines = [book["title"], context_path, "", text]
    summary_item = book["summary"]
    citation = f"{book['title']} > {context_path}"
    return {
        "chunk_id": f"{book['slug']}.{section['section_slug']}.{chunk_index:04d}",
        "book_slug": book["slug"],
        "book_title": book["title"],
        "section_id": section["section_id"],
        "section_slug": section["section_slug"],
        "section_title": section["title"],
        "section_order": section["order"],
        "heading_paths": heading_paths,
        "context_path": context_path,
        "block_start": blocks[0].order,
        "block_end": blocks[-1].order,
        "word_count": len(text.split()),
        "char_count": len(text),
        "source_book_path": book["merged_path"].relative_to(ROOT).as_posix(),
        "source_section_path": section["source_path"].relative_to(ROOT).as_posix(),
        "ai_section_path": ai_section_path.relative_to(ROOT).as_posix(),
        "source_name": section["meta"].get("source_name"),
        "source_url": section["meta"].get("source_url"),
        "official_alignment_status": summary_item.get("status"),
        "official_similarity": summary_item.get("overall_similarity"),
        "official_content_overlap": summary_item.get("overall_content_overlap"),
        "official_section_url": section.get("official_url"),
        "official_section_similarity": section.get("official_similarity"),
        "official_section_content_overlap": section.get("official_content_overlap"),
        "official_section_diff_tokens": section.get("official_diff_tokens"),
        "citation": citation,
        "text": text,
        "embedding_text": "\n".join(embedding_lines).strip(),
    }


def build_chunks(book: dict[str, object], section: dict[str, object], ai_section_path: Path) -> list[dict[str, object]]:
    blocks = parse_blocks(section["title"], section["body"])
    if not blocks:
        return []

    chunks: list[dict[str, object]] = []
    current: list[ContentBlock] = []
    current_words = 0
    previous_headings: list[str] | None = None

    for block in blocks:
        block_words = len(block.text.split())
        heading_changed = previous_headings is not None and block.headings != previous_headings
        should_split = False
        if current:
            if current_words + block_words > MAX_WORDS and current_words >= MIN_WORDS:
                should_split = True
            elif heading_changed and current_words >= MIN_WORDS:
                should_split = True
            elif current_words >= TARGET_WORDS and heading_changed:
                should_split = True
        if should_split:
            chunks.append(make_chunk(book, section, len(chunks) + 1, current, ai_section_path))
            current = []
            current_words = 0
        current.append(block)
        current_words += block_words
        previous_headings = block.headings

    if current:
        chunks.append(make_chunk(book, section, len(chunks) + 1, current, ai_section_path))

    for index, chunk in enumerate(chunks):
        chunk["previous_chunk_id"] = chunks[index - 1]["chunk_id"] if index > 0 else None
        chunk["next_chunk_id"] = chunks[index + 1]["chunk_id"] if index + 1 < len(chunks) else None

    return chunks


def write_ai_policy() -> None:
    rows = [
        "# AI Answering Policy",
        "",
        "Bu klasör, `books/` katmanındaki doğrulanmış Risale-i Nur metinlerinden türetilmiş güvenli AI katmanıdır.",
        "",
        "## Zorunlu kurallar",
        "",
        "1. Cevap üretirken öncelik `ai/passages/*.jsonl` ve `ai/books/*/sections/*.md` dosyaları olmalıdır.",
        "2. Her cevap en az bir açık atıf içermelidir: kitap, bölüm ve mümkünse `chunk_id`.",
        "3. Dinî hüküm veya anlam aktarımı yapılırken önce metnin kendisi, sonra kısa açıklama verilmelidir.",
        "4. Belirsiz durumda sentez yapılmaz; `metinde açık dayanak bulunamadı` denir.",
        "5. Farklı pasajlar birleştirilecekse her pasaj ayrı cite edilmelidir.",
        "6. Bir pasaj tek başına yetersizse aynı bölüm içindeki komşu chunk'lar birlikte okunmalıdır.",
        "7. Doğrulanmış kaynak ile çelişen dış kaynaklara göre cevap verilmez.",
        "",
        "## Önerilen retrieval akışı",
        "",
        "1. Soru için önce lexical + semantic retrieval yap.",
        "2. En iyi 5-10 chunk içinden aynı bölümde kümelenenleri topla.",
        "3. Gerekirse `previous_chunk_id` ve `next_chunk_id` ile bağlamı genişlet.",
        "4. Cevabı yalnız doğruladığın chunk'lara dayandır.",
    ]
    (AI_ROOT / "ANSWERING_POLICY.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_ai_readme(catalog: dict[str, object]) -> None:
    rows = [
        "# AI Corpus Layer",
        "",
        "Bu klasör, `books/` altındaki doğrulanmış metinlerin AI retrieval için hazırlanmış yapısal kopyasıdır.",
        "Üst düzey `books/` klasörü insan okuması içindir; bu klasör ise AI sistemlerinin kullanacağı türetilmiş kopyayı içerir.",
        "",
        "## Amaç",
        "",
        "- metni yeniden yazmadan AI dostu bir kopya üretmek",
        "- kitap / bölüm / pasaj düzeyinde stabil kimlik vermek",
        "- cevaplarda güvenilir atıf ve izlenebilir provenans sağlamak",
        "- yanlış yönlendirme riskini azaltmak",
        "",
        "## Yapı",
        "",
        "- `books/` - AI için frontmatter ile zenginleştirilmiş kitap ve bölüm kopyaları",
        "- `manifests/` - kitap bazlı yapısal JSON manifestleri",
        "- `passages/` - retrieval için chunk JSONL dosyaları",
        "- `catalog.json` - tüm AI katmanının üst seviye kataloğu",
        "- `ANSWERING_POLICY.md` - chatbot / retrieval ajanı için güvenlik kuralları",
        "",
        "## Kapsam",
        "",
        f"- Kitap sayısı: **{catalog['book_count']}**",
        f"- Bölüm sayısı: **{catalog['section_count']}**",
        f"- Pasaj sayısı: **{catalog['chunk_count']}**",
        "",
        "## Üretim",
        "",
        "```bash",
        "python3 scripts/build_ai_corpus.py",
        "```",
    ]
    (AI_ROOT / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    if AI_ROOT.exists():
        shutil.rmtree(AI_ROOT)
    AI_BOOKS_ROOT.mkdir(parents=True, exist_ok=True)
    AI_MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)
    AI_PASSAGES_ROOT.mkdir(parents=True, exist_ok=True)

    catalog_books = []
    all_chunks: list[dict[str, object]] = []
    total_sections = 0

    for book in collect_books():
        ai_book_dir = AI_BOOKS_ROOT / str(book["slug"])
        ai_sections_dir = ai_book_dir / "sections"
        ai_sections_dir.mkdir(parents=True, exist_ok=True)

        merged_body = book["merged_path"].read_text(encoding="utf-8")
        merged_meta, merged_body_stripped = parse_frontmatter(merged_body)
        book_frontmatter = {
            "book_id": book["slug"],
            "book_title": book["title"],
            "source_book_path": book["merged_path"].relative_to(ROOT).as_posix(),
            "source_section_dir": book["by_heading_dir"].relative_to(ROOT).as_posix(),
            "source_name": merged_meta.get("source_name") or merged_meta.get("source name"),
            "source_url": merged_meta.get("source_url") or merged_meta.get("source url"),
            "official_alignment_status": book["summary"].get("status"),
            "official_similarity": book["summary"].get("overall_similarity"),
            "official_content_overlap": book["summary"].get("overall_content_overlap"),
            "overlap_sections": book["summary"].get("overlap_sections"),
            "upstream_only_sections": book["summary"].get("upstream_only_sections"),
            "official_only_sections": book["summary"].get("official_only_sections"),
        }
        (ai_book_dir / "book.md").write_text(
            write_frontmatter(book_frontmatter, merged_body_stripped),
            encoding="utf-8",
        )

        section_entries = []
        book_chunks: list[dict[str, object]] = []
        for order, section_path in enumerate(sorted(book["by_heading_dir"].glob("*.md")), start=1):
            raw = section_path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(raw)
            title = extract_title(section_path, body)
            section_slug = slugify(title)
            section_id = f"{book['slug']}.{order:03d}.{section_slug}"
            ai_section_filename = f"{order:03d}-{section_slug}.md"
            ai_section_path = ai_sections_dir / ai_section_filename
            comparison_entry = book["comparison"].get(title_key(title), {})
            section_frontmatter = {
                "book_id": book["slug"],
                "book_title": book["title"],
                "section_id": section_id,
                "section_order": order,
                "section_slug": section_slug,
                "section_title": title,
                "source_section_path": section_path.relative_to(ROOT).as_posix(),
                "source_name": meta.get("source_name") or meta.get("source name"),
                "source_url": meta.get("source_url") or meta.get("source url"),
                "official_alignment_status": book["summary"].get("status"),
                "official_similarity": book["summary"].get("overall_similarity"),
                "official_content_overlap": book["summary"].get("overall_content_overlap"),
                "official_section_url": comparison_entry.get("official_url"),
                "official_section_similarity": comparison_entry.get("similarity"),
                "official_section_content_overlap": comparison_entry.get("content_overlap"),
                "official_section_diff_tokens": comparison_entry.get("diff_tokens"),
            }
            ai_section_path.write_text(write_frontmatter(section_frontmatter, body), encoding="utf-8")
            ai_section_path = normalize_written_path(ai_section_path)

            section = {
                "title": title,
                "order": order,
                "section_id": section_id,
                "section_slug": section_slug,
                "source_path": section_path,
                "body": body.strip(),
                "meta": meta,
                "official_url": comparison_entry.get("official_url"),
                "official_similarity": comparison_entry.get("similarity"),
                "official_content_overlap": comparison_entry.get("content_overlap"),
                "official_diff_tokens": comparison_entry.get("diff_tokens"),
            }
            chunks = build_chunks(book, section, ai_section_path)
            book_chunks.extend(chunks)
            section_entries.append(
                {
                    "section_id": section_id,
                    "section_slug": section_slug,
                    "section_title": title,
                    "section_order": order,
                    "source_section_path": section_path.relative_to(ROOT).as_posix(),
                    "ai_section_path": ai_section_path.relative_to(ROOT).as_posix(),
                    "chunk_count": len(chunks),
                    "first_chunk_id": chunks[0]["chunk_id"] if chunks else None,
                    "last_chunk_id": chunks[-1]["chunk_id"] if chunks else None,
                    "official_section_url": comparison_entry.get("official_url"),
                    "official_section_similarity": comparison_entry.get("similarity"),
                    "official_section_content_overlap": comparison_entry.get("content_overlap"),
                    "official_section_diff_tokens": comparison_entry.get("diff_tokens"),
                }
            )

        passages_path = AI_PASSAGES_ROOT / f"{book['slug']}.jsonl"
        with passages_path.open("w", encoding="utf-8") as handle:
            for chunk in book_chunks:
                handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")

        manifest = {
            "book_id": book["slug"],
            "book_title": book["title"],
            "source_book_path": book["merged_path"].relative_to(ROOT).as_posix(),
            "ai_book_path": (ai_book_dir / "book.md").relative_to(ROOT).as_posix(),
            "passages_path": passages_path.relative_to(ROOT).as_posix(),
            "section_count": len(section_entries),
            "chunk_count": len(book_chunks),
            "official_alignment_status": book["summary"].get("status"),
            "official_similarity": book["summary"].get("overall_similarity"),
            "official_content_overlap": book["summary"].get("overall_content_overlap"),
            "sections": section_entries,
        }
        (AI_MANIFESTS_ROOT / f"{book['slug']}.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        catalog_books.append(
            {
                "book_id": book["slug"],
                "book_title": book["title"],
                "ai_book_path": (ai_book_dir / "book.md").relative_to(ROOT).as_posix(),
                "manifest_path": (AI_MANIFESTS_ROOT / f"{book['slug']}.json").relative_to(ROOT).as_posix(),
                "passages_path": passages_path.relative_to(ROOT).as_posix(),
                "section_count": len(section_entries),
                "chunk_count": len(book_chunks),
                "official_alignment_status": book["summary"].get("status"),
                "official_similarity": book["summary"].get("overall_similarity"),
                "official_content_overlap": book["summary"].get("overall_content_overlap"),
            }
        )
        total_sections += len(section_entries)
        all_chunks.extend(book_chunks)

    all_passages_path = AI_PASSAGES_ROOT / "all-passages.jsonl"
    with all_passages_path.open("w", encoding="utf-8") as handle:
        for chunk in all_chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    catalog = {
        "book_count": len(catalog_books),
        "section_count": total_sections,
        "chunk_count": len(all_chunks),
        "books": catalog_books,
        "all_passages_path": all_passages_path.relative_to(ROOT).as_posix(),
    }
    (AI_ROOT / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_ai_policy()
    write_ai_readme(catalog)
    print(f"Built AI corpus for {len(catalog_books)} books, {total_sections} sections, {len(all_chunks)} chunks.")


if __name__ == "__main__":
    main()
