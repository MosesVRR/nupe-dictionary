
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "nupe_dictionary.sqlite3"

app = FastAPI(
    title="Nupe Dictionary API",
    description="Search Nupe headwords and their English definitions.",
    version="0.1.0",
)

# Allow the local Vue development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


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

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Enter a word to search for.",
        )

    sql = """
        SELECT entry_id, headword, source_printed_page
        FROM entries
        WHERE headword = ?

        UNION

        SELECT e.entry_id, e.headword, e.source_printed_page
        FROM entries AS e
        JOIN alternative_spellings AS a
            ON a.entry_id = e.entry_id
        WHERE a.spelling = ?

        ORDER BY headword
        LIMIT 50;
    """

    with get_connection() as connection:
        matches = connection.execute(
            sql, (query, query)
        ).fetchall()

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
