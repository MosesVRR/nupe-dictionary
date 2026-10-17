"""
Read-only audit of potential dictionary entry relationships.

Run from the nupe-dictionary project root:
    python audit_entry_relationships.py

Outputs:
    output/relationship_audit.csv
    output/relationship_audit_summary.txt

This script DOES NOT modify the SQLite database. Its candidates require
human review; it does not merge entries or assert a relationship is correct.
"""
import csv
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_ROOT / "data" / "nupe_dictionary.sqlite3"
OUTPUT_DIR = PROJECT_ROOT / "output"
CSV_PATH = OUTPUT_DIR / "relationship_audit.csv"
SUMMARY_PATH = OUTPUT_DIR / "relationship_audit_summary.txt"

REFERENCE_PATTERNS = [
    ("see_reference", re.compile(r"\bsee\b", re.IGNORECASE)),
    ("cf_reference", re.compile(r"\bcf\.?", re.IGNORECASE)),
    ("compare_reference", re.compile(r"\bcompare\b", re.IGNORECASE)),
    ("under_reference", re.compile(r"\bunder\b", re.IGNORECASE)),
    ("also_reference", re.compile(r"\balso\b", re.IGNORECASE)),
    ("whence_reference", re.compile(r"\bwhence\b", re.IGNORECASE)),
]


