<template>
  <div class="page">
    <header class="topbar">
      <button class="iconBtn" type="button" @click="goBack" aria-label="Go back">←</button>
      <h1 class="title">Results</h1>
      <div class="spacer" aria-hidden="true"></div>
    </header>

    <main class="main">
      <!-- Search within results -->
      <div class="searchPill" role="search" aria-label="Search results">
        <input
          class="searchInput"
          v-model="searchText"
          placeholder="Search results"
        />
        <span class="searchIcon" aria-hidden="true">🔍</span>
      </div>

      <!-- Sort + Filter row -->

      <div class="controlsRow">
            <div class="sortWrap">
            <button
                class="chipBtn"
                type="button"
                @click="sortMenuOpen = !sortMenuOpen"
                aria-haspopup="menu"
                :aria-expanded="sortMenuOpen"
            >
                Sort: <span class="chipValue">{{ sortLabel }}</span> ▾
            </button>

            <div v-if="sortMenuOpen" class="menu" role="menu" @click.stop>
                <button class="menuItem" type="button" role="menuitem" @click="setSort('relevance')">
                Relevance
                </button>
                <button class="menuItem" type="button" role="menuitem" @click="setSort('az')">
                Alphabetical (A–Z)
                </button>
                <button class="menuItem" type="button" role="menuitem" @click="setSort('distance')">
                Distance
                </button>
            </div>
            </div>

        <div class="filterWrap">
        <button
            class="chipBtn"
            type="button"
            @click="filterMenuOpen = !filterMenuOpen"
            aria-haspopup="menu"
            :aria-expanded="filterMenuOpen"
        >
            Filter: <span class="chipValue">{{ activeFilterLabel }}</span> ▾
        </button>

        <div v-if="filterMenuOpen" class="menu" role="menu" @click.stop>
        <div class="menuSectionTitle">Category</div>

        <button
            v-for="c in categoryOptions"
            :key="`cat-${c}`"
            class="menuItem"
            :class="{ selected: selectedCategories.includes(c) }"
            type="button"
            @click="toggleCategory(c)"
        >
            <span>{{ c }}</span>
            <span class="check" v-if="selectedCategories.includes(c)">✓</span>
        </button>

        <div class="menuDivider"></div>

        <div class="menuSectionTitle">Demographic</div>

        <button
            v-for="d in demographicOptions"
            :key="`demo-${d}`"
            class="menuItem"
            :class="{ selected: selectedDemographics.includes(d) }"
            type="button"
            @click="toggleDemographic(d)"
        >
            <span>{{ d }}</span>
            <span class="check" v-if="selectedDemographics.includes(d)">✓</span>
        </button>

        <div class="menuFooter">
            <button
            class="menuAction"
            type="button"
            @click="selectedCategories = []; selectedDemographics = []"
            >
            Clear
            </button>

            <button class="menuAction primary" type="button" @click="filterMenuOpen = false">
            Done
            </button>
        </div>
        </div>
        </div>
      </div>

      <!-- Sub-categories (UI only, optional data effect) -->
      <section class="subcats">
        <h2 class="subcatsLabel">Sub-Categories</h2>
        <div class="subcatsRow">
          <button
            v-for="s in subcategories"
            :key="s"
            class="subcatChip"
            :class="{ active: selectedSubcategory === s }"
            type="button"
            @click="selectedSubcategory = s"
          >
            {{ s }}
          </button>
        </div>
      </section>

      <!-- Results -->
      <section class="resultsSection">
        <div class="resultsHeader">
          <h2 class="resultsH2">{{ headerText }}</h2>
          <p class="count" v-if="!loading && !errorMsg">{{ filteredResults.length }} found</p>
        </div>

        <p class="state" v-if="loading">Loading…</p>
        <p class="state error" v-else-if="errorMsg">{{ errorMsg }}</p>
        <p class="state" v-else-if="filteredResults.length === 0">No results. Try another search.</p>

        <div class="list" v-else>
          <article
            v-for="org in filteredResults"
            :key="org.name"
            class="card"
            role="button"
            tabindex="0"
            @click="openResource(org.name)"
            @keyup.enter="openResource(org.name)"
          >
            <div class="cardTop">
              <h3 class="cardTitle">{{ org.name }}</h3>
              <span class="chev" aria-hidden="true">›</span>
            </div>

            <p class="meta" v-if="org.category">Category: {{ org.category }}</p>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const allOrgs = ref([]);

const filterMenuOpen = ref(false);
const selectedCategories = ref([]);     
const selectedDemographics = ref([]);   

const categoryOptions = computed(() => {
  const set = new Set(allOrgs.value.map(o => String(o.category || "").trim()).filter(Boolean));
  return ["All", ...Array.from(set).sort((a,b)=>a.localeCompare(b))];
});

const demographicOptions = ref([
  "All",
  "Youth",
  "Seniors",
  "Veterans",
  "Disability",
  "LGBTQ+",
  "Low Income",
]);

function toggleCategory(value) {
  if (value === "All") {
    selectedCategories.value = [];
    return;
  }
  // single-select: pick one category at a time
  selectedCategories.value = [value];
}

