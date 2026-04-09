<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const allOrgs = ref([]);

const UI_CATEGORIES = [
  "Food",
  "Housing",
  "Health",
  "Education & Work",
  "Legal & Financial",
  "Transportation",
  "Family Services",
  "Community Programs"
];

function mapToUICategory(org) {
  const category = String(org?.category || "").toUpperCase();
  const name = String(org?.name || "")
    .toUpperCase()
    .replace(/[^A-Z0-9 ]/g, "");
  const details = String(org?.data?.[1] || "").toUpperCase();
  const func = String(org?.data?.[7] || "").toUpperCase();

  const text = `${category} ${name} ${details} ${func}`;

// MANUAL LEGAL MATCHES
if (
  name.includes("BLUE MOUNTAIN ACTION COUNCIL") ||
  name.includes("CLEAR HOTLINE") ||
  name.includes("COLUMBIA LEGAL SERVICES") ||
  name.includes("NEUTRAL GROUND DISPUTE RESOLUTION") ||
  name.includes("NORTHWEST IMMIGRANTS RIGHTS PROJECT") ||
  name.includes("NORTHWEST JUSTICE PROJECT") ||
  name.includes("COURT APPOINTED SPECIAL ADVOCATES") ||
  name.includes("LEGAL AID SERVICES OF OREGON") ||
  name.includes("WALLA WALLA COUNTY CRIME VICTIM ADVOCATES") ||
  name.includes("WASHINGTON CASA") ||
  name.includes("COLLEGE PLACE POLICE") ||
  name.includes("COLUMBIA COUNTY SHERIFF") ||
  name.includes("MILTON-FREEWATER POLICE") ||
  name.includes("NON-EMERGENCY DISPATCH") ||
  name.includes("UMATILLA COUNTY SHERIFF") ||
  name.includes("WALLA WALLA COUNTY SHERIFF") ||
  name.includes("WALLA WALLA POLICE") ||
  name.includes("COUNSELING SERVICES FOR DV OFFENDERS") ||
  name.includes("NATIONAL CHILD ABUSE HOTLINE") ||
  name.includes("OREGON CHILDREN'S SERVICES") ||
  name.includes("OREGON SAFENET") ||
  name.includes("UMATILLA -MORROW DV CRISIS LINE") ||
  name.includes("WASHINGTON ADULT AND CHILD PROTECTIVE SERVICES") ||
  name.includes("YWCA LINC") ||
  name.includes("YWCA 24 HOUR CRISIS LINE") ||
  name.includes("WALLA WALLA VALLEY DIVERGENCE") ||
  name.includes("WALLA WALLA LEAD") ||
  name.includes("YWCA HUMAN TRAFFICKING ADVOCACY")
) {
  return "Legal & Financial";
}

// MANUAL FAMILY SERVICES MATCHES
if (
  // Parenting, Childcare & Early Learning
  name.includes("MY FRIENDS HOUSE PRESCHOOL") ||
  name.includes("ADVENTURE CLUB") ||
  name.includes("KIDS KORNER") ||
  name.includes("LITTLE OWLS PRESCHOOL") ||
  name.includes("EARLY LEARNING CENTER") ||
  name.includes("CHILD CARE AWARE") ||
  name.includes("OREGON CHILD DEVELOPMENT COALITION") ||
  name.includes("HEAD START") ||
  name.includes("THE KIDS PLACE") ||

  // Parenting Education & Family Support
  name.includes("WWCC PARENT EDUCATION") ||
  name.includes("PARENT CO OP") ||
  name.includes("PARENT CO-OP") ||
  name.includes("EARLY LEARNING COALITION") ||
  name.includes("CATHOLIC CHARITIES") ||

  // Youth Programs
  name.includes("FRIENDS OF CHILDREN") ||
  name.includes("CAMP FIRE") ||
  name.includes("PARKS AND RECREATION") ||
  name.includes("PARKS & RECREATION") ||
  name.includes("4 H CLUB") ||

  //Family / Child Welfare
  name.includes("CHILDRENS HOME SOCIETY") ||
  name.includes("CHILDREN'S HOME SOCIETY") ||
  name.includes("DIVISION OF CHILDREN AND FAMILY SERVICES") ||
  name.includes("GOOD SAMARITAN MINISTRIES")
) {
  return "Family Services";
}

  // MANUAL TRANSPORTATION MATCHES
  if (
    name.includes("COLUMBIA COUNTY PUBLIC TRANSPORTATION") ||
    name.includes("GORGE TRANSLINK") ||
    name.includes("GRAPELINE BUS LINE") ||
    name.includes("KAYAK BUS LINE") ||
    name.includes("MILTON-FREEWATER CITY BUS") ||
    name.includes("PEOPLE FOR PEOPLE MEDICAID TRANSPORTATION") ||
    name.includes("VALLEY TRANSIT BUS SERVICE") ||
    name.includes("VALLEY TRANSIT DIAL-A-RIDE") ||
    name.includes("VALLEY TRANSIT JOB ACCESS") ||
    name.includes("VETERANS TRANSPORTATION SERVICE")
  ) {
    return "Transportation";
  }

  if (text.includes("FOOD")) return "Food";

  if (
    text.includes("HOUSING") ||
    text.includes("SHELTER") ||
    text.includes("HOMELESS") ||
    text.includes("RENT") ||
    text.includes("UTILITY") ||
    text.includes("UTILITIES")
  ) {
    return "Housing";
  }

  if (
    text.includes("HEALTH") ||
    text.includes("MENTAL") ||
    text.includes("MEDICAL") ||
    text.includes("COUNSELING") ||
    text.includes("CLINIC")
  ) {
    return "Health";
  }

  if (
    text.includes("EDUCATION") ||
    text.includes("EMPLOYMENT") ||
    text.includes("WORK") ||
    text.includes("JOB") ||
    text.includes("SCHOOL") ||
    text.includes("COLLEGE")
  ) {
    return "Education & Work";
  }

  return "Community Programs";
}

