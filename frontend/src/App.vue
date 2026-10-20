<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import CategoryCodeReference from './components/CategoryCodeReference.vue'
import { getCategoryMeaning } from './data/categoryCodes'
import DictionaryReadingGuide from './components/DictionaryReadingGuide.vue'

interface Sense {
  part_of_speech: string | null
  definition_en: string
  category_code: string | null
}

interface ApiDictionaryEntry {
  headword: string
  source_printed_page?: number | null
  senses?: Sense[] | null
  additional_information?: string[] | null
  alternative_spellings?: string[] | null
}

interface SearchResponse {
  query?: string
  count: number
  results: ApiDictionaryEntry[]
}

interface BrowseResponse {
  letter: string
  count: number
  total: number
  offset: number
  limit: number
  results: ApiDictionaryEntry[]
}

interface DictionaryEntry {
  headword: string
  source_printed_page: number | null
  senses: Sense[]
  additional_information: string[]
  alternative_spellings: string[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://nupe-dictionary.onrender.com'
const PAGE_SIZE = 50
const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

interface KeyboardForm {
  text: string
  code_points: string[]
  kind: string
  occurrences: number
  headwords_containing_form: number
  example_headword: string
}

const searchInput = ref<HTMLInputElement | null>(null)
const keyboardForms = ref<KeyboardForm[]>([])
const keyboardOpen = ref(false)
const keyboardLoadError = ref('')
const cursorStart = ref(0)
const cursorEnd = ref(0)

const basicKeyboardForms = computed(() =>
  keyboardForms.value.filter((form) => form.kind === 'basic_letter'),
)
const specialKeyboardForms = computed(() =>
  keyboardForms.value.filter((form) => form.kind !== 'basic_letter'),
)

onMounted(async () => {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}data/app_character_config.json`)
    if (!response.ok) {
      throw new Error(`Could not load character configuration (HTTP ${response.status}).`)
    }
    const config: { keyboard_forms?: KeyboardForm[] } = await response.json()
    if (!Array.isArray(config.keyboard_forms)) {
      throw new Error('The character configuration has an unexpected format.')
    }

    // Keep lowercase forms for the first version; uppercase headwords remain in
    // the generated source config but are not shown as separate keyboard keys.
    keyboardForms.value = config.keyboard_forms.filter(
      (form) => form.text === form.text.toLocaleLowerCase(),
    )
  } catch (error: unknown) {
    keyboardLoadError.value =
      error instanceof Error ? error.message : 'Could not load character configuration.'
    console.error('Character keyboard configuration failed to load:', error)
  }
})

function rememberCursor() {
  const input = searchInput.value
  if (!input) return
  cursorStart.value = input.selectionStart ?? searchQuery.value.length
  cursorEnd.value = input.selectionEnd ?? cursorStart.value
}

async function insertKeyboardForm(form: string) {
  const input = searchInput.value
  const value = searchQuery.value
  const start = input?.selectionStart ?? cursorStart.value ?? value.length
  const end = input?.selectionEnd ?? cursorEnd.value ?? start

  searchQuery.value = `${value.slice(0, start)}${form}${value.slice(end)}`
  const nextCursor = start + form.length
  cursorStart.value = nextCursor
  cursorEnd.value = nextCursor
  scheduleSuggestions()

  await nextTick()
  if (searchInput.value) {
    searchInput.value.focus()
    searchInput.value.setSelectionRange(nextCursor, nextCursor)
  }
}

const searchQuery = ref('')
const suggestions = ref<string[]>([])
const suggestionsOpen = ref(false)
let suggestionTimer: ReturnType<typeof setTimeout> | undefined
let suggestionRequestId = 0
const results = ref<DictionaryEntry[]>([])
const loading = ref(false)
const errorMessage = ref('')
const hasSearched = ref(false)
const resultCount = ref(0)

const browseMode = ref(false)
const categoryReferenceOpen = ref(false)
const readingGuideOpen = ref(false)
const selectedLetter = ref('all')
const browseOffset = ref(0)
const browseTotal = ref(0)

const currentPage = computed(() => Math.floor(browseOffset.value / PAGE_SIZE) + 1)
const totalPages = computed(() => Math.max(1, Math.ceil(browseTotal.value / PAGE_SIZE)))
const hasPreviousPage = computed(() => browseOffset.value > 0)
const hasNextPage = computed(
  () => browseOffset.value + PAGE_SIZE < browseTotal.value,
)

function normalizeEntries(entries: ApiDictionaryEntry[]): DictionaryEntry[] {
  return entries.map((entry) => ({
    headword: entry.headword,
    source_printed_page: entry.source_printed_page ?? null,
    senses: entry.senses ?? [],
    additional_information: entry.additional_information ?? [],
    alternative_spellings: entry.alternative_spellings ?? [],
  }))
}

function scheduleSuggestions() {
  if (suggestionTimer) clearTimeout(suggestionTimer)

  const query = searchQuery.value.trim()
  suggestionsOpen.value = false

  if (query.length < 1) {
    suggestions.value = []
    return
  }

  suggestionTimer = setTimeout(async () => {
    const requestId = ++suggestionRequestId
    try {
      const params = new URLSearchParams({ q: query, limit: '8' })
      const response = await fetch(`${API_BASE_URL}/api/suggest?${params}`)
      if (!response.ok) return

      const data: { suggestions?: { headword: string }[] } = await response.json()
      if (requestId !== suggestionRequestId) return

      suggestions.value = (data.suggestions ?? []).map((item) => item.headword)
      suggestionsOpen.value = suggestions.value.length > 0
    } catch {
      // Suggestions are optional; the normal search remains available if this fails.
      suggestions.value = []
      suggestionsOpen.value = false
    }
  }, 180)
}

function chooseSuggestion(headword: string) {
  searchQuery.value = headword
  suggestions.value = []
  suggestionsOpen.value = false
  void searchDictionary()
}

async function searchDictionary() {
  if (suggestionTimer) clearTimeout(suggestionTimer)
  suggestionRequestId += 1
  suggestions.value = []
  suggestionsOpen.value = false
  const query = searchQuery.value.trim()

  if (!query) {
    results.value = []
    resultCount.value = 0
    errorMessage.value = 'Please enter a Nupe word to search.'
    hasSearched.value = false
    browseMode.value = false
    return
  }

  loading.value = true
  errorMessage.value = ''
  results.value = []
  resultCount.value = 0
  hasSearched.value = true
  browseMode.value = false

  try {
    const url = `${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`
    const response = await fetch(url)

    if (!response.ok) {
      let detail = `The API returned HTTP ${response.status}.`
      try {
        const body = await response.json()
        if (typeof body.detail === 'string') detail = body.detail
      } catch {
        // Keep the HTTP status message.
      }
      throw new Error(detail)
    }

    const data: SearchResponse = await response.json()
    if (!data || !Array.isArray(data.results)) {
      throw new Error('The API response was not in the expected format.')
    }

    results.value = normalizeEntries(data.results)
    resultCount.value = results.value.length

    if (results.value.length === 0) {
      errorMessage.value =
        'No matching entries found. Try a shorter spelling or omit the diacritics.'
    }
  } catch (error: unknown) {
    console.error('Dictionary search failed:', error)
    errorMessage.value =
      error instanceof TypeError
        ? 'Could not reach the API. Check that FastAPI is running and CORS allows this frontend.'
        : error instanceof Error
          ? error.message
          : 'An unexpected error occurred while searching.'
  } finally {
    loading.value = false
  }
}

async function browseDictionary(letter = 'all', offset = 0) {
  loading.value = true
  errorMessage.value = ''
  results.value = []
  resultCount.value = 0
  hasSearched.value = true
  browseMode.value = true
  selectedLetter.value = letter
  browseOffset.value = offset
  searchQuery.value = ''

  try {
    const params = new URLSearchParams({
      letter,
      offset: String(offset),
      limit: String(PAGE_SIZE),
    })
    const response = await fetch(`${API_BASE_URL}/api/browse?${params}`)

    if (!response.ok) {
      let detail = `The API returned HTTP ${response.status}.`
      try {
        const body = await response.json()
        if (typeof body.detail === 'string') detail = body.detail
      } catch {
        // Keep the HTTP status message.
      }
      throw new Error(detail)
    }

    const data: BrowseResponse = await response.json()
    if (!data || !Array.isArray(data.results)) {
      throw new Error('The API response was not in the expected format.')
    }

    results.value = normalizeEntries(data.results)
    resultCount.value = data.count
    browseTotal.value = data.total
    browseOffset.value = data.offset

    if (data.total === 0) {
      errorMessage.value = 'No entries were found for this letter.'
    }
  } catch (error: unknown) {
    console.error('Dictionary browse failed:', error)
    errorMessage.value =
      error instanceof TypeError
        ? 'Could not reach the API. Check that FastAPI is running and CORS allows this frontend.'
        : error instanceof Error
          ? error.message
          : 'An unexpected error occurred while browsing.'
  } finally {
    loading.value = false
  }
}

function goToPreviousPage() {
  if (hasPreviousPage.value && !loading.value) {
    void browseDictionary(selectedLetter.value, Math.max(0, browseOffset.value - PAGE_SIZE))
  }
}

function goToNextPage() {
  if (hasNextPage.value && !loading.value) {
    void browseDictionary(selectedLetter.value, browseOffset.value + PAGE_SIZE)
  }
}
</script>

<template>
  <main class="page">
    <header class="header">
      <p class="eyebrow">NUPE LANGUAGE PROJECT</p>
      <h1>Nupe Dictionary</h1>
      <p class="subtitle">
        Discover the meaning of Nupe words in English.
      </p>
    </header>

    <section class="search-section">
      <form class="search-form" @submit.prevent="searchDictionary">
        <label for="search">Search the Nupe dictionary</label>

        <div class="search-input">
          <div class="search-control">
            <input
              id="search"
              ref="searchInput"
              v-model="searchQuery"
              type="search"
              placeholder="Type a Nupe word, with or without diacritics..."
              autocomplete="off"
              :disabled="loading"
              aria-autocomplete="list"
              aria-controls="search-suggestions"
              :aria-expanded="suggestionsOpen"
              @input="scheduleSuggestions"
              @click="rememberCursor"
              @keyup="rememberCursor"
              @select="rememberCursor"
              @focus="suggestionsOpen = suggestions.length > 0"
              @keydown.esc="suggestionsOpen = false"
            />
            <ul
              v-if="suggestionsOpen && suggestions.length > 0"
              id="search-suggestions"
              class="suggestions-list"
              role="listbox"
              aria-label="Matching Nupe headwords"
            >
              <li v-for="headword in suggestions" :key="headword" role="option">
                <button
                  type="button"
                  class="suggestion-option"
                  :disabled="loading"
                  @mousedown.prevent="chooseSuggestion(headword)"
                >
                  {{ headword }}
                </button>
              </li>
            </ul>
          </div>
          <button type="submit" :disabled="loading">
            {{ loading ? 'Loading…' : 'Search' }}
          </button>
        </div>

        <p class="hint">
          Search for a complete word or part of a word. Diacritics are optional
          for searching; results retain the dictionary's original spelling.
        </p>

        <section class="character-keyboard" aria-label="Nupe character keyboard">
          <div class="keyboard-heading">
            <div>
              <h2>Nupe character keyboard</h2>
              <p>Insert observed Nupe character forms at the cursor in the search field.</p>
            </div>
            <button
              type="button"
              class="keyboard-toggle"
              :aria-expanded="keyboardOpen"
              :disabled="loading"
              @click="keyboardOpen = !keyboardOpen"
            >
              {{ keyboardOpen ? 'Hide keys' : 'Show keys' }}
            </button>
          </div>

          <p v-if="keyboardLoadError" class="keyboard-error" role="status">
            Character keys could not be loaded. Make sure
            <code>public/data/app_character_config.json</code> exists in the frontend.
          </p>

          <div v-if="keyboardOpen && keyboardForms.length > 0" class="keyboard-keys">
            <div v-if="specialKeyboardForms.length > 0" class="keyboard-group">
              <h3>Special letters and diacritics</h3>
              <div class="key-grid">
                <button
                  v-for="form in specialKeyboardForms"
                  :key="form.text"
                  type="button"
                  class="character-key"
                  :title="`${form.code_points.join(' + ')} · found ${form.occurrences} times`"
                  :aria-label="`Insert ${form.text}`"
                  :disabled="loading"
                  @mousedown.prevent
                  @click="insertKeyboardForm(form.text)"
                >
                  {{ form.text }}
                </button>
              </div>
            </div>

            <div v-if="basicKeyboardForms.length > 0" class="keyboard-group">
              <h3>Basic letters found in the dictionary</h3>
              <div class="key-grid">
                <button
                  v-for="form in basicKeyboardForms"
                  :key="form.text"
                  type="button"
                  class="character-key basic-character-key"
                  :title="`Found ${form.occurrences} times`"
                  :aria-label="`Insert ${form.text}`"
                  :disabled="loading"
                  @mousedown.prevent
                  @click="insertKeyboardForm(form.text)"
                >
                  {{ form.text }}
                </button>
              </div>
            </div>
          </div>
          <p v-else-if="keyboardOpen && !keyboardLoadError" class="hint">
            Loading character keys…
          </p>
        </section>
      </form>

      <div class="browse-panel">
        <div class="browse-heading">
          <div>
            <h2>Browse alphabetically</h2>
            <p>Explore headwords without knowing what to search for.</p>
          </div>
          <button
            class="browse-all"
            type="button"
            :disabled="loading"
            @click="browseDictionary('all', 0)"
          >
            Browse all
          </button>
        </div>

        <div class="alphabet" aria-label="Filter dictionary by first letter">
          <button
            v-for="letter in alphabet"
            :key="letter"
            type="button"
            :class="{ active: selectedLetter === letter.toLowerCase() && browseMode }"
            :aria-pressed="selectedLetter === letter.toLowerCase() && browseMode"
            :disabled="loading"
            @click="browseDictionary(letter.toLowerCase(), 0)"
          >
            {{ letter }}
          </button>
        </div>
      </div>

      <section class="category-reference-panel reading-guide-panel">
        <div class="browse-heading">
          <div>
            <h2>How to use this dictionary</h2>
            <p>Learn about entries, Nupe spelling, tones, diacritics, and category codes.</p>
          </div>
          <button
            class="browse-all"
            type="button"
            :aria-expanded="readingGuideOpen"
            @click="readingGuideOpen = !readingGuideOpen"
          >
            {{ readingGuideOpen ? 'Hide reading guide' : 'Read the guide' }}
          </button>
        </div>
        <DictionaryReadingGuide v-if="readingGuideOpen" />
      </section>

      <section class="category-reference-panel">
        <div class="browse-heading">
          <div>
            <h2>Dictionary category codes</h2>
            <p>Look up the subject codes used in dictionary entries.</p>
          </div>
          <button
            class="browse-all"
            type="button"
            :aria-expanded="categoryReferenceOpen"
            @click="categoryReferenceOpen = !categoryReferenceOpen"
          >
            {{ categoryReferenceOpen ? 'Hide code reference' : 'Explore category codes' }}
          </button>
        </div>
        <CategoryCodeReference v-if="categoryReferenceOpen" />
      </section>
    </section>

    <section class="results" aria-live="polite" :aria-busy="loading">
      <p v-if="loading" class="status" role="status">
        {{ browseMode ? 'Loading dictionary entries…' : 'Searching the dictionary…' }}
      </p>

      <div v-else-if="errorMessage" class="status" role="status">
        {{ errorMessage }}
      </div>

      <div v-else-if="!hasSearched" class="empty-state">
        <h2>Start exploring</h2>
        <p>
          Search for a Nupe word or choose a letter to browse the dictionary.
        </p>
      </div>

      <div v-else>
        <div class="results-toolbar">
          <p class="result-count">
            <template v-if="browseMode">
              {{ browseTotal.toLocaleString() }} total
              {{ selectedLetter === 'all' ? 'dictionary entries' : `entries beginning with ${selectedLetter.toUpperCase()}` }}
            </template>
            <template v-else>
              {{ resultCount }} {{ resultCount === 1 ? 'entry' : 'entries' }} found
            </template>
          </p>

          <div v-if="browseMode && browseTotal > 0" class="pagination">
            <button type="button" :disabled="!hasPreviousPage || loading" @click="goToPreviousPage">
              Previous
            </button>
            <span>Page {{ currentPage }} of {{ totalPages }}</span>
            <button type="button" :disabled="!hasNextPage || loading" @click="goToNextPage">
              Next
            </button>
          </div>
        </div>

        <article
          v-for="(entry, index) in results"
          :key="`${entry.headword}-${index}`"
          class="entry-card"
          :aria-labelledby="`entry-title-${index}`"
        >
          <div class="entry-heading">
            <div class="headword-group">
              <p class="entry-label">NUPE HEADWORD</p>
              <h2 :id="`entry-title-${index}`">{{ entry.headword }}</h2>
            </div>
            <span v-if="entry.source_printed_page != null" class="page-number">
              <span class="page-label">SOURCE</span>
              Printed page {{ entry.source_printed_page }}
            </span>
          </div>

          <div v-if="entry.alternative_spellings.length > 0" class="entry-section alternative-section">
            <h3>Alternative spellings</h3>
            <p class="spellings">{{ entry.alternative_spellings.join(' · ') }}</p>
          </div>

          <div class="entry-section definitions-section">
            <h3>English definitions</h3>
            <ol v-if="entry.senses.length > 0" class="definitions">
              <li v-for="(sense, senseIndex) in entry.senses" :key="senseIndex">
                <div class="sense-meta">
                  <span v-if="sense.part_of_speech" class="part-of-speech">
                    {{ sense.part_of_speech }}
                  </span>
                  <span v-if="sense.category_code" class="category">
                    Code: {{ sense.category_code }}
                    <template v-if="getCategoryMeaning(sense.category_code)">
                      — {{ getCategoryMeaning(sense.category_code) }}
                    </template>
                  </span>
                </div>
                <p>{{ sense.definition_en }}</p>
              </li>
            </ol>
            <p v-else>No definitions available for this entry.</p>
          </div>

          <div v-if="entry.additional_information.length > 0" class="entry-section additional-section">
            <h3>Notes from the dictionary</h3>
            <ul>
              <li v-for="(information, infoIndex) in entry.additional_information" :key="infoIndex">
                {{ information }}
              </li>
            </ul>
          </div>
        </article>

        <div v-if="browseMode && browseTotal > 0" class="pagination pagination-bottom">
          <button type="button" :disabled="!hasPreviousPage || loading" @click="goToPreviousPage">
            Previous
          </button>
          <span>Page {{ currentPage }} of {{ totalPages }}</span>
          <button type="button" :disabled="!hasNextPage || loading" @click="goToNextPage">
            Next
          </button>
        </div>
      </div>
    </section>

    <footer>
      <p>Nupe Dictionary · A project to make Nupe vocabulary more accessible.</p>
      <div class="support-project">
        <p class="support-title">Support NupeDictionary</p>
        <p>
          Help support the continued development, improvement, and preservation
          of the Nupe language through this dictionary.
        </p>
        <a
          class="support-link"
          href="https://buymeacoffee.com/mosesvrr"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Support NupeDictionary on Buy Me a Coffee (opens in a new tab)"
        >
          <span aria-hidden="true">☕</span>
          Buy Me a Coffee
        </a>
      </div>
    </footer>
  </main>
</template>

<style>
:root {
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #202b27;
  background: #f7f8f5;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
* { box-sizing: border-box; }
body { margin: 0; min-width: 320px; min-height: 100vh; text-align: left; }
button, input { font: inherit; }
button:focus-visible, input:focus-visible { outline: 3px solid #8ab49a; outline-offset: 3px; }
button:disabled { cursor: wait; opacity: 0.55; }
.page { width: min(100% - 32px, 850px); margin: 0 auto; }
.header { padding: 56px 0 32px; text-align: center; }
.eyebrow { color: #47745d; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.14em; }
h1 { margin: 12px 0 8px; color: #202b27; font-size: clamp(2.2rem, 5vw, 3.2rem); line-height: 1.15; letter-spacing: -0.045em; }
.subtitle { margin: 0; color: #65716a; font-size: 1rem; line-height: 1.5; }
.search-section { padding: 28px; background: #fff; border: 1px solid #e4e9e3; border-radius: 18px; box-shadow: 0 10px 30px rgb(30 50 35 / 5%); }
.search-form label { display: block; margin-bottom: 10px; font-weight: 650; }
.search-input { display: flex; gap: 10px; align-items: flex-start; }
.search-control { position: relative; flex: 1; min-width: 0; }
.search-control input { display: block; }
.suggestions-list { position: absolute; z-index: 20; top: calc(100% + 5px); left: 0; right: 0; margin: 0; padding: 5px; list-style: none; background: #fff; border: 1px solid #d5ddd5; border-radius: 9px; box-shadow: 0 10px 24px rgb(30 50 35 / 12%); max-height: 280px; overflow-y: auto; }
.suggestions-list li { margin: 0; padding: 0; }
.suggestion-option { display: block; width: 100%; padding: 10px 12px; color: #203b2d; background: #fff; border: 0; border-radius: 6px; text-align: left; cursor: pointer; }
.suggestion-option:hover, .suggestion-option:focus-visible { background: #edf4ee; }
.search-input input { width: 100%; min-width: 0; padding: 14px 16px; color: #202b27; background: #fff; border: 1px solid #d5ddd5; border-radius: 9px; }
.search-input input:focus { border-color: #47745d; }
.search-input button, .browse-all { padding: 0 23px; color: #fff; background: #315e49; border: 0; border-radius: 9px; cursor: pointer; font-weight: 650; }
.search-input button:hover:not(:disabled), .browse-all:hover:not(:disabled) { background: #244b39; }
.hint, .status { margin: 12px 0 0; color: #65716a; font-size: 0.9rem; line-height: 1.6; }
.character-keyboard { margin-top: 18px; padding-top: 17px; border-top: 1px solid #e8ece7; }
.keyboard-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.keyboard-heading h2 { margin: 0 0 6px; color: #1f3328; font-size: 1.08rem; font-weight: 750; line-height: 1.35; letter-spacing: -0.015em; }
.keyboard-heading p { margin: 0; color: #65716a; font-size: 0.86rem; line-height: 1.5; }
.keyboard-toggle { flex-shrink: 0; min-height: 38px; padding: 0 13px; color: #315e49; background: #f7f8f5; border: 1px solid #dce5dc; border-radius: 8px; cursor: pointer; font-weight: 650; }
.keyboard-toggle:hover:not(:disabled) { background: #eaf1e9; }
.keyboard-keys { display: grid; gap: 17px; margin-top: 18px; }
.keyboard-group h3 { margin: 0 0 9px; color: #65716a; font-size: 0.8rem; font-weight: 700; }
.key-grid { display: flex; flex-wrap: wrap; gap: 7px; }
.character-key { min-width: 39px; min-height: 40px; padding: 6px 10px; color: #203b2d; background: #f1f6f0; border: 1px solid #d3e1d2; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 650; }
.character-key:hover:not(:disabled), .character-key:focus-visible { background: #deecdf; border-color: #83a98b; }
.basic-character-key { min-width: 36px; color: #315e49; background: #fff; }
.keyboard-error { margin: 12px 0 0; color: #a43d31; font-size: 0.86rem; line-height: 1.5; }
.category-reference-panel { margin-top: 22px; padding-top: 22px; border-top: 1px solid #e8ece7; }
.browse-panel { margin-top: 25px; padding-top: 22px; border-top: 1px solid #e8ece7; }
.browse-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.browse-heading h2 { margin: 0 0 6px; color: #1f3328; font-size: 1.12rem; font-weight: 750; line-height: 1.35; letter-spacing: -0.015em; }
.browse-heading p { margin: 0; color: #65716a; font-size: 0.88rem; line-height: 1.5; }
.browse-all { min-height: 40px; white-space: nowrap; }
.alphabet { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 18px; }
.alphabet button { min-width: 35px; min-height: 36px; padding: 0 8px; color: #315e49; background: #f7f8f5; border: 1px solid #dce5dc; border-radius: 7px; cursor: pointer; font-weight: 650; }
.alphabet button:hover:not(:disabled) { background: #eaf1e9; }
.alphabet button.active { color: #fff; background: #315e49; border-color: #315e49; }
.results { min-height: 190px; padding: 30px 0; text-align: left; }
.empty-state { padding: 30px 12px; text-align: center; }
.empty-state h2 { color: #202b27; font-size: 1.2rem; }
.empty-state p { color: #65716a; line-height: 1.6; }
.results-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.result-count { margin: 0; color: #65716a; font-size: 0.9rem; }
.pagination { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 10px; color: #65716a; font-size: 0.88rem; }
.pagination button { min-height: 36px; padding: 0 12px; color: #315e49; background: #fff; border: 1px solid #dce5dc; border-radius: 7px; cursor: pointer; }
.pagination button:hover:not(:disabled) { background: #eaf1e9; }
.pagination-bottom { padding-top: 10px; }
.entry-card { margin-bottom: 18px; padding: 25px; color: #202b27; background: #fff; border: 1px solid #e0e7df; border-radius: 14px; text-align: left; box-shadow: 0 4px 16px rgb(30 50 35 / 3%); }
.entry-heading { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 14px; padding-bottom: 18px; border-bottom: 1px solid #e8ece7; }
.headword-group { min-width: 0; }
.entry-label, .page-label { margin: 0 0 5px; color: #7a877e; font-size: 0.68rem; font-weight: 750; letter-spacing: 0.12em; }
.entry-heading h2 { margin: 0; color: #203b2d; font-size: 2rem; font-weight: 750; line-height: 1.25; letter-spacing: -0.025em; overflow-wrap: anywhere; }
.page-number { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; color: #65716a; font-size: 0.82rem; white-space: nowrap; }
.page-label { margin: 0; }
.entry-section { margin-top: 22px; }
.entry-section h3 { margin: 0 0 12px; color: #315e49; font-size: 0.88rem; font-weight: 750; letter-spacing: 0.015em; }
.entry-section p, .entry-section li { color: #28332d; line-height: 1.7; }
.entry-section p { margin-top: 6px; margin-bottom: 6px; }
.alternative-section { padding: 13px 15px; background: #f6f8f5; border-radius: 9px; }
.alternative-section h3 { margin-bottom: 5px; }
.alternative-section .spellings { margin: 0; }
.spellings { overflow-wrap: anywhere; }
.definitions { margin: 0; padding-left: 27px; }
.definitions li { padding-left: 6px; margin-bottom: 18px; }
.definitions li:last-child { margin-bottom: 0; }
.definitions li::marker { color: #6a8a75; font-weight: 700; }
.definitions p { margin: 7px 0 0; white-space: normal; overflow-wrap: anywhere; font-size: 1rem; }
.sense-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; }
.part-of-speech { display: inline-block; padding: 3px 8px; color: #315e49; background: #edf4ee; border-radius: 5px; font-size: 0.78rem; font-weight: 650; font-style: italic; }
.category {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.35rem;
  padding: 0.3rem 0.55rem;
  border: 1px solid #8aaf96;
  border-radius: 6px;
  background: #e7f4e9;
  color: #174d2a;
  font-weight: 650;
  line-height: 1.4;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}
.additional-section { padding-top: 17px; border-top: 1px solid #edf0ec; }
.additional-section ul { margin: 0; padding-left: 22px; }
.additional-section li { padding-left: 4px; margin-bottom: 8px; }
.additional-section li:last-child { margin-bottom: 0; }
footer { padding: 24px 0 35px; color: #65716a; text-align: center; font-size: 0.82rem; line-height: 1.6; }
.support-project { max-width: 520px; margin: 22px auto 0; padding: 20px 22px; background: #fff; border: 1px solid #e0e7df; border-radius: 14px; }
.support-project p { margin: 0; }
.support-project .support-title { margin-bottom: 6px; color: #203b2d; font-size: 1rem; font-weight: 750; }
.support-project p:not(.support-title) { color: #65716a; font-size: 0.88rem; }
.support-link { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 42px; margin-top: 14px; padding: 0 18px; color: #fff; background: #315e49; border-radius: 9px; text-decoration: none; font-size: 0.9rem; font-weight: 700; transition: background 150ms ease, transform 150ms ease; }
.support-link:hover { background: #244b39; transform: translateY(-1px); }
.support-link:focus-visible { outline: 3px solid #8ab49a; outline-offset: 3px; }
@media (max-width: 520px) {
  .header { padding-top: 48px; }
  .search-section { padding: 20px; }
  .search-input { flex-direction: column; }\n  .search-control { width: 100%; }
  .search-input button { min-height: 46px; }
  .keyboard-heading { align-items: flex-start; flex-direction: column; }
  .keyboard-toggle { min-height: 42px; }
  .character-key { min-width: 42px; min-height: 42px; }
  .browse-heading { align-items: flex-start; flex-direction: column; }
  .browse-all { min-height: 42px; }
  .entry-card { padding: 18px; }
  .entry-heading { align-items: flex-start; flex-direction: column; }
  .entry-heading h2 { font-size: 1.6rem; }
  .page-number { align-items: flex-start; }
  .results-toolbar { align-items: flex-start; flex-direction: column; }
}
</style>
