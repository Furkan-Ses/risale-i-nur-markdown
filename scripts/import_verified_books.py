#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = ROOT / "sources" / "official-markdown-mirror" / "obsidian-markdown"
BOOKS_ROOT = ROOT / "books"
SUMMARY_PATH = ROOT / "generated" / "json" / "all-upstream-public-summary.json"

ACCEPTED_STATUSES = {"very-high", "almost-identical"}
PROTECTED_EXISTING = {"sozler"}

BOOK_DIR_RE = re.compile(r"^(?P<order>\d+)\s+(?P<title>.+)$")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
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

MERGED_NAME_MAP = {
    "sozler": "Sozler",
    "mektubat": "Mektubat",
    "lemalar": "Lemalar",
    "sualar": "Sualar",
    "tarihce-i-hayat": "Tarihce-i Hayat",
    "mesnevi-i-nuriye": "Mesnevi-i Nuriye",
    "isaratul-icaz": "Isaratul-icaz",
    "sikke-i-tasdik-i-gaybi": "Sikke-i Tasdik-i Gaybi",
    "barla-lahikasi": "Barla Lahikasi",
    "kastamonu-lahikasi": "Kastamonu Lahikasi",
    "emirdag-lahikasi-1": "Emirdag Lahikasi 1",
    "emirdag-lahikasi-2": "Emirdag Lahikasi 2",
    "asa-yi-musa": "Asa-yi Musa",
    "muhakemat": "Muhakemat",
    "kucuk-kitaplar": "Kucuk Kitaplar",
}


def slugify(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"[^a-z0-9]+", "-", ascii_only)
    return ascii_only.strip("-")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).strip()


def load_summary() -> dict[str, dict[str, object]]:
    payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    return {str(item["slug"]): item for item in payload["books"]}


def load_upstream_dirs() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in sorted(UPSTREAM_ROOT.iterdir()):
        if not path.is_dir():
            continue
        match = BOOK_DIR_RE.match(path.name)
        if not match:
            continue
        slug = slugify(match.group("title"))
        mapping[slug] = path
    return mapping


def write_readme(
    canonical_dir: Path,
    merged_name: str,
    upstream_dir: Path,
    summary_item: dict[str, object],
) -> None:
    rows = [
        f"# {merged_name}",
        "",
        f"Bu klasör, **{merged_name}** metninin repo içindeki doğrulanmış okuma kopyasını içerir.",
        "",
        "## İçerik",
        "",
        f"- `{merged_name}.md` - tüm bölüm dosyalarının tek dosyada birleşik sürümü",
        "- `by_heading/` - bölüm dosyaları",
        "",
        "## Provenans",
        "",
        f"- Başlangıç kopyası, `{upstream_dir.relative_to(ROOT).as_posix()}` altındaki kaynak aynasından alınmıştır.",
        "- Upstream set, resmi Hizmet Vakfı public kaynağı ile karşılaştırılmıştır.",
        f"- Genel sıra benzerliği: **{float(summary_item['overall_similarity']):.4f}**",
        f"- Genel içerik örtüşmesi: **{float(summary_item['overall_content_overlap']):.4f}**",
        f"- Karşılaştırma durumu: **{summary_item['status']}**",
        f"- Ortak bölüm sayısı: **{summary_item['overlap_sections']}**",
        f"- Upstream-only bölüm: **{summary_item['upstream_only_sections']}**",
        f"- Official-only bölüm: **{summary_item['official_only_sections']}**",
        "",
        "## Düzenleme kuralları",
        "",
        "- Dosya adlarını ve `by_heading/` yapısını değiştirmeyin.",
        "- Gerekçesiz toplu biçim değişikliği yapmayın.",
        "- Metin düzeltmesi yapılırsa dayanak belirtin: resmi public metin, baskı karşılaştırması veya güvenilir referans.",
        "- Türkçe ve Arapça satırları UTF-8 olarak koruyun.",
    ]
    (canonical_dir / "README.source.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def import_book(slug: str, upstream_dir: Path, summary_item: dict[str, object], overwrite: bool) -> str:
    canonical_dir = BOOKS_ROOT / slug
    if canonical_dir.exists() and slug in PROTECTED_EXISTING and not overwrite:
        return f"skip-protected:{slug}"
    if canonical_dir.exists() and not overwrite:
        return f"skip-existing:{slug}"

    if canonical_dir.exists():
        shutil.rmtree(canonical_dir)

    by_heading_dir = canonical_dir / "by_heading"
    by_heading_dir.mkdir(parents=True, exist_ok=True)

    section_paths = []
    for path in sorted(upstream_dir.glob("*.md")):
        if path.stem.startswith("00"):
            continue
        destination = by_heading_dir / path.name
        shutil.copy2(path, destination)
        section_paths.append(destination)

    merged_name = MERGED_NAME_MAP.get(slug, upstream_dir.name)
    merged_path = canonical_dir / f"{merged_name}.md"
    merged_chunks = []
    for path in section_paths:
        merged_chunks.append(strip_frontmatter(path.read_text(encoding="utf-8")))
    merged_path.write_text("\n\n".join(chunk for chunk in merged_chunks if chunk).strip() + "\n", encoding="utf-8")

    write_readme(canonical_dir, merged_name, upstream_dir, summary_item)
    return f"imported:{slug}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing canonical directories.")
    args = parser.parse_args()

    summary = load_summary()
    upstream_dirs = load_upstream_dirs()
    BOOKS_ROOT.mkdir(parents=True, exist_ok=True)

    results = []
    for slug, item in summary.items():
        if str(item["status"]) not in ACCEPTED_STATUSES:
            results.append(f"skip-unaccepted:{slug}")
            continue
        upstream_dir = upstream_dirs.get(slug)
        if upstream_dir is None:
            results.append(f"skip-missing-upstream:{slug}")
            continue
        results.append(import_book(slug, upstream_dir, item, overwrite=args.overwrite))

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
