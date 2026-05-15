#!/usr/bin/env python3

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = ROOT / "sources" / "official-markdown-mirror" / "obsidian-markdown"
GENERATED_JSON_ROOT = ROOT / "generated" / "json"
GENERATED_JSON_BOOK_ROOT = GENERATED_JSON_ROOT / "books"
REPORT_ROOT = ROOT / "reports" / "comparisons"
REPORT_BOOK_ROOT = REPORT_ROOT / "books"

SITE_ROOT = "https://risaleinur.hizmetvakfi.org/"
USER_AGENT = "Mozilla/5.0 (compatible; CopilotCLI/1.0)"

BOOK_URLS = {
    "sozler": "https://risaleinur.hizmetvakfi.org/sozler-2/",
    "mektubat": "https://risaleinur.hizmetvakfi.org/mektubat/",
    "lemalar": "https://risaleinur.hizmetvakfi.org/lemalar/",
    "sualar": "https://risaleinur.hizmetvakfi.org/sualar/",
    "tarihce-i-hayat": "https://risaleinur.hizmetvakfi.org/tarihce-i-hayat/",
    "mesnevi-i-nuriye": "https://risaleinur.hizmetvakfi.org/mesnevi-i-nuriye/",
    "isaratul-icaz": "https://risaleinur.hizmetvakfi.org/isaratul-icaz/",
    "sikke-i-tasdik-i-gaybi": "https://risaleinur.hizmetvakfi.org/sikke-i-tasdik-i-gaybi/",
    "barla-lahikasi": "https://risaleinur.hizmetvakfi.org/barla-lahikasi/",
    "kastamonu-lahikasi": "https://risaleinur.hizmetvakfi.org/kastamonu-lahikasi/",
    "emirdag-lahikasi-1": "https://risaleinur.hizmetvakfi.org/emirdag-lahikasi-i/",
    "emirdag-lahikasi-2": "https://risaleinur.hizmetvakfi.org/emirdag-lahikasi-ii/",
    "asa-yi-musa": "https://risaleinur.hizmetvakfi.org/asa-yi-musa/",
    "muhakemat": "https://risaleinur.hizmetvakfi.org/muhakemat/",
    "kucuk-kitaplar": "https://risaleinur.hizmetvakfi.org/kucuk-kitaplar/",
}

BOOK_DIR_RE = re.compile(r"^(?P<order>\d+)\s+(?P<title>.+)$")
FILE_ORDER_RE = re.compile(r"^(?P<order>\d+)\s+(?P<title>.+)$")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
PAGE_RE = re.compile(r"\[Page\s+\d+\]")
FOOTNOTE_RE = re.compile(r"\[\^[^\]]+\]")
SEPARATOR_RE = re.compile(r"^\s*(?:---|\*\*\*|\*\s*\*\s*\*)\s*$", re.MULTILINE)
TAG_RE = re.compile(r"<[^>]+>")
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


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    return urlopen(req, timeout=60).read().decode("utf-8", errors="ignore")


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