function toggleDemographic(value) {
  if (value === "All") {
    selectedDemographics.value = [];
    return;
  }
  const arr = [...selectedDemographics.value];
  const i = arr.indexOf(value);
  if (i >= 0) arr.splice(i, 1);
  else arr.push(value);
  selectedDemographics.value = arr;
}

const activeFilterLabel = computed(() => {
  const parts = [];
  if (selectedCategories.value.length) parts.push(`${selectedCategories.value.length} categories`);
  if (selectedDemographics.value.length) parts.push(`${selectedDemographics.value.length} demographics`);
  return parts.length ? parts.join(" • ") : "All";
});

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const errorMsg = ref("");
const results = ref([]);

const searchText = ref("");
const sortBy = ref("relevance"); 
const sortMenuOpen = ref(false);

const sortLabel = computed(() => {
  if (sortBy.value === "az") return "Alphabetical";
  if (sortBy.value === "distance") return "Distance";
  return "Relevance";
});
function setSort(option) {
  sortBy.value = option;
  sortMenuOpen.value = false;
}

function onDocClick(e) {
  // close sort if click outside sort
  if (!e.target.closest(".sortWrap")) sortMenuOpen.value = false;

  // close filter if click outside filter
  if (!e.target.closest(".filterWrap")) filterMenuOpen.value = false;
}

onMounted(() => {
  document.addEventListener("click", onDocClick);
});

import { onBeforeUnmount } from "vue";
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
});

const selectedSubcategory = ref("All");
function getOrgSubcats(org) {
  // adjust these keys to match your backend if needed
  const raw =
    org.subcategories ??
    org.subcategory ??
    org.services ??
    org.service ??
    org.tags ??
    org.tag ??
    [];

  if (Array.isArray(raw)) return raw.map(s => String(s).trim()).filter(Boolean);

  return String(raw)
    .split(",")
    .map(s => s.trim())
    .filter(Boolean);
}

const subcategories = computed(() => {
  // build subcats from the list AFTER search/category/demographic filters
  let list = results.value;

  watch(subcategories, () => {
  if (!subcategories.value.includes(selectedSubcategory.value)) {
    selectedSubcategory.value = "All";
  }
});

  // search-within-results
  const q = searchText.value.trim().toLowerCase();
  if (q) {
    list = list.filter(o => String(o.name || "").toLowerCase().includes(q));
  }

  // category filter
  if (selectedCategories.value.length) {
    list = list.filter(o =>
      selectedCategories.value.includes(String(o.category || "").trim())
    );
  }

  // demographic filter
  if (selectedDemographics.value.length) {
    list = list.filter(o => {
      const d = (o.demographic || o.demographics || o.population || "");
      const hay = Array.isArray(d) ? d.join(" ").toLowerCase() : String(d).toLowerCase();
      return selectedDemographics.value.some(sel => hay.includes(sel.toLowerCase()));
    });
  }

  const set = new Set();
  for (const org of list) {
    for (const s of getOrgSubcats(org)) set.add(s);
  }

  return ["All", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
});

const type = computed(() => String(route.params.type || ""));
const query = computed(() => decodeURIComponent(String(route.params.query || "")));

const headerText = computed(() => {
  const parts = [];

  // base route context
  if (type.value === "category" && query.value) parts.push(query.value);
  else if (query.value) parts.push(`"${query.value}"`);

  // active filters
  if (selectedCategories.value.length) parts.push(`Category: ${selectedCategories.value.join(", ")}`);
  if (selectedDemographics.value.length) parts.push(`Demographic: ${selectedDemographics.value.join(", ")}`);
  if (selectedSubcategory.value !== "All") parts.push(`Sub-Category: ${selectedSubcategory.value}`);

  return parts.length ? `Results for ${parts.join(" • ")}` : "Results";
});

function goBack() {
  router.back();
}

function openResource(name) {
  router.push(`/resource/${encodeURIComponent(name)}`);
}

async function getResults() {
  loading.value = true;
  errorMsg.value = "";
  try {
    // ✅ same endpoint your old page used
    const res = await fetch("http://127.0.0.1:5000/api/organizations");
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);

    const data = await res.json();
    allOrgs.value = data;
    if (!Array.isArray(data)) {
      results.value = [];
      return;
    }

    // apply the exact same filtering logic you had
    const q = query.value;

    if (type.value === "category") {
      results.value = data.filter((org) => String(org.category || "").toUpperCase() === q.toUpperCase());
    } else {
      results.value = data.filter((org) => String(org.name || "").toUpperCase().includes(q.toUpperCase()));
    }

    // initialize local search field to the route query (nice UX)
    searchText.value = "";
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.message || "Error fetching results";
    results.value = [];
  } finally {
    loading.value = false;
  }
}

watch(() => route.fullPath, getResults);

onMounted(getResults);

