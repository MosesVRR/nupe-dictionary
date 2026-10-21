# NupeDictionary

**NupeDictionary** is a free application for searching and exploring Nupe vocabulary and English definitions, with tools designed to make Nupe spelling and diacritics easier to work with.

- **Live dictionary:** https://nupe-dictionary.vercel.app/
- **Download for Android:** [Download NupeDictionary APK](https://drive.google.com/file/d/1mdmOJnZj4MF-YrWUGjm6-OXGPNqkj3VF/view?usp=drive_link)
- **Support the project:** https://buymeacoffee.com/mosesvrr

NupeDictionary combines a Vue frontend, a FastAPI backend, and a SQLite database built from digitized dictionary records. The Android application uses Capacitor to package the frontend for installation on Android devices.

The project aims to make Nupe vocabulary easier to search and explore while preserving the spellings and diacritics represented in the source data.

> **Data note:** The underlying dictionary source is marked as a draft prepared for comment. Some entries, spellings, tone marks, and definitions may require verification against the source. Please report suspected errors rather than assuming every record is definitive.

## Features

### Dictionary

- Search Nupe headwords and available English definitions.
- Search with exact diacritics, partial spellings, and queries that omit diacritic marks.
- Use search suggestions to discover possible headwords.
- Browse dictionary entries alphabetically.
- Use the Nupe character keyboard to enter characters and diacritic combinations that may be difficult to type.
- Consult a reading guide covering entry structure, spelling, tones and diacritics, character input, and category codes.
- Look up dictionary category codes in a searchable reference.
- View available parts of speech, alternative spellings, additional information, and printed source-page references.
- Access dictionary search results through a JSON API.

### Android application

- Install the application directly using a signed APK, without Google Play.
- Download the dictionary for local storage on the device.
- Search downloaded entries when the internet connection is unavailable.
- Browse dictionary entries and use suggestions offline.
- View dictionary download progress, the number of stored entries, and the last successful update time.
- Check API connectivity through the online/offline status indicator.
- Use dedicated scrollable areas for search suggestions and dictionary results.

The offline dictionary is stored locally on the device. Downloading or updating the dictionary requires a connection to the backend. Offline functionality depends on a successful initial download and the availability of locally stored data.

### Search behavior

Search normalization is used for comparison; it should not change the displayed source spelling. Because removing diacritics can make distinct spellings look alike, a diacritic-insensitive query may return multiple candidates.

## Download and installation

### Android

**[Download NupeDictionary for Android](https://drive.google.com/file/d/1mdmOJnZj4MF-YrWUGjm6-OXGPNqkj3VF/view?usp=drive_link)**

NupeDictionary can be installed directly on compatible Android devices without using Google Play.

1. Open the download link on your Android device.
2. Download the APK file.
3. Open the downloaded APK.
4. If prompted, allow your browser or file manager to install apps from that source.
5. Follow the installation instructions and open NupeDictionary.

Android may display a security warning because the app is distributed outside Google Play. Only install APKs from a source you trust.

**Updates:** When a new version is released, download and install the updated APK. Updates require the same application ID and compatible signing key as the installed version.

### iOS

A native iOS version is not currently included in this release. The Android APK cannot be installed on an iPhone or iPad. The live web dictionary remains accessible through a mobile browser.

## Technology stack

- **Frontend:** Vue 3, TypeScript, Vite
- **Mobile framework:** Capacitor
- **Backend:** Python, FastAPI
- **Database:** SQLite
- **API:** JSON over HTTP
- **Web deployment:** Vercel
- **Backend deployment:** Render
- **Android development:** Android Studio and Gradle

## Project structure

The repository layout may vary by branch. The main application components include:

```text
nupe-dictionary/
├── backend/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   └── components/
│   ├── android/
│   ├── package.json
│   ├── package-lock.json
│   └── capacitor.config.ts
├── README.md
└── ...
```

The backend reads dictionary records from SQLite and exposes them through the API. The frontend provides the search interface, while the Android project packages the frontend for native Android installation.

The exact directory structure and available scripts should be checked against the current branch.

## Getting started

### Prerequisites

- Python
- Node.js and npm
- The project's backend dependencies and local dictionary database, where permitted and available
- Android Studio for Android development
- A compatible Java Development Kit and Android SDK

### 1. Start the backend

From the repository root, create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies using the requirements file in the repository. If it is located at `backend/requirements.txt`, run:

```powershell
pip install -r backend/requirements.txt
```

Start the API from the directory containing `main.py`. For example:

```powershell
cd backend
uvicorn main:app --reload
```

The API is typically available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

The backend must be configured to find the local SQLite database. Check the path and configuration in the current backend code before running it.

### 2. Start the frontend

Open a second terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local development URL, commonly `http://localhost:5173`.

Configure the frontend API base URL and backend CORS settings as required by the current environment. Do not commit secrets or private environment files.

## Building the Android application

The Android version uses Capacitor to package the frontend into an Android application.

### 1. Build the frontend

From the `frontend` directory:

```powershell
npm run build
```

### 2. Synchronize Capacitor

After the frontend build succeeds, run:

```powershell
npx cap sync android
```

### 3. Open Android Studio

Open the Android project generated by Capacitor, usually the `frontend/android` directory. Allow Gradle synchronization to finish, then run the application on an emulator or connected Android device.

### 4. Generate a signed APK

In Android Studio:

1. Open **Build → Generate Signed Bundle / APK**.
2. Select **APK**.
3. Select the existing signing keystore or create one for the first release.
4. Select the release build variant.
5. Complete the signing wizard and generate the APK.

The output location depends on the Android Gradle configuration and Android Studio version. Common locations include:

```text
frontend/android/app/release/
frontend/android/app/build/outputs/apk/release/
```

Use the location reported by Android Studio rather than assuming either path.

### 5. Distribute the APK

Upload the signed APK to a trusted file-hosting service and share its download link. Ensure the file's sharing permissions allow recipients to access it.

Google Play is not required for this distribution method.

### 6. Release updates

When publishing a new Android release:

- Preserve the existing application ID.
- Use the same signing key and alias used for the installed release.
- Update the application version as appropriate.
- Rebuild the frontend and synchronize Capacitor before generating the new APK.
- Test the release APK before distributing it.
- Update the download link or hosted file when publishing a new version.

Back up the signing keystore and passwords securely. Do not commit them to GitHub or distribute them with the APK. Losing the signing key can prevent updates to installations signed with that key.

## API

### `GET /`

Returns basic API information.

### `GET /api/search?q=<query>`

Searches dictionary entries and returns a JSON response containing the query, result count, and matching entries. The maximum result count and response fields are defined by the deployed backend; consult the interactive API documentation for the current schema.

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

Additional endpoints support suggestions and alphabetical browsing. Consult `/docs` for the current parameters and response schemas.

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
- Test online and offline behavior, including first download, application restarts, failed updates, and loss of connectivity.
- Check desktop and mobile layouts, keyboard navigation, focus visibility, and accessible labels when changing the UI.

## Known limitations and future work

Dictionary data quality remains an ongoing process. Possible areas for future improvement include:

- Reviewing cross-references such as `cf.` references and connecting entries.
- Checking uncertain spellings, tones, diacritics, and page-boundary records against the scans.
- Improving automated regression tests for Unicode normalization and search ranking.
- Adding more contributor guidance for dictionary corrections and data review.
- Reviewing the representation of illustrations or other non-textual information in the source, if relevant and permitted.
- Exploring a native iOS release.

Only mark a limitation as resolved after the relevant data or behaviour has been checked and verified.

## Support

NupeDictionary is intended to make Nupe vocabulary more accessible and easier to explore. If you find it useful and would like to support ongoing development, you can contribute through **[Buy Me a Coffee](https://buymeacoffee.com/mosesvrr)**. Support is optional; the dictionary remains free to use online and in the Android application.

---

*NupeDictionary is a work in progress. Please treat dictionary entries as a resource for exploration and learning, and verify uncertain information with knowledgeable Nupe speakers or reliable source material.*
