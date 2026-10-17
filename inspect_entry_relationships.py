import sqlite3
from pathlib import Path

db_path = Path("data/nupe_dictionary.sqlite3")
if not db_path.exists():
    raise SystemExit(f"Database not found: {db_path.resolve()}")

connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row

try:
    query = """
        SELECT
            e.entry_id,
            e.headword,
            e.source_printed_page,
            s.part_of_speech,
            s.definition_en,
            ai.information,
            a.spelling
        FROM entries AS e
        LEFT JOIN senses AS s
            ON s.entry_id = e.entry_id
        LEFT JOIN additional_information AS ai
            ON ai.entry_id = e.entry_id
        LEFT JOIN alternative_spellings AS a
            ON a.entry_id = e.entry_id
        WHERE
            LOWER(COALESCE(s.definition_en, '')) LIKE '%cf.%'
            OR LOWER(COALESCE(s.definition_en, '')) LIKE '%see %'
            OR LOWER(COALESCE(ai.information, '')) LIKE '%cf.%'
            OR LOWER(COALESCE(ai.information, '')) LIKE '%see %'
            OR a.spelling IS NOT NULL
        ORDER BY e.entry_id
        LIMIT 40;
    """

    rows = connection.execute(query).fetchall()

    for row in rows:
        print("-" * 60)
        for key in row.keys():
            print(f"{key}: {row[key]}")

    print(f"\nRows displayed: {len(rows)}")

finally:
    connection.close()