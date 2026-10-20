<script setup lang="ts">
import { ref } from "vue";

const activeSection = ref("entry");
</script>

<template>
  <article class="reading-guide" aria-label="How to use the Nupe dictionary">
    <nav class="guide-nav" aria-label="Reading guide sections">
      <button
        v-for="section in [
          { id: 'entry', label: 'Reading an entry' },
          { id: 'orthography', label: 'Spelling and sounds' },
          { id: 'tones', label: 'Tones and diacritics' },
          { id: 'keyboard', label: 'Typing characters' },
          { id: 'codes', label: 'Category codes' },
        ]"
        :key="section.id"
        type="button"
        :class="{ active: activeSection === section.id }"
        @click="activeSection = section.id"
      >
        {{ section.label }}
      </button>
    </nav>

    <section v-if="activeSection === 'entry'" class="guide-content">
      <h3>Reading a dictionary entry</h3>
      <p>Each entry in this web app may contain several kinds of information:</p>
      <ul>
        <li><strong>Nupe headword:</strong> the word or expression being described. Keep its diacritics as shown.</li>
        <li><strong>Alternative spellings:</strong> other spellings recorded for the entry, when available.</li>
        <li><strong>Part of speech:</strong> grammatical information for a sense, when supplied in the data.</li>
        <li><strong>English definition:</strong> the meaning recorded for that sense. An entry can have more than one sense.</li>
        <li><strong>Category code:</strong> a short subject label explained in the category-code reference.</li>
        <li><strong>Notes from the dictionary:</strong> additional information retained from the source, when available.</li>
        <li><strong>Source page:</strong> the printed page number associated with the entry, when available.</li>
      </ul>
      <p class="guide-note">Not every entry has every field. The app displays information available in its structured data; it does not imply that missing information is absent from Nupe generally.</p>
    </section>

    <section v-else-if="activeSection === 'orthography'" class="guide-content">
      <h3>Nupe spelling and sounds</h3>
      <p>The supplied introductory material describes five vowels: <span class="sample-characters">i, e, a, o, u</span>.</p>
      <p>It also describes spellings that use more than one letter to represent a single sound:</p>
      <div class="character-examples">
        <div><code>c</code><span>represents the sound written <code>tʃ</code> in the source's phonetic description.</span></div>
        <div><code>j</code><span>represents the sound written <code>dʒ</code> in the source's phonetic description.</span></div>
        <div><code>ts · dz · gb · kp</code><span>the source describes these as combinations of letters representing single sounds.</span></div>
      </div>
      <p>The source's alphabetical order places combinations such as <code>gb</code> under <code>g</code>, rather than giving them separate alphabet headings.</p>
      <p class="guide-note">These explanations follow the supplied draft's “Nupe orthography” section. The document notes that its transcriptions may differ from locally published materials.</p>
    </section>

    <section v-else-if="activeSection === 'tones'" class="guide-content">
      <h3>Tones, nasalisation, and diacritics</h3>
      <p>The supplied draft describes five tone patterns:</p>
      <div class="tone-grid">
        <div><strong>High</strong><span class="tone-mark">◌́</span></div>
        <div><strong>Mid</strong><span class="tone-mark">Unmarked</span></div>
        <div><strong>Low</strong><span class="tone-mark">◌̀</span></div>
        <div><strong>Rising</strong><span class="tone-mark">◌̌</span></div>
        <div><strong>Falling</strong><span class="tone-mark">◌̂</span></div>
      </div>
      <p>The source says tones are marked where possible, but some words in the draft may lack tone marking because certain transcriptions had not been rechecked in the field.</p>
      <p>It also discusses nasalised vowels and notes that representing nasalisation is a difficult aspect of the orthography. The examples in the source show that pronunciation and representation can vary.</p>
      <p class="guide-note">The marks above illustrate the tone-mark shapes described by the source; they are not a complete pronunciation guide for every word. Preserve the exact spelling shown in each dictionary entry.</p>
    </section>

    <section v-else-if="activeSection === 'keyboard'" class="guide-content">
      <h3>Searching and typing special characters</h3>
      <ol>
        <li>Open <strong>Nupe character keyboard</strong> near the search field.</li>
        <li>Choose <strong>Show keys</strong> to reveal the character forms observed in the dictionary data.</li>
        <li>Select a key to insert that character at the cursor in the search field.</li>
        <li>Search for a full word or a shorter character sequence. The search is designed to help find words even when you do not enter every diacritic.</li>
      </ol>
      <p>Search results retain the dictionary's original spelling. When comparing words, pay attention to the exact marks displayed in the headword.</p>
    </section>

    <section v-else class="guide-content">
      <h3>Understanding category codes</h3>
      <p>Category codes identify subject areas used in the dictionary's third column. For example:</p>
      <div class="code-examples">
        <span><code>f</code> Fish</span>
        <span><code>k</code> Kinship</span>
        <span><code>pl</code> Plant</span>
        <span><code>t</code> Tree</span>
      </div>
      <p>Use the <strong>Dictionary category codes</strong> section on the main page to search the full list by code or meaning. When a code is present on a search result, its meaning is shown beside it.</p>
      <p class="guide-note">The definitions are transcribed from the supplied Nupe Dictionary draft's “Key to codes used in column 3.”</p>
    </section>

    <p class="source-note">
      Source note: R. M. Blench, <em>Nupe Dictionary: Introductory Material</em>, draft printout dated August 5, 2009, supplied pages 2–4 of the PDF. The document is marked “Draft — prepared for comment only”; this guide summarizes those pages and the fields displayed by this web app.
    </p>
  </article>
