import csv
from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "output" / "relationship_audit.csv"
destination = root / "output" / "relationship_audit_review.csv"

if not source.exists():
    raise SystemExit(f"File not found: {source}")

with source.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

selected = [
    row for row in rows
    if row.get("target_match_status") == "no_matching_headword_found"
    or row.get("target_match_status") == "no_target_extracted"
]

if selected:
    with destination.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=selected[0].keys())
        writer.writeheader()
        writer.writerows(selected)

print(f"Original candidate rows: {len(rows)}")
print(f"Rows selected for review: {len(selected)}")
print(f"Review file: {destination}")