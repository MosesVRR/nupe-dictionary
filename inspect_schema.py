import sqlite3
from pathlib import Path

database_path = Path("data/nupe_dictionary.sqlite3")

if not database_path.exists():
    print(f"Database not found: {database_path.resolve()}")
    raise SystemExit(1)

connection = sqlite3.connect(database_path)

try:
    tables = connection.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND sql IS NOT NULL
        ORDER BY name;
    """).fetchall()

    for (schema,) in tables:
        print(schema)
        print()

finally:
    connection.close()