def normalize_for_matching(value):
    """Normalize only for comparison; never alter stored values."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        char for char in decomposed
        if unicodedata.category(char) != "Mn"
    ).strip()


def collect_reference_markers(text):
    if not text:
        return []
    return [label for label, pattern in REFERENCE_PATTERNS if pattern.search(text)]


def join_values(values):
    seen = set()
    result = []
    for value in values:
        if value is None:
            continue
        value = str(value).strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return " | ".join(result)


def main():
    if not DATABASE_PATH.exists():
        raise SystemExit(
            f"Database not found: {DATABASE_PATH}\n"
            "Run this script from the nupe-dictionary project root, "
            "or update DATABASE_PATH at the top."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(
        f"file:{DATABASE_PATH.as_posix()}?mode=ro", uri=True
    )
    connection.row_factory = sqlite3.Row

    try:
        entries = connection.execute("""
            SELECT entry_id, record_id, headword, source_printed_page,
                   source_pdf_page, source_file, review_required, human_verified
            FROM entries
            ORDER BY entry_id;
        """).fetchall()

        senses_by_entry = {}
        for row in connection.execute("""
            SELECT entry_id, sense_order, part_of_speech,
                   definition_en, category_code
            FROM senses ORDER BY entry_id, sense_order;
        """):
            senses_by_entry.setdefault(row["entry_id"], []).append(row)

        info_by_entry = {}
        for row in connection.execute("""
            SELECT entry_id, information_order, information
            FROM additional_information
            ORDER BY entry_id, information_order;
        """):
            info_by_entry.setdefault(row["entry_id"], []).append(row["information"])

        alternatives_by_entry = {}
        for row in connection.execute("""
            SELECT entry_id, spelling_order, spelling
            FROM alternative_spellings
            ORDER BY entry_id, spelling_order;
        """):
            alternatives_by_entry.setdefault(row["entry_id"], []).append(row["spelling"])
    finally:
        connection.close()

    # Keep all possible matches; repeated headwords may represent distinct senses.
    normalized_headwords = {}
    exact_headwords = {}
    for entry in entries:
        headword = entry["headword"] or ""
        exact_headwords.setdefault(headword.casefold(), []).append(entry)
        key = normalize_for_matching(headword)
        if key:
            normalized_headwords.setdefault(key, []).append(entry)

    rows_out = []
    counts = Counter()
    target_patterns = [
        re.compile(r"\bsee\s+([^.;,\n]+)", re.IGNORECASE),
        re.compile(r"\bcf\.?\s*([^.;,\n]+)", re.IGNORECASE),
        re.compile(r"\bcompare\s+([^.;,\n]+)", re.IGNORECASE),
    ]

    for entry in entries:
        entry_id = entry["entry_id"]
        headword = entry["headword"] or ""
        senses = senses_by_entry.get(entry_id, [])
        information = info_by_entry.get(entry_id, [])
        alternatives = alternatives_by_entry.get(entry_id, [])
        definitions = join_values(row["definition_en"] for row in senses)
        info_text = join_values(information)
        all_text = " | ".join(x for x in (definitions, info_text) if x)
        markers = collect_reference_markers(all_text)

        extracted_targets = []
        source_texts = [(row["definition_en"] or "") for row in senses] + information
        for text in source_texts:
            for pattern in target_patterns:
                for match in pattern.finditer(text):
                    target = match.group(1).strip(" \t:-'\"“”‘’")
                    if target:
                        extracted_targets.append(target)

        base = {
            "source_entry_id": entry_id,
            "source_record_id": entry["record_id"],
            "source_headword": headword,
            "source_printed_page": entry["source_printed_page"],
            "source_pdf_page": entry["source_pdf_page"],
            "part_of_speech": join_values(row["part_of_speech"] for row in senses),
            "definitions": definitions,
            "additional_information": info_text,
            "alternative_spellings": join_values(alternatives),
            "review_required": entry["review_required"],
            "human_verified": entry["human_verified"],
            "review_decision": "",
            "review_notes": "",
        }

        if markers and not extracted_targets:
            rows_out.append({
                **base,
                "candidate_type": "reference_marker_needs_review",
                "relationship_marker": ";".join(markers),
                "mentioned_target_text": "",
                "possible_target_entry_ids": "",
                "possible_target_headwords": "",
                "target_match_status": "no_target_extracted",
            })
            counts["reference_marker_needs_review"] += 1

        for target_text in dict.fromkeys(extracted_targets):
            exact = exact_headwords.get(target_text.casefold(), [])
            normalized = normalized_headwords.get(normalize_for_matching(target_text), [])
            if exact:
                matches, status = exact, "exact_headword_match"
            elif normalized:
                matches, status = normalized, "normalized_headword_match"
            else:
                matches, status = [], "no_matching_headword_found"

            rows_out.append({
                **base,
                "candidate_type": "explicit_reference",
                "relationship_marker": ";".join(markers),
                "mentioned_target_text": target_text,
                "possible_target_entry_ids": ";".join(str(m["entry_id"]) for m in matches),
                "possible_target_headwords": ";".join(
                    f'{m["headword"]} (entry_id={m["entry_id"]}, page={m["source_printed_page"]})'
                    for m in matches
                ),
                "target_match_status": status,
            })
            counts["explicit_reference"] += 1
            counts[status] += 1

        # Report each existing alternative spelling independently.
        for spelling in alternatives:
            exact = [
                m for m in exact_headwords.get((spelling or "").casefold(), [])
                if m["entry_id"] != entry_id
            ]
            normalized = [
                m for m in normalized_headwords.get(normalize_for_matching(spelling), [])
                if m["entry_id"] != entry_id
            ]
            if exact:
                matches, status = exact, "matches_other_headword_exactly"
            elif normalized:
                matches, status = normalized, "matches_other_headword_after_normalization"
            else:
                matches, status = [], "no_other_headword_match"

            rows_out.append({
                **base,
                "candidate_type": "alternative_spelling",
                "relationship_marker": "alternative_spelling_field",
                "mentioned_target_text": spelling or "",
                "possible_target_entry_ids": ";".join(str(m["entry_id"]) for m in matches),
                "possible_target_headwords": ";".join(
                    f'{m["headword"]} (entry_id={m["entry_id"]}, page={m["source_printed_page"]})'
                    for m in matches
                ),
                "target_match_status": status,
            })
            counts["alternative_spelling"] += 1
            counts[status] += 1

    fields = [
        "candidate_type", "relationship_marker", "source_entry_id",
        "source_record_id", "source_headword", "source_printed_page",
        "source_pdf_page", "part_of_speech", "definitions",
        "additional_information", "alternative_spellings",
        "mentioned_target_text", "possible_target_entry_ids",
        "possible_target_headwords", "target_match_status",
        "review_required", "human_verified", "review_decision", "review_notes",
    ]

    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_out)

    summary = [
        "Nupe Dictionary — Entry Relationship Audit",
        "==========================================",
        f"Database: {DATABASE_PATH}",
        "Database modified: NO (opened read-only)",
        f"Entries scanned: {len(entries)}",
        f"Candidate rows exported: {len(rows_out)}",
        "",
        "Counts (candidate rows can overlap):",
    ]
    summary.extend(f"- {name}: {count}" for name, count in sorted(counts.items()))
    summary.extend([
        "",
        "Review notes:",
        "- Candidates are not confirmed relationships.",
        "- Reference detection is heuristic and may include false positives or miss unusual wording.",
        "- Normalized matches ignore combining diacritics for comparison only.",
        "- If multiple target entries match, all are listed rather than selecting one.",
        "- No entries were merged, deleted, or modified.",
        f"CSV report: {CSV_PATH}",
    ])
    SUMMARY_PATH.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