const filterMenuOpen = ref(false);
const selectedCategories = ref([]);       

const language = ref("en");
const translateToSpanish = window.translateToSpanish
const translateToEnglish = window.translateToEnglish

const categoryOptions = ["All", ...UI_CATEGORIES];


function toggleCategory(value) {
  if (value === "All") {
    selectedCategories.value = [];
    return;
  }
  // single-select: pick one category at a time
  selectedCategories.value = [value];
}


const activeFilterLabel = computed(() => {
  if (selectedCategories.value.length) {
    return `${selectedCategories.value.length} categories`;
  }
  return "All";
});

const route = useRoute();
const router = useRouter();

const type = computed(() => String(route.params.type || ""));
const query = computed(() => decodeURIComponent(String(route.params.query || "")));

const loading = ref(true);
const errorMsg = ref("");

const searchText = ref("");
const sortBy = ref("az");
const sortMenuOpen = ref(false);

const sortLabel = computed(() => {
  if (sortBy.value === "az") return "A → Z";
  if (sortBy.value === "za") return "Z → A";
  return "A → Z";
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
  let list = allOrgs.value;

  // use selected filter category first, otherwise route category/search
  if (selectedCategories.value.length) {
    const picked = selectedCategories.value[0];
    list = list.filter(o => mapToUICategory(o) === picked);
  } else {
    if (type.value === "category") {
      list = list.filter(o => mapToUICategory(o) === query.value);
    } else if (query.value) {
      list = list.filter(o =>
        String(o.name || "").toUpperCase().includes(query.value.toUpperCase())
      );
    }
  }


  // search within results
  const q = searchText.value.trim().toLowerCase();
  if (q) {
    list = list.filter(o => String(o.name || "").toLowerCase().includes(q));
  }

  const set = new Set();
  for (const org of list) {
    for (const s of getOrgSubcats(org)) set.add(s);
  }

  return ["All", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
});

watch(subcategories, () => {
  if (!subcategories.value.includes(selectedSubcategory.value)) {
    selectedSubcategory.value = "All";
  }
});

const headerText = computed(() => {
  const activeCat = selectedCategories.value.length
    ? selectedCategories.value[0]
    : (type.value === "category" ? query.value : null);

  const parts = [];

  if (activeCat) parts.push(activeCat);
  else if (query.value) parts.push(`"${query.value}"`);

  if (selectedSubcategory.value !== "All") {
    parts.push(`Sub-Category: ${selectedSubcategory.value}`);
  }

  return parts.length ? `Results for ${parts.join(" • ")}` : "Results";
});

function goBack() {
  router.back();
}

function scrollToSearchTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openResource(name) {
  router.push(`/resource/${encodeURIComponent(name)}`);
}

async function getResults() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await fetch("https://service-provider-database-lb3m.onrender.com/api/organizations");
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);

    const data = await res.json();
    allOrgs.value = data;

    console.log("RAW CATEGORIES:", [...new Set(data.map(o => o.category))]);

    searchText.value = "";
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.message || "Error fetching results";
    allOrgs.value = [];
  } finally {
    loading.value = false;
  }
}

