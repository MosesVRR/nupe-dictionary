# Nupe Dictionary

A web application for searching and exploring Nupe vocabulary and
English definitions. The project combines a Vue frontend, a FastAPI
backend, and a SQLite database built from a digitized Nupe--English
dictionary.

> **Project status:** Early development. The application can query
> dictionary entries through the frontend. Search improvements are being
> introduced and should be tested against the current database before
> being considered verified.

## Contents

-   [Project goals](#project-goals)
-   [Technology stack](#technology-stack)
-   [Project structure](#project-structure)
-   [Current functionality](#current-functionality)
-   [Getting started](#getting-started)
-   [API](#api)
-   [Known issues and planned work](#known-issues-and-planned-work)
-   [Dictionary data and source
    files](#dictionary-data-and-source-files)
-   [Development notes](#development-notes)

## Project goals

The goal is to make Nupe vocabulary more accessible through a
searchable, readable web dictionary. The application should preserve
Nupe spelling and diacritics, show English definitions and related entry
information, and make it easier for users to discover words even when
they do not know the exact spelling.

## Technology stack

-   **Frontend:** Vue 3, TypeScript, Vite
-   **Backend:** Python, FastAPI
-   **Database:** SQLite
-   **API style:** JSON over HTTP

## Project structure

The main application structure is:

``` text
nupe-dictionary/
├── backend/
│   └── main.py
├── frontend/
│   └── src/
│       └── App.vue
├── data/
│   └── nupe_dictionary.sqlite3
└── README.md
```

The exact frontend structure may include additional Vite configuration,
package files, components, and assets not shown above.

The SQLite database is read-only from the API's perspective. The backend
opens it in SQLite read-only mode and does not modify dictionary records
during searches.

## Current functionality

-   Search for dictionary entries through the web interface.
-   Retrieve entries from SQLite through the FastAPI backend.
-   Display headwords and available English definitions.
-   Display parts of speech, category codes, alternative spellings,
    additional information, and printed source-page references when
    present.
-   Return JSON search results from the `/api/search` endpoint.
-   Support local development with the Vue/Vite frontend and FastAPI
    backend.

The current search implementation is intended to support: - Exact
headword and alternative-spelling matches. - Searches that omit
diacritic marks. - Partial-word matching. - Ranking exact matches ahead
of broader matches.

**Verification note:** test the search behaviours above against the
actual database after installing changes. Diacritic-insensitive matching
can return more than one candidate, because removing diacritics for
comparison may cause distinct spellings to normalize to the same search
form. Displayed dictionary spellings should remain unchanged.

## Getting started

These instructions assume Python and Node.js are installed. Run commands
from the appropriate project directories.

### 1. Start the backend

From the repository root, create and activate a Python virtual
environment if you do not already have one.

Windows PowerShell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

``` powershell
pip install -r backend/requirements.txt
```

If the project keeps `requirements.txt` inside `backend/`, run the
command from that directory instead:

``` powershell
cd backend
pip install -r requirements.txt
```

Start FastAPI from the directory containing `main.py`:

``` powershell
uvicorn main:app --reload
```

The API should be available at `http://127.0.0.1:8000`. Interactive API
documentation is available at `http://127.0.0.1:8000/docs`.

The backend expects the database at:

``` text
data/nupe_dictionary.sqlite3
```

The path is resolved relative to the repository layout in
`backend/main.py`.

### 2. Start the frontend

Open a second terminal and change to the frontend directory:

``` powershell
cd frontend
npm install
npm run dev
```

Vite will print the local URL, commonly `http://localhost:5173`.

The backend CORS configuration currently allows the Vite development
origins `http://localhost:5173` and `http://127.0.0.1:5173`.

> **Dependency note:** use the project's existing dependency files and
> scripts as the source of truth. If your repository has a different
> requirements-file location or npm script, follow those project files.

## API

### `GET /`

Returns basic API information.

### `GET /api/search?q=<query>`

Searches the dictionary and returns a JSON response containing the
original query, result count, and matching entries.

Example:

``` text
http://127.0.0.1:8000/api/search?q=fako
```

The exact results depend on the contents of the local SQLite database.
The endpoint limits responses to 50 entries.

A result can include:

-   `headword`
-   `source_printed_page`
-   `senses`
    -   `sense_order`
    -   `part_of_speech`
    -   `definition_en`
    -   `category_code`
-   `alternative_spellings`
-   `additional_information`

## Known issues and planned work

Use this section as a living checklist. Add issues as they are
discovered, and check items off only after the fix has been implemented
and verified.

### Data modelling and dictionary content

-   [ ] **Connecting entries are currently stored as unique entries.**
    Some entries that function as connecting entries or cross-references
    to another headword are currently represented as independent entries
    or alternative spellings. Review the source dictionary and data
    model to decide how these should be represented, linked, and
    displayed.
-   [ ] Review cross-references such as `cf.` references and ensure they
    point to the intended headword.
-   [ ] Review entries with multiple senses, alternative spellings, or
    additional information to ensure the data model preserves their
    relationships.
-   [ ] Continue checking corrected page-boundary entries against the
    scanned source where uncertainty remains.
-   [ ] Decide how to represent non-textual source information, such as
    photographs or illustrations associated with entries.

### Search

-   [ ] Test diacritic-insensitive search with real Nupe examples,
    including cases where different words may normalize to the same
    unaccented spelling.
-   [ ] Confirm that exact headword matches rank above normalized,
    prefix, and substring matches.
-   [ ] Test alternative-spelling search, including spellings with and
    without diacritics.
-   [ ] Decide whether English-definition search should be supported.
-   [ ] Consider keyboard-friendly suggestions or live search as the
    interface evolves.
-   [ ] Evaluate search performance on the full dataset and add indexes
    or a dedicated search approach if needed.

### User interface and accessibility

-   [ ] Test the layout on mobile and desktop screen sizes.
-   [ ] Review keyboard navigation, focus indicators, labels, and
    screen-reader announcements.
-   [ ] Consider a dedicated entry page with a shareable URL for each
    headword.
-   [ ] Consider alphabetical browsing and pagination for exploring the
    dictionary without a known query.
-   [ ] Improve the presentation of cross-references and linked entries
    once the data model supports them.

### Data quality and testing

-   [ ] Add automated tests for the API's matching and result-ranking
    behaviour.
-   [ ] Add checks for JSON/database import integrity and duplicate or
    conflicting headwords.
-   [ ] Verify the number of entries and sample corrected records after
    each database refresh.
-   [ ] Add regression tests for Nupe diacritics and Unicode
    normalization.
-   [ ] Confirm that missing definitions, empty fields, and entries with
    multiple senses render gracefully.

### Deployment and project maintenance

-   [ ] Define a production deployment configuration for the frontend
    and backend.
-   [ ] Configure production CORS origins rather than relying on local
    development origins.
-   [ ] Document how the SQLite database is generated and updated from
    the master dictionary data.
-   [ ] Add a repeatable setup and test process for new contributors.

## Dictionary data and source files

The database is derived from a scanned Nupe--English dictionary that was
processed into structured records and reviewed for extraction and
page-boundary issues.

Keep the database and source material out of public version control
until the rights to redistribute the dictionary content have been
confirmed. The project repository is intended to remain private while
this is unresolved. Check `.gitignore` before committing and ensure
database files, source scans, credentials, and other restricted material
are not accidentally included.

Do not commit API keys or other secrets. Use local environment
configuration for secrets if they are required by future tooling.

## Development notes

-   Treat the original Nupe headword, diacritics, and definitions as
    source data. Search normalization should be used for comparison
    only; it must not rewrite stored spellings.
-   When changing the database schema, update the data-generation/import
    process and the API together.
-   For changes to search, test both exact spellings and unaccented
    queries.
-   Keep a record of known data issues here so that they can be resolved
    systematically rather than silently changing source entries.
