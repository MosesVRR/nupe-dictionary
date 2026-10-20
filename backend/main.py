import os

import sqlite3
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "nupe_dictionary.sqlite3"

app = FastAPI(
    title="Nupe Dictionary API",
    description="Search and browse Nupe headwords and their English definitions.",
    version="0.3.0",
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        *frontend_origins,
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def normalize_search_exact(value: str | None) -> str:
    """Canonical Unicode normalization while preserving diacritics."""
    if not value:
        return ""
    return unicodedata.normalize("NFD", value.casefold()).strip()


def normalize_search_text(value: str | None) -> str:
    """Diacritic-insensitive fallback normalization."""
    exact = normalize_search_exact(value)
    return "".join(
        character
        for character in exact
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
    connection.create_function(
        "normalize_search_exact",
        1,
        normalize_search_exact,
        deterministic=True,
    )
    return connection


def serialize_entries(connection, matches):
    """Load the details shown by both search and alphabetical browsing."""
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

    return results


@app.get("/")
def home():
    return {
        "message": "Nupe Dictionary API",
        "docs": "/docs",
    }


@app.get("/api/suggest")
def suggest_dictionary(
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=8, ge=1, le=12),
):
    """Suggest headwords matching a query anywhere, preserving diacritics first."""
    query = q.strip()
    exact_query = normalize_search_exact(query)
    normalized_query = normalize_search_text(query)

    if not exact_query or not normalized_query:
        return {"query": query, "count": 0, "suggestions": []}

    # Prefer matches that preserve the exact diacritic sequence, even when it
    # occurs inside a headword. Fall back to diacritic-insensitive matching
    # only after all exact-sequence matches.
    sql = """
        WITH candidates AS (
            SELECT
                e.entry_id,
                e.headword,
                CASE
                    WHEN normalize_search_exact(e.headword) = ? THEN 0
                    WHEN substr(normalize_search_exact(e.headword), 1, length(?)) = ? THEN 1
                    ELSE 2
                END AS match_rank
            FROM entries AS e
            WHERE instr(normalize_search_exact(e.headword), ?) > 0

            UNION ALL

            SELECT
                e.entry_id,
                e.headword,
                CASE
                    WHEN normalize_search_exact(a.spelling) = ? THEN 0
                    WHEN substr(normalize_search_exact(a.spelling), 1, length(?)) = ? THEN 1
                    ELSE 2
                END AS match_rank
            FROM entries AS e
            JOIN alternative_spellings AS a ON a.entry_id = e.entry_id
            WHERE instr(normalize_search_exact(a.spelling), ?) > 0

            UNION ALL

            SELECT
                e.entry_id,
                e.headword,
                CASE
                    WHEN normalize_search(e.headword) = ? THEN 3
                    WHEN substr(normalize_search(e.headword), 1, length(?)) = ? THEN 4
                    ELSE 5
                END AS match_rank
            FROM entries AS e
            WHERE instr(normalize_search(e.headword), ?) > 0

            UNION ALL

            SELECT
                e.entry_id,
                e.headword,
                CASE
                    WHEN normalize_search(a.spelling) = ? THEN 3
                    WHEN substr(normalize_search(a.spelling), 1, length(?)) = ? THEN 4
                    ELSE 5
                END AS match_rank
            FROM entries AS e
            JOIN alternative_spellings AS a ON a.entry_id = e.entry_id
            WHERE instr(normalize_search(a.spelling), ?) > 0
        ),
        ranked AS (
            SELECT entry_id, headword, MIN(match_rank) AS match_rank
            FROM candidates
            GROUP BY entry_id, headword
        )
        SELECT headword
        FROM ranked
        ORDER BY match_rank, normalize_search(headword), headword
        LIMIT ?;
    """

    params = (
        exact_query, exact_query, exact_query, exact_query,
        exact_query, exact_query, exact_query, exact_query,
        normalized_query, normalized_query, normalized_query, normalized_query,
        normalized_query, normalized_query, normalized_query, normalized_query,
        limit,
    )

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    suggestions = [{"headword": row["headword"]} for row in rows]
    return {
        "query": query,
        "count": len(suggestions),
        "suggestions": suggestions,
    }


@app.get("/api/search")
def search_dictionary(
    q: str = Query(min_length=1, max_length=200),
):
    query = q.strip()
    exact_query = normalize_search_exact(query)
    normalized_query = normalize_search_text(query)

    if not normalized_query:
        raise HTTPException(
            status_code=422,
            detail="Enter a word containing searchable letters or numbers.",
        )

    # Diacritic-preserving substring matches rank before broad,
    # diacritic-insensitive matches. Canonical NFD normalization means
    # composed and decomposed forms of the same spelling can match.
    sql = """
        WITH candidates AS (
            SELECT
                e.entry_id,
                CASE
                    WHEN normalize_search_exact(e.headword) = ? THEN 0
                    WHEN instr(normalize_search_exact(e.headword), ?) > 0 THEN 1
                    WHEN normalize_search(e.headword) = ? THEN 2
                    WHEN substr(normalize_search(e.headword), 1, length(?)) = ? THEN 3
                    ELSE 4
                END AS match_rank
            FROM entries AS e
            WHERE instr(normalize_search_exact(e.headword), ?) > 0
               OR instr(normalize_search(e.headword), ?) > 0

            UNION ALL

            SELECT
                e.entry_id,
                CASE
                    WHEN normalize_search_exact(a.spelling) = ? THEN 0
                    WHEN instr(normalize_search_exact(a.spelling), ?) > 0 THEN 1
                    WHEN normalize_search(a.spelling) = ? THEN 2
                    WHEN substr(normalize_search(a.spelling), 1, length(?)) = ? THEN 3
                    ELSE 4
                END AS match_rank
            FROM entries AS e
            JOIN alternative_spellings AS a ON a.entry_id = e.entry_id
            WHERE instr(normalize_search_exact(a.spelling), ?) > 0
               OR instr(normalize_search(a.spelling), ?) > 0
        ),
        ranked AS (
            SELECT entry_id, MIN(match_rank) AS match_rank
            FROM candidates
            GROUP BY entry_id
        )
        SELECT e.entry_id, e.headword, e.source_printed_page, ranked.match_rank
        FROM ranked
        JOIN entries AS e ON e.entry_id = ranked.entry_id
        ORDER BY ranked.match_rank, normalize_search(e.headword), e.headword
        LIMIT 50;
    """

    params = (
        exact_query, exact_query, normalized_query,
        normalized_query, normalized_query, exact_query, normalized_query,
        exact_query, exact_query, normalized_query,
        normalized_query, normalized_query, exact_query, normalized_query,
    )

    with get_connection() as connection:
        matches = connection.execute(sql, params).fetchall()
        results = serialize_entries(connection, matches)

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


@app.get("/api/browse")
def browse_dictionary(
    letter: str = Query(default="all", min_length=1, max_length=10),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Browse headwords alphabetically, with optional first-letter filtering."""
    selected_letter = letter.strip().casefold()

    if selected_letter != "all":
        normalized_letter = normalize_search_text(selected_letter)
        if len(normalized_letter) != 1 or not normalized_letter.isalpha():
            raise HTTPException(
                status_code=422,
                detail="Choose 'all' or a single alphabetic letter.",
            )
    else:
        normalized_letter = ""

    with get_connection() as connection:
        if selected_letter == "all":
            total = connection.execute(
                "SELECT COUNT(*) FROM entries;"
            ).fetchone()[0]

            matches = connection.execute(
                """
                SELECT entry_id, headword, source_printed_page
                FROM entries
                ORDER BY normalize_search(headword), headword
                LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            ).fetchall()
        else:
            total = connection.execute(
                """
                SELECT COUNT(*)
                FROM entries
                WHERE substr(normalize_search(headword), 1, 1) = ?;
                """,
                (normalized_letter,),
            ).fetchone()[0]

            matches = connection.execute(
                """
                SELECT entry_id, headword, source_printed_page
                FROM entries
                WHERE substr(normalize_search(headword), 1, 1) = ?
                ORDER BY normalize_search(headword), headword
                LIMIT ? OFFSET ?;
                """,
                (normalized_letter, limit, offset),
            ).fetchall()

        results = serialize_entries(connection, matches)

    return {
        "letter": selected_letter,
        "count": len(results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": results,
    }