watch(() => route.fullPath, getResults);

onMounted(getResults);

const filteredResults = computed(() => {
  let list = allOrgs.value;

  // selected filter category overrides route category
  if (selectedCategories.value.length) {
    const picked = selectedCategories.value[0];
    list = list.filter(o => mapToUICategory(o) === picked);
  } else {
    if (type.value === "category") {
      list = list.filter(o => mapToUICategory(o) === query.value);
    } else if (query.value) {
      list = list.filter(o =>
        String(o.name || "").toUpperCase().includes(query.value.toUpperCase())
      );
    }
  }

  // search within results
  const q = searchText.value.trim().toLowerCase();
  if (q) {
    list = list.filter(o => String(o.name || "").toLowerCase().includes(q));
  }

  // subcategory chip filter
  if (selectedSubcategory.value !== "All") {
    list = list.filter(org => getOrgSubcats(org).includes(selectedSubcategory.value));
  }

if (sortBy.value === "az") {
  list = [...list].sort((a, b) =>
    String(a?.name ?? "").trim().toLowerCase()
      .localeCompare(String(b?.name ?? "").trim().toLowerCase())
  );
} else if (sortBy.value === "za") {
  list = [...list].sort((a, b) =>
    String(b?.name ?? "").trim().toLowerCase()
      .localeCompare(String(a?.name ?? "").trim().toLowerCase())
  );
}

  return list;
});


</script>

<template>
  <div class="page">
    <header class="topbar">
    <div class="navLeft">
        <button class="iconBtn" type="button" @click="goBack" aria-label="Go back">←</button>
    </div>

    <div class="centerTitle">
      Search
    </div>

    <nav class="topNav">
      <router-link to="/" class="navLink">Home</router-link>

      <router-link to="/results" class="navLink">
        Search
      </router-link>

      <router-link to="/about" class="navLink">About</router-link>

      <select
        class="languageSelect"
        @change="$event.target.value === 'es' ? translateToSpanish() : translateToEnglish()"
      >
        <option value="en">English</option>
        <option value="es">Español</option>
      </select>
    </nav>
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
              <button class="menuItem" @click="setSort('az')">
                Alphabetical (A–Z)
              </button>

              <button class="menuItem" @click="setSort('za')">
                Alphabetical (Z–A)
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

        <div class="menuFooter">
            <button
            class="menuAction"
            type="button"
            @click="selectedCategories = []"
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

            <p class="meta">Category: {{ mapToUICategory(org) }}</p>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page {
  --bar: #DBE2EF;
  --pill: #F5F5F5;
  --card: #F5F5F5;
  --chip: #F0F0F0;
  --ink: #2f3e36;
  --muted: #4b5563;
  --accent: #2563eb;

  min-height: 100vh;
  background: #fff;
  color: var(--ink);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

.topbar {
  background: var(--bar);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navLeft {
  display: flex;
  align-items: center;
}

.topNav {
  display: flex;
  gap: 18px;
  align-items: center;
}

.navLink {
  text-decoration: none;
  font-family: "Cormorant Garamond", serif;
  font-size: 18px;
  font-weight: 600;
  color: #2f3e36;
  letter-spacing: 0.4px;
}

.navLink:hover {
  color: var(--accent);
}

.languageSelect {
  font-family: "Cormorant Garamond", serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  color: #2f3e36;
  cursor: pointer;
}

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
  background: var(--chip);
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

.centerTitle {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-family: "Cormorant Garamond", serif;
  font-size: 20px;
  font-weight: 700;
  color: #2f3e36;
  white-space: nowrap;
}

.cardTitle { margin: 0; font-size: 18px; font-weight: 900; }
.chev { font-size: 22px; opacity: 0.65; }

.meta { margin: 8px 0 0; color: var(--muted); font-weight: 800; }
</style>