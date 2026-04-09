<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const allOrgs = ref([]);
const resultsScrollRef = ref(null);

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

const DEMOGRAPHIC_OPTIONS = [
  "All",
  "Men",
  "Women",
  "LGBTQ+",
  "Hispanic/Latino",
  "Native American",
  "Black/African American",
  "Asian"
];

function forwardScroll(e) {
  const el = resultsScrollRef.value;
  if (!el) return;

  const canScroll = el.scrollHeight > el.clientHeight;
  if (!canScroll) return;

  el.scrollTop += e.deltaY;
  e.preventDefault();
}

function syncFiltersFromRoute() {
  if (type.value === "category" && query.value) {
    selectedCategories.value = [query.value];
  } else {
    selectedCategories.value = [];
  }

  selectedDemographic.value = "All";
}

function mapToUICategory(org) {
  const category = String(org?.category || "").toUpperCase();
  const name = String(org?.name || "")
    .toUpperCase()
    .replace(/[^A-Z0-9 ]/g, "");
  const details = String(org?.data?.[1] || "").toUpperCase();
  const func = String(org?.data?.[7] || "").toUpperCase();

  const text = `${category} ${name} ${details} ${func}`;

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

  if (
    name.includes("MY FRIENDS HOUSE PRESCHOOL") ||
    name.includes("ADVENTURE CLUB") ||
    name.includes("KIDS KORNER") ||
    name.includes("LITTLE OWLS PRESCHOOL") ||
    name.includes("EARLY LEARNING CENTER") ||
    name.includes("CHILD CARE AWARE") ||
    name.includes("OREGON CHILD DEVELOPMENT COALITION") ||
    name.includes("HEAD START") ||
    name.includes("THE KIDS PLACE") ||
    name.includes("WWCC PARENT EDUCATION") ||
    name.includes("PARENT CO OP") ||
    name.includes("PARENT CO-OP") ||
    name.includes("EARLY LEARNING COALITION") ||
    name.includes("CATHOLIC CHARITIES") ||
    name.includes("FRIENDS OF CHILDREN") ||
    name.includes("CAMP FIRE") ||
    name.includes("PARKS AND RECREATION") ||
    name.includes("PARKS & RECREATION") ||
    name.includes("4 H CLUB") ||
    name.includes("CHILDRENS HOME SOCIETY") ||
    name.includes("CHILDREN'S HOME SOCIETY") ||
    name.includes("DIVISION OF CHILDREN AND FAMILY SERVICES") ||
    name.includes("GOOD SAMARITAN MINISTRIES")
  ) {
    return "Family Services";
  }

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

function matchesDemographic(org, demographic) {
  if (!demographic || demographic === "All") return true;

  const blob = [
    org?.name || "",
    ...(Array.isArray(org?.data) ? org.data : [])
  ]
    .join(" ")
    .toLowerCase();

  const demographicPatterns = {
    "Men": [/\bmen\b/, /\bmale\b/, /\bfather\b/, /\bboy\b/],
    "Women": [/\bwomen\b/, /\bfemale\b/, /\bmother\b/, /\bpregnancy\b/, /\bmaternal\b/, /\bgirl\b/, /\bywca\b/],
    "LGBTQ+": [/\blgbt/, /\bgay\b/, /\blesbian\b/, /\bqueer\b/, /\btransgender\b/, /\bpride\b/, /\bsexual orientation\b/],
    "Hispanic/Latino": [/\bhispanic\b/, /\blatino\b/, /\blatina\b/, /\bspanish\b/, /\bbilingual\b/, /\bmexican\b/],
    "Native American": [/\bnative american\b/, /\bindigenous\b/, /\btribal\b/, /\btribe\b/, /\bumatilla\b/, /\bconfederated\b/],
    "Black/African American": [/\bblack\b/, /\bafrican american\b/, /\bminority\b/, /\bequity\b/, /\bdiversity\b/, /\bmulticultural\b/],
    "Asian": [/\basian\b/, /\bpacific islander\b/, /\bchinese\b/, /\bkorean\b/, /\bmultilingual\b/, /\blanguage\b/, /\bimmigrant\b/, /\brefugee\b/]
  };

  const patterns = demographicPatterns[demographic] || [];
  return patterns.some((pattern) => pattern.test(blob));
}

const filterMenuOpen = ref(false);
const sortMenuOpen = ref(false);

const selectedCategories = ref([]);
const selectedDemographic = ref("All");

const categoryOptions = ["All", ...UI_CATEGORIES];

const translateToSpanish = window.translateToSpanish;
const translateToEnglish = window.translateToEnglish;

const route = useRoute();
const router = useRouter();

const type = computed(() => String(route.params.type || ""));
const query = computed(() => decodeURIComponent(String(route.params.query || "")));

const loading = ref(true);
const errorMsg = ref("");
const searchText = ref("");
const sortBy = ref("az");

function applySearch() {
  const q = searchText.value.trim();

  selectedCategories.value = [];
  selectedDemographic.value = "All";

  if (!q) {
    router.push("/results");
    return;
  }

  router.push(`/results/keyword/${encodeURIComponent(q)}`);
}

watch(
  () => [type.value, query.value],
  ([newType, newQuery]) => {
    if (newType === "keyword") {
      searchText.value = newQuery || "";
    } else if (newType === "category") {
      searchText.value = "";
    } else {
      searchText.value = "";
    }
  },
  { immediate: true }
);

function toggleCategory(value) {
  if (value === "All") {
    selectedCategories.value = [];
    return;
  }
  selectedCategories.value = [value];
}

const sortLabel = computed(() => {
  if (sortBy.value === "az") return "A → Z";
  if (sortBy.value === "za") return "Z → A";
  return "A → Z";
});

const activeFilterLabel = computed(() => {
  const parts = [];

  if (selectedCategories.value.length) {
    parts.push(selectedCategories.value[0]);
  }

  if (selectedDemographic.value !== "All") {
    parts.push(selectedDemographic.value);
  }

  return parts.length ? parts.join(" • ") : "All";
});

const headerText = computed(() => {
  const activeCat = selectedCategories.value.length
    ? selectedCategories.value[0]
    : type.value === "category"
      ? query.value
      : null;

  const parts = [];

  if (activeCat) parts.push(activeCat);
  else if (query.value) parts.push(`"${query.value}"`);

  if (selectedDemographic.value !== "All") {
    parts.push(selectedDemographic.value);
  }

  return parts.length ? `Results for ${parts.join(" • ")}` : "Results";
});

function setSort(option) {
  sortBy.value = option;
  sortMenuOpen.value = false;
}

function clearFilters() {
  selectedCategories.value = [];
  selectedDemographic.value = "All";
}

function onDocClick(e) {
  if (!e.target.closest(".sortWrap")) sortMenuOpen.value = false;
  if (!e.target.closest(".filterWrap")) filterMenuOpen.value = false;
}

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
    const res = await fetch("https://service-provider-database-lb3m.onrender.com/api/organizations");
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);

    const data = await res.json();
    allOrgs.value = data;
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.message || "Error fetching results";
    allOrgs.value = [];
  } finally {
    loading.value = false;
  }
}

