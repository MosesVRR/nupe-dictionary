
<script setup lang="ts">
import { ref } from 'vue'

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
  query: string
  count: number
  results: ApiDictionaryEntry[]
}

interface DictionaryEntry {
  headword: string
  source_printed_page: number | null
  senses: Sense[]
  additional_information: string[]
  alternative_spellings: string[]
}

const searchQuery = ref('')
const results = ref<DictionaryEntry[]>([])
const loading = ref(false)
const errorMessage = ref('')
const hasSearched = ref(false)
const resultCount = ref(0)

async function searchDictionary() {
  const query = searchQuery.value.trim()

  if (!query) {
    results.value = []
    resultCount.value = 0
    errorMessage.value = 'Please enter a Nupe word to search.'
    hasSearched.value = false
    return
  }

  loading.value = true
  errorMessage.value = ''
  results.value = []
  resultCount.value = 0
  hasSearched.value = true

  try {
    const url = `http://127.0.0.1:8000/api/search?q=${encodeURIComponent(query)}`
    const response = await fetch(url)

    if (!response.ok) {
      let detail = `The API returned HTTP ${response.status}.`

      try {
        const body = await response.json()
        if (typeof body.detail === 'string') {
          detail = body.detail
        }
      } catch {
        // Keep the HTTP status message if the error isn't JSON.
      }

      throw new Error(detail)
    }

    const data: SearchResponse = await response.json()

    if (!data || !Array.isArray(data.results)) {
      throw new Error(
        'The API response was not in the expected format. Check the backend response.',
      )
    }

    results.value = data.results.map((entry) => ({
      headword: entry.headword,
      source_printed_page: entry.source_printed_page ?? null,
      senses: entry.senses ?? [],
      additional_information: entry.additional_information ?? [],
      alternative_spellings: entry.alternative_spellings ?? [],
    }))

    resultCount.value = results.value.length

    if (results.value.length === 0) {
      errorMessage.value =
        'No matching entries found. Check the spelling and diacritics.'
    }
  } catch (error: unknown) {
    console.error('Dictionary search failed:', error)

    if (error instanceof TypeError) {
      errorMessage.value =
        'Could not reach the API. Check that FastAPI is running and that CORS allows this frontend.'
    } else if (error instanceof Error) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'An unexpected error occurred while searching.'
    }
  } finally {
    loading.value = false
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
        <label for="search">Search for a Nupe word</label>

        <div class="search-input">
          <input
            id="search"
            v-model="searchQuery"
            type="search"
            placeholder="Enter a Nupe headword..."
            autocomplete="off"
            :disabled="loading"
          />

          <button type="submit" :disabled="loading">
            {{ loading ? 'Searching…' : 'Search' }}
          </button>
        </div>

        <p class="hint">
          Enter a complete headword or an alternative spelling.
          Diacritics may be important.
        </p>
      </form>
    </section>

    <section
      class="results"
      aria-live="polite"
      :aria-busy="loading"
    >
      <p v-if="loading" class="status" role="status">
        Searching the dictionary…
      </p>

      <div v-else-if="errorMessage" class="status" role="status">
        {{ errorMessage }}
      </div>

      <div v-else-if="!hasSearched" class="empty-state">
        <h2>Start exploring</h2>
        <p>
          Enter a Nupe word above to look up its English definitions.
        </p>
      </div>

      <div v-else>
        <p class="result-count">
          {{ resultCount }}
          {{ resultCount === 1 ? 'entry' : 'entries' }} found
        </p>

        <article
          v-for="(entry, index) in results"
          :key="`${entry.headword}-${index}`"
          class="entry-card"
        >
          <div class="entry-heading">
            <h2>{{ entry.headword }}</h2>

            <span
              v-if="entry.source_printed_page != null"
              class="page-number"
            >
              Printed page {{ entry.source_printed_page }}
            </span>
          </div>

          <div
            v-if="entry.alternative_spellings.length > 0"
            class="entry-section"
          >
            <h3>Alternative spellings</h3>
            <p class="spellings">
              {{ entry.alternative_spellings.join(', ') }}
            </p>
          </div>

          <div class="entry-section">
            <h3>Definitions</h3>

            <ol v-if="entry.senses.length > 0" class="definitions">
              <li
                v-for="(sense, senseIndex) in entry.senses"
                :key="senseIndex"
              >
                <span
                  v-if="sense.part_of_speech"
                  class="part-of-speech"
                >
                  {{ sense.part_of_speech }}
                </span>

                <p>{{ sense.definition_en }}</p>

                <span
                  v-if="sense.category_code"
                  class="category"
                >
                  Category: {{ sense.category_code }}
                </span>
              </li>
            </ol>

            <p v-else>No definitions available for this entry.</p>
          </div>

          <div
            v-if="entry.additional_information.length > 0"
            class="entry-section additional"
          >
            <h3>Additional information</h3>

            <ul>
              <li
                v-for="(information, infoIndex) in entry.additional_information"
                :key="infoIndex"
              >
                {{ information }}
              </li>
            </ul>
          </div>
        </article>
      </div>
    </section>

    <footer>
      <p>
        Nupe Dictionary · A project to make Nupe vocabulary more accessible.
      </p>
    </footer>
  </main>
</template>

<style>

:root {
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  color: #202b27;
  background: #f7f8f5;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  text-align: left;
}

button,
input {
  font: inherit;
}

button:focus-visible,
input:focus-visible {
  outline: 3px solid #8ab49a;
  outline-offset: 3px;
}

.page {
  width: min(100% - 32px, 850px);
  margin: 0 auto;
}

.header {
  padding: 56px 0 32px;
  text-align: center;
}

.eyebrow {
  color: #47745d;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.14em;
}

h1 {
  margin: 12px 0 8px;
  color: #202b27;
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  line-height: 1.15;
  letter-spacing: -0.045em;
}

.subtitle {
  margin: 0;
  color: #65716a;
  font-size: 1rem;
  line-height: 1.5;
}

.search-section {
  padding: 28px;
  background: #fff;
  border: 1px solid #e4e9e3;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgb(30 50 35 / 5%);
}

.search-form label {
  display: block;
  margin-bottom: 10px;
  font-weight: 650;
}

.search-input {
  display: flex;
  gap: 10px;
}

.search-input input {
  width: 100%;
  min-width: 0;
  padding: 14px 16px;
  color: #202b27;
  background: #fff;
  border: 1px solid #d5ddd5;
  border-radius: 9px;
}

.search-input input:focus {
  border-color: #47745d;
}

.search-input button {
  padding: 0 23px;
  color: #fff;
  background: #315e49;
  border: 0;
  border-radius: 9px;
  cursor: pointer;
  font-weight: 650;
}

.search-input button:hover:not(:disabled) {
  background: #244b39;
}

.search-input button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.hint,
.status {
  margin: 12px 0 0;
  color: #65716a;
  font-size: 0.9rem;
  line-height: 1.6;
}

.results {
  min-height: 190px;
  padding: 30px 0;
  text-align: left;
}

.empty-state {
  padding: 30px 12px;
  text-align: center;
}

.empty-state h2 {
  color: #202b27;
  font-size: 1.2rem;
}

.empty-state p {
  color: #65716a;
  line-height: 1.6;
}

.result-count {
  margin: 0 0 16px;
  color: #65716a;
  font-size: 0.9rem;
}

.entry-card {
  margin-bottom: 18px;
  padding: 24px;
  color: #202b27;
  background: #fff;
  border: 1px solid #e0e7df;
  border-radius: 14px;
  text-align: left;
}

.entry-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8ece7;
}