def normalize_text(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = TAG_RE.sub(" ", text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = PAGE_RE.sub(" ", text)
    text = FOOTNOTE_RE.sub(" ", text)
    text = SEPARATOR_RE.sub(" ", text)
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = text.replace("**", " ").replace("*", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(path: Path, raw: str) -> str:
    body = FRONTMATTER_RE.sub("", raw, count=1)
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    match = FILE_ORDER_RE.match(path.stem)
    if match:
        return match.group("title")
    return path.stem


def load_upstream_books() -> list[dict[str, object]]:
    books: list[dict[str, object]] = []
    for book_dir in sorted(UPSTREAM_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue
        match = BOOK_DIR_RE.match(book_dir.name)
        if not match:
            continue

        title = match.group("title")
        slug = slugify(title)
        if slug not in BOOK_URLS:
            continue

        sections: dict[str, dict[str, object]] = {}
        for path in sorted(book_dir.glob("*.md")):
            if path.stem.startswith("00"):
                continue
            raw = path.read_text(encoding="utf-8")
            section_title = extract_title(path, raw)
            sections[title_key(section_title)] = {
                "title": section_title,
                "path": path.relative_to(ROOT).as_posix(),
                "normalized": normalize_text(raw),
            }

        books.append(
            {
                "title": title,
                "slug": slug,
                "path": book_dir.relative_to(ROOT).as_posix(),
                "official_index_url": BOOK_URLS[slug],
                "sections": sections,
            }
        )
    return books


def scrape_official_sections(index_url: str) -> dict[str, dict[str, object]]:
    html = fetch_html(index_url)
    soup = BeautifulSoup(html, "html.parser")
    current_menu = soup.select_one("li.current-menu-item.menu-item-has-children")
    if current_menu is None:
        raise RuntimeError(f"Could not locate official menu on {index_url}")

    sections: dict[str, dict[str, object]] = {}
    for link in current_menu.select("ul.sub-menu a"):
        title = link.get_text(" ", strip=True)
        url = link.get("href")
        if not title or not url:
            continue

        section_html = fetch_html(url)
        section_soup = BeautifulSoup(section_html, "html.parser")
        article = section_soup.select_one(".entry-content")
        heading = section_soup.select_one("h1.entry-title")
        if article is None or heading is None:
            continue

        normalized = normalize_text(article.get_text("\n", strip=True))
        heading_text = heading.get_text(" ", strip=True)
        sections[title_key(heading_text)] = {
            "title": heading_text,
            "url": url,
            "normalized": normalized,
            "token_count": len(normalized.split()),
        }

    return sections


def token_diff_count(left: list[str], right: list[str]) -> int:
    matcher = difflib.SequenceMatcher(None, left, right)
    count = 0
    for tag, left_start, left_end, right_start, right_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        count += max(left_end - left_start, right_end - right_start)
    return count


def content_overlap(left: list[str], right: list[str]) -> float:
    left_counter = Counter(left)
    right_counter = Counter(right)
    intersection = sum((left_counter & right_counter).values())
    return intersection / max(len(left), len(right)) if max(len(left), len(right)) else 1.0


def diff_snippets(left: list[str], right: list[str], limit: int = 3, window: int = 28) -> list[dict[str, str]]:
    matcher = difflib.SequenceMatcher(None, left, right)
    snippets: list[dict[str, str]] = []
    for tag, left_start, left_end, right_start, right_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        upstream_chunk = " ".join(left[left_start : min(left_end, left_start + window)]).strip()
        official_chunk = " ".join(right[right_start : min(right_end, right_start + window)]).strip()
        if not upstream_chunk and not official_chunk:
            continue
        snippets.append({"type": tag, "upstream": upstream_chunk, "official": official_chunk})
        if len(snippets) >= limit:
            break
    return snippets


def classify_book(overlap: float, similarity: float, upstream_only: int, official_only: int) -> str:
    if upstream_only == 0 and official_only == 0 and overlap >= 0.995 and similarity >= 0.995:
        return "almost-identical"
    if overlap >= 0.99 and similarity >= 0.99:
        return "very-high"
    if overlap >= 0.97:
        return "high"
    if overlap >= 0.94:
        return "review-needed"
    return "low"


def write_book_outputs(book: dict[str, object], payload: dict[str, object]) -> None:
    GENERATED_JSON_BOOK_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_BOOK_ROOT.mkdir(parents=True, exist_ok=True)
    slug = str(book["slug"])

    (GENERATED_JSON_BOOK_ROOT / f"{slug}-official-scrape.json").write_text(
        json.dumps(payload["official_sections"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    trimmed_payload = dict(payload)
    trimmed_payload.pop("official_sections", None)
    (GENERATED_JSON_BOOK_ROOT / f"{slug}-public-comparison.json").write_text(
        json.dumps(trimmed_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    comparisons = list(payload["sections"])
    worst_sections = sorted(comparisons, key=lambda item: item["similarity"])[:8]

    rows = [
        f"# {book['title']} Public Comparison",
        "",
        f"- Upstream kaynak: `{book['path']}`",
        "- Public kaynak: resmi Hizmet Vakfı sayfaları",
        f"- Public index: {book['official_index_url']}",
        "",
        "## Summary",
        "",
        f"- Public bölüm sayısı: **{payload['source']['section_count']}**",
        f"- Ortak bölüm sayısı: **{payload['overlap_sections']}**",
        f"- Genel sıra-duyarlı benzerlik: **{payload['overall_similarity']:.4f}**",
        f"- Genel içerik örtüşmesi: **{payload['overall_content_overlap']:.4f}**",
        f"- Toplam farklı token: **{payload['total_diff_tokens']}**",
        f"- Yalnız upstream bölümleri: **{len(payload['upstream_only_sections'])}**",
        f"- Yalnız public bölümleri: **{len(payload['official_only_sections'])}**",
        f"- Durum: **{payload['status']}**",
        "",
    ]

    if payload["upstream_only_sections"]:
        rows.extend(["### Upstream-only", ""])
        for item in payload["upstream_only_sections"]:
            rows.append(f"- {item['title']} (`{item['path']}`)")
        rows.append("")

    if payload["official_only_sections"]:
        rows.extend(["### Official-only", ""])
        for item in payload["official_only_sections"]:
            rows.append(f"- {item['title']} ({item['url']})")
        rows.append("")

    rows.extend(
        [
            "## Lowest-similarity overlapping sections",
            "",
            "| Bölüm | Sıra benzerliği | İçerik örtüşmesi | Fark tokenı | Upstream | Public |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for item in worst_sections:
        rows.append(
            f"| {item['title']} | {item['similarity']:.4f} | {item['content_overlap']:.4f} | {item['diff_tokens']} | "
            f"`{item['upstream_path']}` | [public]({item['official_url']}) |"
        )

    rows.extend(["", "## Representative divergence snippets", ""])
    for item in worst_sections[:4]:
        rows.append(f"### {item['title']}")
        rows.append("")
        rows.append(
            f"- Sıra benzerliği: **{item['similarity']:.4f}** · İçerik örtüşmesi: **{item['content_overlap']:.4f}** · Fark tokenı: **{item['diff_tokens']}**"
        )
        rows.append("")
        for idx, snippet in enumerate(item["snippets"], start=1):
            rows.append(f"{idx}. `{snippet['type']}`")
            rows.append(f"   - Upstream: {snippet['upstream'] or '(boş)'}")
            rows.append(f"   - Public: {snippet['official'] or '(boş)'}")
        rows.append("")

    (REPORT_BOOK_ROOT / f"{slug}-public-comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def compare_book(book: dict[str, object]) -> dict[str, object]:
    official_sections = scrape_official_sections(str(book["official_index_url"]))
    upstream_sections = dict(book["sections"])

    shared_keys = sorted(set(upstream_sections) & set(official_sections))
    upstream_only = [upstream_sections[key] for key in sorted(set(upstream_sections) - set(official_sections))]
    official_only = [official_sections[key] for key in sorted(set(official_sections) - set(upstream_sections))]

    comparisons: list[dict[str, object]] = []
    total_diff_tokens = 0
    weighted_similarity_total = 0.0
    weighted_overlap_total = 0.0
    weighted_length_total = 0

    for key in shared_keys:
        upstream = upstream_sections[key]
        official = official_sections[key]
        upstream_tokens = str(upstream["normalized"]).split()
        official_tokens = str(official["normalized"]).split()
        similarity = difflib.SequenceMatcher(None, upstream_tokens, official_tokens).ratio()
        overlap = content_overlap(upstream_tokens, official_tokens)
        diff_tokens = token_diff_count(upstream_tokens, official_tokens)
        weight = max(len(upstream_tokens), len(official_tokens))

        comparisons.append(
            {
                "title": upstream["title"],
                "upstream_path": upstream["path"],
                "official_url": official["url"],
                "similarity": similarity,
                "content_overlap": overlap,
                "diff_tokens": diff_tokens,
                "upstream_tokens": len(upstream_tokens),
                "official_tokens": len(official_tokens),
                "snippets": diff_snippets(upstream_tokens, official_tokens),
            }
        )
        total_diff_tokens += diff_tokens
        weighted_similarity_total += similarity * weight
        weighted_overlap_total += overlap * weight
        weighted_length_total += weight

    overall_similarity = weighted_similarity_total / weighted_length_total if weighted_length_total else 1.0
    overall_overlap = weighted_overlap_total / weighted_length_total if weighted_length_total else 1.0
    status = classify_book(overall_overlap, overall_similarity, len(upstream_only), len(official_only))

    payload = {
        "book": {"title": book["title"], "slug": book["slug"], "path": book["path"]},
        "source": {
            "name": "Hizmet Vakfı official site",
            "index_url": book["official_index_url"],
            "section_count": len(official_sections),
        },
        "overall_similarity": overall_similarity,
        "overall_content_overlap": overall_overlap,
        "overlap_sections": len(comparisons),
        "total_diff_tokens": total_diff_tokens,
        "upstream_only_sections": upstream_only,
        "official_only_sections": official_only,
        "status": status,
        "sections": comparisons,
        "official_sections": official_sections,
    }
    write_book_outputs(book, payload)
    return payload


def write_summary(results: list[dict[str, object]]) -> None:
    GENERATED_JSON_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    weighted_similarity_total = 0.0
    weighted_overlap_total = 0.0
    weighted_weight_total = 0
    total_upstream_only = 0
    total_official_only = 0

    summary_books = []
    for item in results:
        weight = max(item["overlap_sections"], 1)
        weighted_similarity_total += item["overall_similarity"] * weight
        weighted_overlap_total += item["overall_content_overlap"] * weight
        weighted_weight_total += weight
        total_upstream_only += len(item["upstream_only_sections"])
        total_official_only += len(item["official_only_sections"])
        summary_books.append(
            {
                "title": item["book"]["title"],
                "slug": item["book"]["slug"],
                "overall_similarity": item["overall_similarity"],
                "overall_content_overlap": item["overall_content_overlap"],
                "overlap_sections": item["overlap_sections"],
                "total_diff_tokens": item["total_diff_tokens"],
                "upstream_only_sections": len(item["upstream_only_sections"]),
                "official_only_sections": len(item["official_only_sections"]),
                "status": item["status"],
            }
        )

    payload = {
        "book_count": len(results),
        "overall_similarity": weighted_similarity_total / weighted_weight_total if weighted_weight_total else 1.0,
        "overall_content_overlap": weighted_overlap_total / weighted_weight_total if weighted_weight_total else 1.0,
        "total_upstream_only_sections": total_upstream_only,
        "total_official_only_sections": total_official_only,
        "books": summary_books,
    }

    (GENERATED_JSON_ROOT / "all-upstream-public-summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    rows = [
        "# All Upstream Books vs Official Public Source",
        "",
        f"- Karşılaştırılan upstream kitap sayısı: **{payload['book_count']}**",
        f"- Genel ağırlıklı sıra-duyarlı benzerlik: **{payload['overall_similarity']:.4f}**",
        f"- Genel ağırlıklı içerik örtüşmesi: **{payload['overall_content_overlap']:.4f}**",
        f"- Toplam upstream-only bölüm: **{payload['total_upstream_only_sections']}**",
        f"- Toplam official-only bölüm: **{payload['total_official_only_sections']}**",
        "",
        "| Kitap | Sıra benzerliği | İçerik örtüşmesi | Ortak bölüm | Upstream-only | Official-only | Durum | Rapor |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    for item in sorted(summary_books, key=lambda current: current["overall_content_overlap"]):
        report_path = f"books/{item['slug']}-public-comparison.md"
        rows.append(
            f"| {item['title']} | {item['overall_similarity']:.4f} | {item['overall_content_overlap']:.4f} | "
            f"{item['overlap_sections']} | {item['upstream_only_sections']} | {item['official_only_sections']} | "
            f"{item['status']} | [{item['slug']}]({report_path}) |"
        )

    (REPORT_ROOT / "all-upstream-public-summary.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    results = []
    for book in load_upstream_books():
        result = compare_book(book)
        results.append(result)
        print(
            f"{book['title']}: overlap={result['overall_content_overlap']:.4f} "
            f"similarity={result['overall_similarity']:.4f} "
            f"shared={result['overlap_sections']} "
            f"status={result['status']}"
        )

    write_summary(results)
    print(f"Compared {len(results)} books against official public sources.")


if __name__ == "__main__":
    main()
