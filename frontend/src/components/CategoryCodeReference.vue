<script setup lang="ts">
import { computed, ref } from "vue";
import { categoryCodes } from "../data/categoryCodes";

const query = ref("");

const filteredCodes = computed(() => {
  const term = query.value.trim().toLocaleLowerCase();
  if (!term) return categoryCodes;
  return categoryCodes.filter(({ code, meaning }) =>
    code.toLocaleLowerCase().includes(term) ||
    meaning.toLocaleLowerCase().includes(term)
  );
});
</script>

<template>
  <section class="category-code-reference" aria-labelledby="category-code-title">
    <header class="reference-header">
      <h2 id="category-code-title">Dictionary category codes</h2>
      <p>
        These codes identify subject categories used in the dictionary's third column.
        The definitions below are transcribed from the introductory material of the
        Nupe Dictionary draft.
      </p>
    </header>

    <label class="search-label" for="category-code-search">Search codes or meanings</label>
    <input
      id="category-code-search"
      v-model="query"
      class="search-input"
      type="search"
      placeholder="For example, “pl”, “plant”, or “animal”"
      autocomplete="off"
    />

    <p class="result-count" aria-live="polite">
      {{ filteredCodes.length }} {{ filteredCodes.length === 1 ? "code" : "codes" }}
    </p>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Code</th>
            <th scope="col">Meaning in the source</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredCodes" :key="item.code">
            <td><code>{{ item.code }}</code></td>
            <td>{{ item.meaning }}</td>
          </tr>
          <tr v-if="filteredCodes.length === 0">
            <td colspan="2" class="empty-state">No matching category codes.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="source-note">
      Source: R. M. Blench, <em>Nupe Dictionary</em>, “Key to codes used in column 3,”
      introductory PDF page 4 (printed page 1), draft printout dated August 5, 2009.
      The source is marked “Draft — prepared for comment only.”
    </p>
  </section>
</template>

<style scoped>
.category-code-reference {
  width: 100%;
  max-width: 900px;
  margin-inline: auto;
  color: var(--text-color, inherit);
}
.reference-header h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}
.reference-header p,
.source-note {
  line-height: 1.6;
  color: var(--muted-text-color, #666);
}
.search-label {
  display: block;
  margin: 1rem 0 0.4rem;
  font-weight: 600;
}
.search-input {
  box-sizing: border-box;
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--border-color, #c9c9c9);
  border-radius: 8px;
  background: var(--input-background, transparent);
  color: inherit;
  font: inherit;
}
.result-count {
  margin: 0.75rem 0 0.5rem;
  font-size: 0.9rem;
  color: var(--muted-text-color, #666);
}
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
th,
td {
  padding: 0.7rem 0.85rem;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  vertical-align: top;
}
th {
  background: var(--table-header-background, #f5f5f5);
  font-weight: 650;
}
tbody tr:last-child td {
  border-bottom: 0;
}
td:first-child {
  width: 5rem;
  white-space: nowrap;
}
td code {
  display: inline-block;
  min-width: 2rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid #7da88a;
  border-radius: 6px;
  background: #e2f2e5;
  color: #174d2a;
  font-size: 0.98rem;
  font-weight: 750;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.empty-state {
  padding: 1.25rem;
  text-align: center;
  color: var(--muted-text-color, #666);
}
.source-note {
  margin-top: 1rem;
  font-size: 0.85rem;
}
@media (max-width: 520px) {
  .reference-header h2 {
    font-size: 1.3rem;
  }
  th,
  td {
    padding: 0.6rem;
  }
}
</style>