.entry-heading h2 {
  margin: 0;
  color: #203b2d;
  font-size: 1.9rem;
  font-weight: 700;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.page-number {
  color: #65716a;
  font-size: 0.85rem;
}

.entry-section {
  margin-top: 22px;
}

.entry-section h3 {
  margin: 0 0 12px;
  color: #315e49;
  font-size: 1rem;
  font-weight: 700;
}

.entry-section p,
.entry-section li {
  color: #28332d;
  line-height: 1.65;
}

.entry-section p {
  margin-top: 6px;
  margin-bottom: 6px;
}

.spellings {
  overflow-wrap: anywhere;
}

.definitions {
  margin: 0;
  padding-left: 25px;
}

.definitions li {
  padding-left: 5px;
  margin-bottom: 16px;
}

.definitions li:last-child {
  margin-bottom: 0;
}

.definitions p {
  margin: 5px 0;
  white-space: normal;
  overflow-wrap: anywhere;
}

.part-of-speech {
  display: inline-block;
  color: #65716a;
  font-size: 0.9rem;
  font-style: italic;
}

.category {
  display: inline-block;
  margin-top: 4px;
  color: #65716a;
  font-size: 0.82rem;
}

.additional ul {
  margin: 0;
  padding-left: 25px;
}

.additional li {
  padding-left: 4px;
  margin-bottom: 8px;
}

.additional li:last-child {
  margin-bottom: 0;
}

footer {
  padding: 24px 0 35px;
  color: #65716a;
  text-align: center;
  font-size: 0.82rem;
  line-height: 1.6;
}

@media (max-width: 520px) {
  .header {
    padding-top: 48px;
  }

  .search-section {
    padding: 20px;
  }

  .search-input {
    flex-direction: column;
  }

  .search-input button {
    min-height: 46px;
  }

  .entry-card {
    padding: 18px;
  }

  .entry-heading h2 {
    font-size: 1.6rem;
  }
}

</style>