const filteredResults = computed(() => {
  let list = allOrgs.value;

  // 1) CATEGORY SOURCE:
  // If user picked a category in the filter dropdown, use that.
  // Otherwise fall back to the route category/search.
  if (selectedCategories.value.length) {
    const picked = selectedCategories.value[0];
    list = list.filter(o => String(o.category || "").trim().toUpperCase() === picked.toUpperCase());
  } else {
    // fall back to route behavior
    if (type.value === "category") {
      const q = query.value;
      list = list.filter(o => String(o.category || "").trim().toUpperCase() === q.toUpperCase());
    } else {
      const q = query.value;
      if (q) {
        list = list.filter(o => String(o.name || "").toUpperCase().includes(q.toUpperCase()));
      }
    }
  }

  // 2) demographic filter
  if (selectedDemographics.value.length) {
    list = list.filter(o => {
      const d = (o.demographic || o.demographics || o.population || "");
      const hay = Array.isArray(d) ? d.join(" ").toLowerCase() : String(d).toLowerCase();
      return selectedDemographics.value.some(sel => hay.includes(sel.toLowerCase()));
    });
  }

  // 3) search-within-results
  const q2 = searchText.value.trim().toLowerCase();
  if (q2) list = list.filter(o => String(o.name || "").toLowerCase().includes(q2));

  // 4) sort
  if (sortBy.value === "az") {
    list = [...list].sort((a, b) =>
      String(a?.name ?? "").trim().toLowerCase().localeCompare(String(b?.name ?? "").trim().toLowerCase())
    );
  } else if (sortBy.value === "distance") {
    if (list.some(o => o.distance != null)) {
      list = [...list].sort((a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity));
    }
  }

  return list;
});


</script>

<style scoped>
.page {
  --bar: #e6e6e6;
  --pill: #efefef;
  --card: #dedede;
  --ink: #2f3e36;
  --muted: #4b5563;
  --accent: #2563eb;

  min-height: 100vh;
  background: #fff;
  color: var(--ink);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bar);
  padding: 14px 16px;
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

.title {
  margin: 0;
  text-align: center;
  font-family: "Cormorant Garamond", serif;
  font-size: 28px;
  font-weight: 800;
}

.spacer { width: 44px; height: 44px; }

.iconBtn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 999px;
  background: rgba(255,255,255,0.75);
  cursor: pointer;
  font-size: 20px;
}

.main {
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.searchPill {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--pill);
  border-radius: 999px;
  padding: 12px 14px;
}

.searchInput {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
}

.searchIcon { opacity: 0.7; }

.controlsRow {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.sortWrap {
  position: relative;
  z-index: 9999;
  flex: 1;
}

.menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 14px;
  padding: 8px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0, 0, 0, 0.08);
  z-index: 9999;
}

.menuItem {
  width: 100%;
  border: none;
  background: transparent;
  padding: 10px 12px;
  border-radius: 12px;
  text-align: left;
  font-weight: 900;
  cursor: pointer;
  color: var(--ink);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menuItem.selected {
  background: rgba(37, 99, 235, 0.12);
  outline: 2px solid rgba(37, 99, 235, 0.35);
}

.menuItem:hover {
  background: rgba(37, 99, 235, 0.10);
}

.filterWrap {
  position: relative;
  z-index: 9999;
  flex: 1;
}

.menuSectionTitle {
  font-weight: 900;
  font-size: 12px;
  color: var(--muted);
  padding: 6px 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.menuDivider {
  height: 1px;
  background: rgba(0,0,0,0.08);
  margin: 8px 0;
}

.check {
  font-weight: 900;
}

.menuFooter {
  display: flex;
  gap: 10px;
  padding-top: 8px;
}

.menuAction {
  flex: 1;
  border: none;
  background: #efefef;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 900;
  cursor: pointer;
}

.menuAction.primary {
  background: var(--accent);
  color: white;
}

.chipBtn {
  flex: 1;
  border: none;
  background: #e2e2e2;
  border-radius: 999px;
  padding: 10px 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  justify-content: center;
  gap: 8px;
  align-items: center;
}

.chipValue { font-weight: 900; }

.subcats { margin-top: 16px; }

.subcatsLabel {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 900;
}

.subcatsRow {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 6px;
}

.subcatChip {
  border: none;
  background: #d8d8d8;
  border-radius: 14px;
  padding: 10px 12px;
  font-weight: 900;
  white-space: nowrap;
  cursor: pointer;
}

.subcatChip.active {
  background: var(--accent);
  color: #fff;
}

.resultsSection { margin-top: 18px; }

.resultsHeader {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.resultsH2 {
  margin: 0;
  font-family: "Cormorant Garamond", serif;
  font-size: 24px;
  font-weight: 800;
}

.count {
  margin: 0;
  color: var(--muted);
  font-weight: 800;
}

.state { margin-top: 12px; color: var(--muted); font-weight: 800; }
.state.error { color: #b42318; }

.list {
  margin-top: 12px;
  display: grid;
  gap: 12px;
}

.card {
  background: var(--card);
  border-radius: 18px;
  padding: 14px;
  cursor: pointer;
}

.cardTop {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.cardTitle { margin: 0; font-size: 18px; font-weight: 900; }
.chev { font-size: 22px; opacity: 0.65; }

.meta { margin: 8px 0 0; color: var(--muted); font-weight: 800; }
</style>