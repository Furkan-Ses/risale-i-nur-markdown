#!/usr/bin/env python3

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = ROOT / "canonical" / "furkan" / "sozler"
LOCAL_SECTIONS = LOCAL_ROOT / "by_heading"
UPSTREAM_ROOT = ROOT / "upstream" / "alitekdemir" / "obsidian-markdown" / "01 Sözler"
GENERATED_ROOT = ROOT / "generated"
GENERATED_JSON_ROOT = GENERATED_ROOT / "json"
GENERATED_TEXT_ROOT = GENERATED_ROOT / "text"
REPORTS_ROOT = ROOT / "reports"
COMPARISON_REPORT_ROOT = REPORTS_ROOT / "comparisons"


FILE_PREFIX_RE = re.compile(r"^(?P<order>\d+)\s*[- ]\s*(?P<title>.+)$")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
PAGE_RE = re.compile(r"\[Page\s+\d+\]")
FOOTNOTE_RE = re.compile(r"\[\^\d+\]")
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def html_to_text(text: str) -> str:
    text = text.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    text = text.replace("</p>", "\n").replace("<p>", "\n")
    text = re.sub(r"<p[^>]*>", "\n", text)
    text = TAG_RE.sub("", text)
    return text


def normalize_for_compare(text: str) -> str:
    text = strip_frontmatter(text)
    text = html_to_text(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
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


def tokenize(text: str) -> list[str]:
    return text.split()


def extract_title(path: Path, text: str) -> str:
    for line in normalize_for_compare(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    match = FILE_PREFIX_RE.match(path.stem)
    if match:
        return match.group("title")
    return path.stem


def title_key(value: str) -> str:
    value = value.translate(TRANSLATION_TABLE)
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_only = re.sub(r"\([^)]*\)", "", ascii_only)
    return re.sub(r"[^a-z0-9]+", "", ascii_only)


def load_local_sections() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted(LOCAL_SECTIONS.glob("*.md")):
        raw = read_text(path)
        title = extract_title(path, raw)
        result[title_key(title)] = {
            "title": title,
            "path": path.relative_to(ROOT).as_posix(),
            "normalized": normalize_for_compare(raw),
        }
    return result


def load_upstream_sections() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted(UPSTREAM_ROOT.glob("*.md")):
        if path.stem.startswith("00"):
            continue
        raw = read_text(path)
        title = extract_title(path, raw)
        result[title_key(title)] = {
            "title": title,
            "path": path.relative_to(ROOT).as_posix(),
            "normalized": normalize_for_compare(raw),
        }
    return result


def token_diff_count(left: list[str], right: list[str]) -> int:
    matcher = difflib.SequenceMatcher(None, left, right)
    count = 0
    for tag, left_start, left_end, right_start, right_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        count += max(left_end - left_start, right_end - right_start)
    return count


def merged_upstream_text(upstream_sections: dict[str, dict[str, object]], order: list[str]) -> str:
    chunks = [upstream_sections[key]["normalized"] for key in order]
    merged = "\n\n".join(chunks).strip() + "\n"
    GENERATED_TEXT_ROOT.mkdir(parents=True, exist_ok=True)
    (GENERATED_TEXT_ROOT / "ali-sozler-merged.md").write_text(merged, encoding="utf-8")
    return merged


def write_outputs(
    comparisons: list[dict[str, object]],
    local_only: list[dict[str, object]],
    upstream_only: list[dict[str, object]],
    overall_similarity: float,
    total_diff_tokens: int,
) -> None:
    GENERATED_JSON_ROOT.mkdir(parents=True, exist_ok=True)
    COMPARISON_REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    payload = {
        "overall_similarity": overall_similarity,
        "overlap_sections": len(comparisons),
        "total_diff_tokens": total_diff_tokens,
        "local_only_sections": local_only,
        "upstream_only_sections": upstream_only,
        "sections": comparisons,
    }
    (GENERATED_JSON_ROOT / "sozler-comparison.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    worst_sections = sorted(comparisons, key=lambda item: item["similarity"])[:10]
    largest_gap = max(comparisons, key=lambda item: item["diff_tokens"]) if comparisons else None

    rows = [
        "# Sözler Comparison Report",
        "",
        "- Yerel güvenilir kaynak: `canonical/furkan/sozler/Sozler.md`",
        "- Upstream kaynak: `upstream/alitekdemir/obsidian-markdown/01 Sözler/`",
        "- Karşılaştırma yöntemi: frontmatter ve HTML etiketleri temizlenmiş, bölüm bazlı normalize metin karşılaştırması",
        "",
        "## Summary",
        "",
        f"- Ortak bölüm sayısı: **{len(comparisons)}**",
        f"- Genel benzerlik oranı: **{overall_similarity:.4f}**",
        f"- Toplam farklı token: **{total_diff_tokens}**",
        f"- Yalnız yerelde bulunan bölümler: **{len(local_only)}**",
        f"- Yalnız upstream'de bulunan bölümler: **{len(upstream_only)}**",
        "",
    ]

    if largest_gap is not None:
        rows.append(
            f"- En büyük fark bloğu: **{largest_gap['title']}** "
            f"({largest_gap['diff_tokens']} farklı token, benzerlik {largest_gap['similarity']:.4f})"
        )
        rows.append("")

    if local_only:
        rows.append("### Local-only sections")
        rows.append("")
        for item in local_only:
            rows.append(f"- {item['title']} (`{item['path']}`)")
        rows.append("")

    if upstream_only:
        rows.append("### Upstream-only sections")
        rows.append("")
        for item in upstream_only:
            rows.append(f"- {item['title']} (`{item['path']}`)")
        rows.append("")

    rows.extend(
        [
            "## Lowest-similarity overlapping sections",
            "",
            "| Bölüm | Benzerlik | Fark tokenı | Yerel | Upstream |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )

    for item in worst_sections:
        rows.append(
            f"| {item['title']} | {item['similarity']:.4f} | {item['diff_tokens']} | "
            f"`{item['local_path']}` | `{item['upstream_path']}` |"
        )

    rows.append("")
    rows.append("## Notes")
    rows.append("")
    rows.append("- `Kapak ve Giriş` ile `Anglikan Kilisesine Cevab` yalnız yerel kanonik sette bulunduğu için genel benzerlik hesabına dahil edilmedi.")
    rows.append("- Benzerlik metriği, sayfa işaretleri, markdown başlıkları, HTML etiketleri ve dipnot numaraları temizlendikten sonra token dizileri üzerinden hesaplandı.")
    rows.append("- Upstream birleştirilmiş çıktı `generated/text/ali-sozler-merged.md` dosyasına yazıldı.")
    rows.append("- Ayrıntılı sayısal veri `generated/json/sozler-comparison.json` içinde tutulur.")
    rows.append("")

    (COMPARISON_REPORT_ROOT / "sozler-comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    local_sections = load_local_sections()
    upstream_sections = load_upstream_sections()

    shared_keys = sorted(set(local_sections) & set(upstream_sections))
    local_only = [local_sections[key] for key in sorted(set(local_sections) - set(upstream_sections))]
    upstream_only = [upstream_sections[key] for key in sorted(set(upstream_sections) - set(local_sections))]

    comparisons: list[dict[str, object]] = []
    weighted_similarity_total = 0.0
    weighted_length_total = 0
    total_diff_lines = 0

    for key in shared_keys:
        local = local_sections[key]
        upstream = upstream_sections[key]
        local_tokens = tokenize(str(local["normalized"]))
        upstream_tokens = tokenize(str(upstream["normalized"]))
        similarity = difflib.SequenceMatcher(None, local_tokens, upstream_tokens).ratio()
        diff_tokens = token_diff_count(local_tokens, upstream_tokens)
        weight = max(len(local_tokens), len(upstream_tokens))
        comparisons.append(
            {
                "title": local["title"],
                "local_path": local["path"],
                "upstream_path": upstream["path"],
                "similarity": similarity,
                "diff_tokens": diff_tokens,
            }
        )
        weighted_similarity_total += similarity * weight
        weighted_length_total += weight
        total_diff_lines += diff_tokens

    overall_similarity = weighted_similarity_total / weighted_length_total if weighted_length_total else 1.0

    merged_upstream_text(upstream_sections, shared_keys)
    write_outputs(comparisons, local_only, upstream_only, overall_similarity, total_diff_lines)
    print(f"Compared {len(comparisons)} overlapping sections.")


if __name__ == "__main__":
    main()
