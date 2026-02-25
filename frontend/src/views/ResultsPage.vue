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

            <div v-if="sortMenuOpen" class="menu" role="menu">
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

        <div v-if="filterMenuOpen" class="menu" role="menu">
            <div class="menuSectionTitle">Category</div>

            <button
            v-for="c in categoryOptions"
            :key="c"
            class="menuItem"
            type="button"
            @click="toggleInArray(selectedCategories, c)"
            >
            <span>{{ c }}</span>
            <span v-if="selectedCategories.includes(c)" class="check">✓</span>
            </button>

            <div class="menuDivider"></div>

            <div class="menuSectionTitle">Demographic</div>

            <button
            v-for="d in demographicOptions"
            :key="d"
            class="menuItem"
            type="button"
            @click="toggleInArray(selectedDemographics, d)"
            >
            <span>{{ d }}</span>
            <span v-if="selectedDemographics.includes(d)" class="check">✓</span>
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

const filterMenuOpen = ref(false);
const selectedCategories = ref([]);     
const selectedDemographics = ref([]);   

const categoryOptions = computed(() => {
  // derive from fetched orgs so it stays accurate
  const set = new Set(results.value.map(o => String(o.category || "").trim()).filter(Boolean));
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

function toggleInArray(arrRef, value) {
  const arr = arrRef.value;
  if (value === "All") {
    arrRef.value = [];
    return;
  }
  const i = arr.indexOf(value);
  if (i >= 0) arr.splice(i, 1);
  else arr.push(value);
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
  if (!e.target.closest(".sortWrap")) sortMenuOpen.value = false;
  
}

onMounted(() => {
  document.addEventListener("click", onDocClick);
});

import { onBeforeUnmount } from "vue";
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
});

const selectedSubcategory = ref("All");
const subcategories = ref(["All", "Vouchers", "Pantries", "Free Meals", "Food Assistance"]);

const type = computed(() => String(route.params.type || ""));
const query = computed(() => decodeURIComponent(String(route.params.query || "")));

const headerText = computed(() => {
  if (!type.value || !query.value) return "Results";
  return type.value === "category" ? `Results for ${query.value}` : `Results for "${query.value}"`;
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
  let list = results.value;
  console.log("SORT MODE:", sortBy.value);

  // search-within-results
  const q = searchText.value.trim().toLowerCase();
  if (q) {
    list = list.filter((o) =>
      String(o.name || "").toLowerCase().includes(q)
    );
  }
    // category filter
  if (selectedCategories.value.length) {
    list = list.filter(o =>
      selectedCategories.value.includes(String(o.category || "").trim())
    );
  }

  if (selectedDemographics.value.length) {
    list = list.filter(o => {
      const d = (o.demographic || o.demographics || o.population || "");
      const hay = Array.isArray(d) ? d.join(" ").toLowerCase() : String(d).toLowerCase();
      return selectedDemographics.value.some(sel => hay.includes(sel.toLowerCase()));
    });
  }

// sort
if (sortBy.value === "az") {
  list = [...list].sort((a, b) => {
    const an = String(a?.name ?? "").trim().toLowerCase();
    const bn = String(b?.name ?? "").trim().toLowerCase();
    return an.localeCompare(bn);
  });
} else if (sortBy.value === "distance") {
    if (list.some(o => o.distance != null)) {
      list = [...list].sort(
        (a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity)
      );
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
  z-index: 20;
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
}

.menuItem:hover {
  background: rgba(37, 99, 235, 0.10);
}

.filterWrap {
  position: relative;
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