const filteredResults = computed(() => {
  let list = allOrgs.value;

  if (selectedCategories.value.length) {
    const picked = selectedCategories.value[0];
    list = list.filter((o) => mapToUICategory(o) === picked);
  } else {
    if (type.value === "category") {
      list = list.filter((o) => mapToUICategory(o) === query.value);
    } else if (type.value === "keyword" && query.value) {
      list = list.filter((o) => {
        const blob = [
          o?.name || "",
          ...(Array.isArray(o?.data) ? o.data : [])
        ]
          .join(" ")
          .toLowerCase();

        return blob.includes(query.value.toLowerCase());
      });
    }
  }

  const q = searchText.value.trim().toLowerCase();

  if (q && type.value !== "keyword") {
    list = list.filter((o) => {
      const blob = [
        o?.name || "",
        ...(Array.isArray(o?.data) ? o.data : [])
      ]
        .join(" ")
        .toLowerCase();

      return blob.includes(q);
    });
  }

  if (selectedDemographic.value !== "All") {
    list = list.filter((org) => matchesDemographic(org, selectedDemographic.value));
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

watch(
  () => route.fullPath,
  () => {
    syncFiltersFromRoute();
    getResults();
  },
  { immediate: true }
);

onMounted(() => {
  document.addEventListener("click", onDocClick);
  window.addEventListener("wheel", forwardScroll, { passive: false });
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  window.removeEventListener("wheel", forwardScroll);
});
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="navLeft">
        <button class="iconBtn" type="button" @click="goBack" aria-label="Go back">←</button>
      </div>

      <div class="centerTitle">Search</div>

      <nav class="topNav">
        <router-link to="/" class="navLink">Home</router-link>
        <router-link to="/results" class="navLink">Search</router-link>
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
      <section class="stickyTop">
        <div class="searchPill" role="search" aria-label="Search results">
          <input
            class="searchInput"
            v-model="searchText"
            @keyup.enter="applySearch"
            placeholder="Search by keyword or organization"
          />
          <button
            class="searchIconBtn"
            type="button"
            @click="applySearch"
            aria-label="Search"
          >
            <span class="searchIcon" aria-hidden="true">🔍</span>
          </button>
        </div>

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
              Filters: <span class="chipValue">{{ activeFilterLabel }}</span> ▾
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

              <div class="menuSectionTitle">Demographic</div>

              <button
                v-for="d in DEMOGRAPHIC_OPTIONS"
                :key="`demo-${d}`"
                class="menuItem"
                :class="{ selected: selectedDemographic === d }"
                type="button"
                @click="selectedDemographic = d"
              >
                <span>{{ d }}</span>
                <span class="check" v-if="selectedDemographic === d">✓</span>
              </button>

              <div class="menuFooter">
                <button class="menuAction" type="button" @click="clearFilters">
                  Clear
                </button>

                <button class="menuAction primary" type="button" @click="filterMenuOpen = false">
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="resultsHeader">
          <h2 class="resultsH2">{{ headerText }}</h2>
          <p class="count" v-if="!loading && !errorMsg">{{ filteredResults.length }} found</p>
        </div>
      </section>

      <section class="resultsScroll" ref="resultsScrollRef">
        <p class="state" v-if="loading">Loading…</p>
        <p class="state error" v-else-if="errorMsg">{{ errorMsg }}</p>
        <p class="state" v-else-if="filteredResults.length === 0">
          No results found. Try a different keyword or adjust your filters.
        </p>

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
  --chip: #F5F5F5;
  --ink: #2f3e36;
  --muted: #4b5563;
  --accent: #2563eb;

  height: 100vh;
  background: #fff;
  color: var(--ink);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  overflow: hidden;
}

.topbar {
  background: var(--bar);
  padding: 10px 24px;
  height: 74px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  flex-shrink: 0;
}

.navLeft {
  display: flex;
  align-items: center;
  z-index: 2;
}

.topNav {
  display: flex;
  gap: 18px;
  align-items: center;
  z-index: 2;
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

.centerTitle {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-family: "Cormorant Garamond", serif;
  font-size: 26px;
  font-weight: 700;
  color: #2f3e36;
  white-space: nowrap;
}

.main {
  max-width: 1000px;
  margin: 0 auto;
  padding: 18px 16px 20px;
  height: calc(100vh - 74px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.stickyTop {
  flex-shrink: 0;
  background: #fff;
  padding-bottom: 18px;
}

.searchPill {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--pill);
  border-radius: 999px;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.searchInput {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  color: var(--ink);
  line-height: 1.4;
}

.searchIconBtn {
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.searchIcon {
  opacity: 0.7;
  font-size: 18px;
}

.controlsRow {
  display: flex;
  gap: 12px;
  margin-bottom: 22px;
}

.sortWrap,
.filterWrap {
  position: relative;
  z-index: 20;
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
  z-index: 999;
  max-height: 420px;
  overflow-y: auto;
}

.menuSectionTitle {
  font-weight: 900;
  font-size: 12px;
  color: var(--muted);
  padding: 8px 10px 6px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.menuItem {
  width: 100%;
  border: none;
  background: transparent;
  padding: 10px 12px;
  border-radius: 12px;
  text-align: left;
  font-weight: 800;
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

.check {
  font-weight: 900;
}

.menuFooter {
  display: flex;
  gap: 10px;
  padding-top: 10px;
}

.menuAction {
  flex: 1;
  border: none;
  background: var(--chip);
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

.chipValue {
  font-weight: 900;
}

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

.resultsScroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.state {
  margin-top: 4px;
  color: var(--muted);
  font-weight: 800;
}

.state.error {
  color: #b42318;
}

.list {
  display: grid;
  gap: 12px;
  padding-bottom: 8px;
}

.card {
  background: var(--card);
  border-radius: 18px;
  padding: 18px 16px;
  cursor: pointer;
}

.cardTop {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.cardTitle {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.chev {
  font-size: 22px;
  opacity: 0.65;
}
</style>