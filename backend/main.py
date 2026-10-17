import sqlite3
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "nupe_dictionary.sqlite3"

app = FastAPI(
    title="Nupe Dictionary API",
    description="Search Nupe headwords and their English definitions.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def normalize_search_text(value: str | None) -> str:
    """Normalize text for matching without changing the stored spelling.

    NFD separates combining diacritic marks from their base letters; removing
    those marks makes a query such as "fako" match "fákó". Original database
    values are returned unchanged. This is a convenience search, not a claim
    that words with different diacritics are linguistically identical.
    """
    if not value:
        return ""

    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    ).strip()


def get_connection():
    if not DATABASE_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Dictionary database was not found.",
        )

    connection = sqlite3.connect(
        DATABASE_PATH.as_uri() + "?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    connection.create_function(
        "normalize_search",
        1,
        normalize_search_text,
        deterministic=True,
    )
    return connection


@app.get("/")
def home():
    return {
        "message": "Nupe Dictionary API",
        "docs": "/docs",
    }


@app.get("/api/search")
def search_dictionary(
    q: str = Query(min_length=1, max_length=200),
):
    query = q.strip()
    normalized_query = normalize_search_text(query)

    if not normalized_query:
        raise HTTPException(
            status_code=422,
            detail="Enter a word containing searchable letters or numbers.",
        )

    # Rank exact original spelling first, then normalized exact matches,
    # then prefix matches, then substring matches. Search alternative
    # spellings as well as headwords. Stored spellings are never modified.
    sql = """
        WITH candidates AS (
            SELECT
                e.entry_id,
                CASE
                    WHEN e.headword = ? COLLATE NOCASE THEN 0
                    WHEN normalize_search(e.headword) = ? THEN 1
                    WHEN substr(normalize_search(e.headword), 1, length(?)) = ? THEN 2
                    ELSE 3
                END AS match_rank
            FROM entries AS e
            WHERE instr(normalize_search(e.headword), ?) > 0

            UNION ALL

            SELECT
                e.entry_id,
                CASE
                    WHEN a.spelling = ? COLLATE NOCASE THEN 0
                    WHEN normalize_search(a.spelling) = ? THEN 1
                    WHEN substr(normalize_search(a.spelling), 1, length(?)) = ? THEN 2
                    ELSE 3
                END AS match_rank
            FROM entries AS e
            JOIN alternative_spellings AS a ON a.entry_id = e.entry_id
            WHERE instr(normalize_search(a.spelling), ?) > 0
        ),
        ranked AS (
            SELECT entry_id, MIN(match_rank) AS match_rank
            FROM candidates
            GROUP BY entry_id
        )
        SELECT e.entry_id, e.headword, e.source_printed_page, ranked.match_rank
        FROM ranked
        JOIN entries AS e ON e.entry_id = ranked.entry_id
        ORDER BY ranked.match_rank, e.headword COLLATE NOCASE
        LIMIT 50;
    """

    params = (
        query, normalized_query, normalized_query, normalized_query,
        normalized_query,
        query, normalized_query, normalized_query, normalized_query,
        normalized_query,
    )

    with get_connection() as connection:
        matches = connection.execute(sql, params).fetchall()
        results = []

        for match in matches:
            entry_id = match["entry_id"]

            senses = connection.execute(
                """
                SELECT sense_order, part_of_speech,
                       definition_en, category_code
                FROM senses
                WHERE entry_id = ?
                ORDER BY sense_order;
                """,
                (entry_id,),
            ).fetchall()

            information = connection.execute(
                """
                SELECT information
                FROM additional_information
                WHERE entry_id = ?
                ORDER BY information_order;
                """,
                (entry_id,),
            ).fetchall()

            alternatives = connection.execute(
                """
                SELECT spelling
                FROM alternative_spellings
                WHERE entry_id = ?
                ORDER BY spelling;
                """,
                (entry_id,),
            ).fetchall()

            results.append({
                "headword": match["headword"],
                "source_printed_page": match["source_printed_page"],
                "senses": [dict(row) for row in senses],
                "additional_information": [
                    row["information"] for row in information
                ],
                "alternative_spellings": [
                    row["spelling"] for row in alternatives
                ],
            })

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }
