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
LOCAL_ROOT = ROOT / "books" / "sozler"
LOCAL_SECTIONS = LOCAL_ROOT / "by_heading"
GENERATED_ROOT = ROOT / "generated"
GENERATED_JSON_ROOT = GENERATED_ROOT / "json"
REPORTS_ROOT = ROOT / "reports"
COMPARISON_REPORT_ROOT = REPORTS_ROOT / "comparisons"

INDEX_URL = "https://risaleinur.hizmetvakfi.org/sozler-2/"
USER_AGENT = "Mozilla/5.0 (compatible; CopilotCLI/1.0)"

FILE_PREFIX_RE = re.compile(r"^(?P<order>\d+)\s*[- ]\s*(?P<title>.+)$")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
PAGE_RE = re.compile(r"\[Page\s+\d+\]")
SEPARATOR_RE = re.compile(r"^\s*(?:---|\*\*\*|\*\s*\*\s*\*)\s*$", re.MULTILINE)
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


def normalize_text(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = PAGE_RE.sub(" ", text)
    text = SEPARATOR_RE.sub(" ", text)
    text = text.replace("**", " ").replace("*", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_key(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"\([^)]*\)", "", ascii_only)
    return re.sub(r"[^a-z0-9]+", "", ascii_only)


def extract_local_title(path: Path, raw: str) -> str:
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    match = FILE_PREFIX_RE.match(path.stem)
    if match:
        return match.group("title")
    return path.stem


def load_local_sections() -> dict[str, dict[str, object]]:
    sections: dict[str, dict[str, object]] = {}
    for path in sorted(LOCAL_SECTIONS.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = extract_local_title(path, raw)
        sections[title_key(title)] = {
            "title": title,
            "path": path.relative_to(ROOT).as_posix(),
            "normalized": normalize_text(raw),
        }
    return sections


def scrape_official_sections() -> dict[str, dict[str, object]]:
    html = fetch_html(INDEX_URL)
    soup = BeautifulSoup(html, "html.parser")
    current_menu = soup.select_one("li.current-menu-item.menu-item-has-children")
    if current_menu is None:
        raise RuntimeError("Could not locate Sözler menu on official index page.")

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

        text = article.get_text("\n", strip=True)
        normalized = normalize_text(text)
        key = title_key(heading.get_text(" ", strip=True))
        sections[key] = {
            "title": heading.get_text(" ", strip=True),
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
        local_chunk = " ".join(left[left_start : min(left_end, left_start + window)]).strip()
        official_chunk = " ".join(right[right_start : min(right_end, right_start + window)]).strip()
        if not local_chunk and not official_chunk:
            continue
        snippets.append(
            {
                "type": tag,
                "local": local_chunk,
                "official": official_chunk,
            }
        )
        if len(snippets) >= limit:
            break
    return snippets


def write_outputs(
    official_sections: dict[str, dict[str, object]],
    comparisons: list[dict[str, object]],
    local_only: list[dict[str, object]],
    official_only: list[dict[str, object]],
    overall_similarity: float,
    overall_overlap: float,
    total_diff_tokens: int,
) -> None:
    GENERATED_JSON_ROOT.mkdir(parents=True, exist_ok=True)
    COMPARISON_REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    payload = {
        "source": {
            "name": "Hizmet Vakfı official Sözler site",
            "index_url": INDEX_URL,
            "section_count": len(official_sections),
        },
        "overall_similarity": overall_similarity,
        "overall_content_overlap": overall_overlap,
        "overlap_sections": len(comparisons),
        "total_diff_tokens": total_diff_tokens,
        "local_only_sections": local_only,
        "official_only_sections": official_only,
        "sections": comparisons,
    }
    (GENERATED_JSON_ROOT / "official-sozler-scrape.json").write_text(
        json.dumps(official_sections, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (GENERATED_JSON_ROOT / "sozler-public-comparison.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    sorted_sections = sorted(comparisons, key=lambda item: item["similarity"])
    worst_sections = sorted_sections[:10]
    biggest_gap = max(comparisons, key=lambda item: item["diff_tokens"]) if comparisons else None

    rows = [
        "# Sözler Public Comparison Report",
        "",
        "- Doğrulanmış kitap kaynağı: `books/sozler/Sozler.md`",
        "- Public kaynak: resmi Hizmet Vakfı `Sözler` sayfaları",
        f"- Public index: {INDEX_URL}",
        "- Yöntem: resmi site menüsündeki tüm `Sözler` bağlantıları scrape edilip bölüm bazlı normalize token karşılaştırması yapıldı",
        "",
        "## Summary",
        "",
        f"- Public tarafta bulunan bölüm sayısı: **{len(official_sections)}**",
        f"- Ortak bölüm sayısı: **{len(comparisons)}**",
        f"- Genel sıra-duyarlı benzerlik: **{overall_similarity:.4f}**",
        f"- Genel içerik örtüşmesi: **{overall_overlap:.4f}**",
        f"- Toplam farklı token: **{total_diff_tokens}**",
        f"- Yalnız yerelde bulunan bölümler: **{len(local_only)}**",
        f"- Yalnız public tarafta bulunan bölümler: **{len(official_only)}**",
    ]

    if biggest_gap is not None:
        rows.append(
            f"- En büyük fark bloğu: **{biggest_gap['title']}** "
            f"({biggest_gap['diff_tokens']} farklı token, benzerlik {biggest_gap['similarity']:.4f})"
        )

    rows.extend(["", "## Coverage gaps", ""])

    if local_only:
        rows.append("### Local-only sections")
        rows.append("")
        for item in local_only:
            rows.append(f"- {item['title']} (`{item['path']}`)")
        rows.append("")

    if official_only:
        rows.append("### Official-only sections")
        rows.append("")
        for item in official_only:
            rows.append(f"- {item['title']} ({item['url']})")
        rows.append("")

    rows.extend(
        [
            "## Full section table",
            "",
            "| Bölüm | Sıra benzerliği | İçerik örtüşmesi | Fark tokenı | Yerel | Public |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )

    for item in sorted_sections:
        rows.append(
            f"| {item['title']} | {item['similarity']:.4f} | {item['content_overlap']:.4f} | {item['diff_tokens']} | "
            f"`{item['local_path']}` | [public]({item['official_url']}) |"
        )

    rows.extend(["", "## Representative divergence snippets", ""])

    for item in worst_sections[:5]:
        rows.append(f"### {item['title']}")
        rows.append("")
        rows.append(
            f"- Sıra benzerliği: **{item['similarity']:.4f}** · İçerik örtüşmesi: **{item['content_overlap']:.4f}** · Fark tokenı: **{item['diff_tokens']}** · Public: {item['official_url']}"
        )
        rows.append("")
        for idx, snippet in enumerate(item["snippets"], start=1):
            rows.append(f"{idx}. `{snippet['type']}`")
            rows.append(f"   - Yerel: {snippet['local'] or '(boş)'}")
            rows.append(f"   - Public: {snippet['official'] or '(boş)'}")
        rows.append("")

    rows.extend(
        [
            "## Notes",
            "",
            "- `Sıra benzerliği`, token dizilerinin sırasını da dikkate alır; başlık/ara başlık yer değişimleri ve uzun blok kaymaları bu metriği sert düşürebilir.",
            "- `İçerik örtüşmesi`, token çoklu-küme kesişimine bakar; aynı malzemenin farklı akış veya imla ile verildiği durumları daha doğru yansıtır.",
            "- Karşılaştırmada sayfa işaretleri ve markdown ayraçları temizlendi; anlamlı metin gövdesi token bazında ölçüldü.",
            "- Resmi site modern imla, HTML yapılandırması ve bazı yerlerde başlık/ara başlık ayrışmaları içerdiği için ham metin eşleşmesi değil normalize içerik uyumu ölçüldü.",
            "- Ayrıntılı veri `generated/json/sozler-public-comparison.json` içinde tutulur; scrape çıktısı `generated/json/official-sozler-scrape.json` dosyasına yazılır.",
        ]
    )

    (COMPARISON_REPORT_ROOT / "sozler-public-comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    local_sections = load_local_sections()
    official_sections = scrape_official_sections()

    shared_keys = sorted(set(local_sections) & set(official_sections))
    local_only = [local_sections[key] for key in sorted(set(local_sections) - set(official_sections))]
    official_only = [official_sections[key] for key in sorted(set(official_sections) - set(local_sections))]

    comparisons: list[dict[str, object]] = []
    total_diff_tokens = 0
    weighted_similarity_total = 0.0
    weighted_overlap_total = 0.0
    weighted_length_total = 0

    for key in shared_keys:
        local = local_sections[key]
        official = official_sections[key]
        local_tokens = str(local["normalized"]).split()
        official_tokens = str(official["normalized"]).split()
        similarity = difflib.SequenceMatcher(None, local_tokens, official_tokens).ratio()
        overlap = content_overlap(local_tokens, official_tokens)
        diff_tokens = token_diff_count(local_tokens, official_tokens)
        weight = max(len(local_tokens), len(official_tokens))
        snippets = diff_snippets(local_tokens, official_tokens)

        comparisons.append(
            {
                "title": local["title"],
                "local_path": local["path"],
                "official_url": official["url"],
                "similarity": similarity,
                "content_overlap": overlap,
                "diff_tokens": diff_tokens,
                "local_tokens": len(local_tokens),
                "official_tokens": len(official_tokens),
                "snippets": snippets,
            }
        )
        total_diff_tokens += diff_tokens
        weighted_similarity_total += similarity * weight
        weighted_overlap_total += overlap * weight
        weighted_length_total += weight

    overall_similarity = weighted_similarity_total / weighted_length_total if weighted_length_total else 1.0
    overall_overlap = weighted_overlap_total / weighted_length_total if weighted_length_total else 1.0
    write_outputs(
        official_sections=official_sections,
        comparisons=comparisons,
        local_only=local_only,
        official_only=official_only,
        overall_similarity=overall_similarity,
        overall_overlap=overall_overlap,
        total_diff_tokens=total_diff_tokens,
    )
    print(f"Scraped {len(official_sections)} official sections; compared {len(comparisons)} overlapping sections.")


if __name__ == "__main__":
    main()