</template>

<style scoped>
.reading-guide {
  margin-top: 1.25rem;
  padding: 1.1rem;
  border: 1px solid #dfe8de;
  border-radius: 12px;
  background: #fbfcfa;
}
.guide-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
}
.guide-nav button {
  min-height: 38px;
  padding: 0.45rem 0.7rem;
  border: 1px solid #cbdacb;
  border-radius: 7px;
  background: #fff;
  color: #315e49;
  font: inherit;
  font-size: 0.88rem;
  cursor: pointer;
}
.guide-nav button.active {
  background: #315e49;
  border-color: #315e49;
  color: #fff;
}
.guide-content h3 {
  margin: 0 0 0.75rem;
  color: #203b2d;
  font-size: 1.1rem;
}
.guide-content p,
.guide-content li {
  line-height: 1.7;
}
.guide-content ul,
.guide-content ol {
  padding-left: 1.4rem;
}
.guide-content li {
  margin-bottom: 0.45rem;
}
.sample-characters {
  font-weight: 700;
  letter-spacing: 0.06em;
}
.character-examples {
  display: grid;
  gap: 0.6rem;
  margin: 1rem 0;
}
.character-examples > div {
  display: grid;
  grid-template-columns: minmax(6rem, auto) 1fr;
  gap: 0.75rem;
  align-items: start;
  padding: 0.7rem;
  border: 1px solid #e0e8df;
  border-radius: 8px;
  background: #fff;
}
.character-examples code,
.code-examples code {
  display: inline-block;
  padding: 0.2rem 0.45rem;
  border: 1px solid #7da88a;
  border-radius: 5px;
  background: #e2f2e5;
  color: #174d2a;
  font-weight: 750;
}
.tone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.55rem;
  margin: 1rem 0;
}
.tone-grid > div {
  display: flex;
  min-height: 76px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem;
  border: 1px solid #dfe8de;
  border-radius: 8px;
  background: #fff;
}
.tone-mark {
  color: #174d2a;
  font-size: 1.25rem;
  font-weight: 750;
}
.code-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin: 1rem 0;
}
.code-examples span {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.6rem;
  border: 1px solid #e0e8df;
  border-radius: 7px;
  background: #fff;
}
.guide-note {
  padding: 0.8rem;
  border-left: 3px solid #8aaf96;
  background: #f0f6ef;
  color: #405b49;
  font-size: 0.9rem;
}
.source-note {
  margin: 1.25rem 0 0;
  padding-top: 0.9rem;
  border-top: 1px solid #e0e8df;
  color: #65716a;
  font-size: 0.82rem;
  line-height: 1.6;
}
@media (max-width: 520px) {
  .reading-guide { padding: 0.8rem; }
  .guide-nav { display: grid; grid-template-columns: 1fr 1fr; }
  .guide-nav button { text-align: left; }
  .character-examples > div { grid-template-columns: 1fr; gap: 0.35rem; }
}
</style>
