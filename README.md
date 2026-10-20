# NupeDictionary

**NupeDictionary** is a web application for searching and exploring Nupe vocabulary and English definitions, with tools designed to make Nupe spelling and diacritics easier to work with.

- **Live dictionary:** https://nupe-dictionary.vercel.app/
- **Support the project:** https://buymeacoffee.com/mosesvrr

NupeDictionary combines a Vue frontend, a FastAPI backend, and a SQLite database built from digitized dictionary records. The application aims to make the dictionary easier to search and explore while preserving the spellings and diacritics represented in the source data.

> **Data note:** The underlying dictionary source is marked as a draft prepared for comment. Some entries, spellings, tone marks, and definitions may require verification against the source. Please report suspected errors rather than assuming every record is definitive.

## Features

- Search Nupe headwords and available English definitions.
- Search with exact diacritics, partial spellings, and queries that omit diacritic marks.
- Use search suggestions to discover possible headwords.
- Browse dictionary entries alphabetically.
- Use the Nupe character keyboard to enter characters and diacritic combinations that may be difficult to type.
- Consult a reading guide covering entry structure, spelling, tones and diacritics, character input, and category codes.
- Look up dictionary category codes in a searchable reference.
- View available parts of speech, alternative spellings, additional information, and printed source-page references.
- Access dictionary search results through a JSON API.

Search normalization is used for comparison; it should not change the displayed source spelling. Because removing diacritics can make distinct spellings look alike, a diacritic-insensitive query may return multiple candidates.

## Technology stack

- **Frontend:** Vue 3, TypeScript, Vite
- **Backend:** Python, FastAPI
- **Database:** SQLite
- **API:** JSON over HTTP
- **Deployment:** Vercel (frontend) and Render (backend)

## Project structure

The repository layout may vary by branch. The main application components include:

```text
nupe-dictionary/
├── backend/
│   └── main.py
├── frontend/
│   └── src/
│       ├── App.vue
│       └── components/
├── README.md
└── ...
```

The backend reads dictionary records from SQLite and exposes them through the API. Search requests should not modify dictionary records.

## Getting started

These instructions are a general local-development outline. Use the dependency files and scripts committed in the current branch as the source of truth.

### Prerequisites

- Python
- Node.js and npm
- The project's backend dependencies and local dictionary database, where permitted and available

### 1. Start the backend

From the repository root, create and activate a virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies using the requirements file in the repository. If it is located at `backend/requirements.txt`, run:

```powershell
pip install -r backend/requirements.txt
```

Start the API from the directory containing `main.py`. For example, if `main.py` is inside `backend/`:

```powershell
cd backend
uvicorn main:app --reload
```

The API is typically available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

The backend must be configured to find the local SQLite database. Check the path and configuration in the current backend code before running it.

### 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local development URL, commonly `http://localhost:5173`.

Configure the frontend API base URL and backend CORS settings as required by the current environment. Do not commit secrets or private environment files.

## API

### `GET /`

Returns basic API information.

### `GET /api/search?q=<query>`

Searches dictionary entries and returns a JSON response with the query, result count, and matching entries. The maximum result count and response fields are defined by the deployed backend; consult the interactive API documentation for the current schema.

A result may include fields such as:

- `headword`
- `source_printed_page`
- `senses`
  - `sense_order`
  - `part_of_speech`
  - `definition_en`
  - `category_code`
- `alternative_spellings`
- `additional_information`

Example local request:

```text
http://127.0.0.1:8000/api/search?q=fako
```

Exact results depend on the dictionary database and current search implementation.

## Dictionary data, source, and attribution

The database was derived from a scanned Nupe–English dictionary attributed to R. M. Blench and marked **“Draft — prepared for comment only”** (dated August 5, 2009). The source document discusses Nupe spelling, sounds, tones, and category codes, but it also cautions that some words may lack tone marks.

The application and the underlying dictionary content may have different rights. **Confirm permission to redistribute the source material and derived dictionary data before publishing the database, scans, or extracted records.** Keep restricted source files and data out of public version control until those rights are clear.

The source and extracted records may contain errors introduced during scanning, OCR, transcription, or structuring. Changes to entries should be checked against the source where possible, and uncertain corrections should be documented.

## Reporting corrections and bugs

If you find a spelling, diacritic, definition, category code, or cross-reference that may be incorrect, please report it through the repository's issue tracker if issues are enabled.

Helpful reports include:

- The headword as displayed
- The suspected correction
- The relevant printed source page, if known
- A screenshot or short explanation, where useful

For software bugs, include the steps to reproduce the problem, what you expected to happen, and what happened instead. Avoid including private information in issue reports.

## Development and data quality

When changing the application:

- Preserve source headwords, definitions, and diacritics in their original form.
- Use normalization for search comparisons only; do not silently rewrite stored spellings.
- Test exact-diacritic, unaccented, prefix, substring, and alternative-spelling queries.
- Check that exact matches rank appropriately and that broad queries do not hide useful exact matches behind result limits.
- Test entries with multiple senses, missing definitions, alternative spellings, and additional information.
- Verify data-import changes against the source and check for duplicate or malformed records.
- Update the database-generation process, schema, and API together when the data model changes.
- Check desktop and mobile layouts, keyboard navigation, focus visibility, and accessible labels when changing the UI.

## Known limitations and future work

Dictionary data quality remains an ongoing process. Possible areas for future improvement include:

- Reviewing cross-references such as `cf.` references and connecting entries.
- Checking uncertain spellings, tones, diacritics, and page-boundary records against the scans.
- Improving automated regression tests for Unicode normalization and search ranking.
- Adding more contributor guidance for dictionary corrections and data review.
- Reviewing the representation of illustrations or other non-textual information in the source, if relevant and permitted.

Only mark a limitation as resolved after the relevant data or behaviour has been checked and verified.

## Support

NupeDictionary is intended to make Nupe vocabulary more accessible and easier to explore. If you find it useful and would like to support ongoing development, you can contribute through **[Buy Me a Coffee](https://buymeacoffee.com/mosesvrr)**. Support is optional; the dictionary remains available to use online.

---

*NupeDictionary is a work in progress. Please treat dictionary entries as a resource for exploration and learning, and verify uncertain information with knowledgeable Nupe speakers or reliable source material.*
