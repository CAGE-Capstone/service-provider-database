<script setup>
import { useRouter } from "vue-router";
import homepageIcon from "../assets/icons/main-image-homepage.png";
import { ref } from "vue";

const router = useRouter();

const language = ref("en");
const menuOpen = ref(false);

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

const categories = ref(UI_CATEGORIES);
const searchQuery = ref("");

const translateToSpanish = window.translateToSpanish;
const translateToEnglish = window.translateToEnglish;

const scrollToSearch = () => {
  const section = document.getElementById("searchSection");
  if (section) {
    section.scrollIntoView({ behavior: "smooth" });
  }
};

function formatCategory(name) {
  if (!name) return "";
  return name
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function categoryIcon(name) {
  const n = (name || "").toLowerCase();

  if (n.includes("food")) return "🍽️";
  if (n.includes("housing")) return "🏠";
  if (n.includes("health")) return "🩺";
  if (n.includes("education") || n.includes("work")) return "🎓";
  if (n.includes("legal") || n.includes("financial")) return "⚖️";
  if (n.includes("transport")) return "🚌";
  if (n.includes("community")) return "🤝";
  if (n.includes("other")) return "⭐️";

  return "⭐️";
}

function handleKeywordSearch(query) {
  if (!query) return;
  router.push(`/results/keyword/${encodeURIComponent(query)}`);
}

function handleCategoryClick(cat) {
  router.push(`/results/category/${encodeURIComponent(cat)}`);
}

// function handleCategoryClick(key) {
//   if (key === "Food") {
//     router.push("/resource/bmac-food-bank"); 
//   } else {
//     // alert(`${key} page coming soon`);
//   }
// }
</script>

<template>
  <!-- HOME PAGE -->
  <div class="page">

  <!-- TOP BAR -->
    <header class="topbar">
      <div class="navLeft"></div>

      <button
        class="menuBtn"
        type="button"
        @click="menuOpen = !menuOpen"
        aria-label="Open menu"
        :aria-expanded="menuOpen"
      >
        ☰
      </button>

      <nav class="topNav desktopNav">
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

      <div v-if="menuOpen" class="mobileMenu">
        <router-link to="/" class="mobileNavLink" @click="menuOpen = false">Home</router-link>
        <router-link to="/results" class="mobileNavLink" @click="menuOpen = false">Search</router-link>
        <router-link to="/about" class="mobileNavLink" @click="menuOpen = false">About</router-link>

        <select
          class="languageSelect mobileLanguageSelect"
          @change="$event.target.value === 'es' ? translateToSpanish() : translateToEnglish()"
        >
          <option value="en">English</option>
          <option value="es">Español</option>
        </select>
      </div>
    </header>

      <header class="hero">

        <!-- Language Dropdown -->
        <div class="container heroInner">
          <div class="heroText">

          <!-- <p class="eyebrow">Walla Walla Community Resources</p> -->
          <h1 class="brand">Walla Walla Community Resources</h1>
          <p class="subhead">
            Find services faster — browse categories, filter results, and view key contact details.
          </p>

        </div>

        <div class="heroMedia">
          <img
            class="heroImage"
            :src="homepageIcon"
            alt="Service Provider Database homepage illustration"
          />
        </div>
      </div>
    </header>

    <main class="main">
      <!-- SEARCH (as a section) -->
      <section class="section" id="searchSection">
        <div class="container">
          <div class="sectionHeader">
            <h2 class="sectionTitle">Search</h2>
            <p class="sectionDesc">Search by keyword, category, or location.</p>
          </div>

          <div class="searchRow">
            <div class="searchPill" role="search" aria-label="Search providers">
              <input
                class="searchInput"
                v-model="searchQuery"
                @keyup.enter="handleKeywordSearch(searchQuery)"
                placeholder="Search"
              />
              <span class="searchIcon" aria-hidden="true">🔍</span>
            </div>

            <button class="primaryBtn" type="button" @click="handleKeywordSearch(searchQuery)">
              Search
            </button>
          </div>
        </div>
      </section>

      <!-- CATEGORIES -->
      <section class="section" id="categories">
        <div class="container">
          <div class="sectionHeader">
            <h2 class="sectionTitle">Categories</h2>
            <p class="sectionDesc">Choose a category to explore services.</p>
          </div>

          <!-- <div class="grid">
            <button
              v-for="c in categories"
              :key="c.key"
              class="catCard"
              type="button"
              @click="handleCategoryClick(c.key)"
            >
              <div class="iconBox">
                <img v-if="c.img" :src="c.img" :alt="c.key" />
                <span v-else class="emoji" aria-hidden="true">{{ c.icon }}</span>
              </div>
              <div class="label">{{ c.key }}</div>
            </button>
          </div> -->
            <div class="grid">
              <button
                v-for="c in categories"
                :key="c"
                class="catCard"
                type="button"
                @click="handleCategoryClick(c)"
              >
                <div class="iconBox">
                  <span class="emoji" aria-hidden="true">{{ categoryIcon(c) }}</span>
                </div>
                <div class="label">{{ formatCategory(c) }}</div>
              </button>
            </div>
        </div>
      </section>

      <!-- FOOTER -->
      <footer class="footer">
        <div class="container footerInner">
          <p class="footerText">OWWL • Service Provider Database</p>
        </div>
      </footer>
    </main>
  </div>
</template>
  
<style scoped>
.hero {
  position: relative;
}

.topbar {
  background: var(--bg-hero);
  padding: 8px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  margin: 0;
  font-family: "Cormorant Garamond", serif;
  font-size: 22px;
  font-weight: 700;
  color: #2f3e36;
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

/* ===== Theme ===== */
.page {
  --bg-page: #ffffff;
  --bg-hero: #DBE2EF;
  --bg-surface: #ffffff;
  --bg-card: #F9F7F7;

  --text-primary: #111111;
  --text-secondary: #4b5563;

  --accent: #2563eb;
  --accent-2: #0f3fbf;

  min-height: 100vh;
  width: 100%;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

/* Headings font */
.brand {
  font-family: "Cormorant Garamond", serif;
  font-size: clamp(48px, 8vw, 80px);
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: 0.5px;
  color: #2f3e36;
}


/* ===== Layout helpers ===== */
.container {
  max-width: 1280px;     
  margin: 0 auto;
  padding: 0 56px;     
}

/* ===== Hero ===== */
.hero {
  background: var(--bg-hero);
  padding: 4px 0 8px; 
}

.heroInner {
  display: grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: 28px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 4px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

.brand {
  margin: 0;
  font-size: 40px;
  line-height: 1.05;
  font-weight: 800;
}

.subhead {
  margin: 14px 0 0;
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.6;
  max-width: 46ch;
}

.heroActions {
  margin-top: 18px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.heroImage {
  width: 100%;
  height: auto;
  max-height: 180px;
  object-fit: contain;
  border-radius: 18px;
  display: block;
}

@media (min-width: 900px) {
  .heroImage {
    max-width: 1000px;
  }
}

/* Mobile hero stacks */
@media (max-width: 850px) {
  .heroInner {
    grid-template-columns: 1fr;
  }
  .brand {
    font-size: 34px;
  }
}

/* ===== Buttons ===== */
.primaryBtn {
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 800;
  cursor: pointer;
  transition: transform 120ms ease, background 120ms ease;
}

.primaryBtn:hover {
  background: var(--accent-2);
  transform: translateY(-1px);
}

.ghostBtn {
  background: transparent;
  color: var(--accent);
  border: 2px solid var(--accent);
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 800;
  cursor: pointer;
}

.ghostBtn:hover {
  background: var(--accent);
  color: #ffffff;
  transform: translateY(-1px);
}

/* ===== Sections ===== */
.main {
  padding-bottom: 40px;
}

.section {
  padding: 20px 0;
}

.sectionHeader {
  margin-bottom: 16px;
}

.sectionTitle {
  margin: 0;
  font-family: "Cormorant Garamond", serif;
  font-size: 28px;
  font-weight: 700;
  color: #2f3e36;       
}

.sectionDesc {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

#searchSection.section {
  padding-top: 28px;   /* pulls Search higher */
}

/* ===== Search row ===== */
.searchRow {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.searchBar {
  flex: 1;
  min-width: 240px;
  background: var(--bg-card);
  border-radius: 999px;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.searchText {
  color: var(--text-secondary);
}

.searchIcon {
  opacity: 0.75;
}

/* ===== Category grid ===== */
.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 24px;
  justify-content: center;
}

/* TABLET */
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
}

/* MOBILE */
@media (max-width: 600px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }
}

.catCard {
  width: 100%;
  max-width: 220px;
  margin: 0 auto;
}

/* MOBILE */
@media (max-width: 600px) {
  .catCard {
    max-width: 100%;
  }
}

@media (max-width: 600px) {
  .iconBox {
    height: 72px;
  }

  .emoji {
    font-size: 24px;
  }

  .label {
    font-size: 14px;
  }
}

.catCard {
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  text-align: center;
}

.iconBox {
  background: var(--bg-card);
  height: 92px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  overflow: hidden;
  transition: outline 120ms ease, transform 120ms ease;
}

.catCard:hover .iconBox {
  outline: 2px solid var(--accent);
  transform: translateY(-2px);
}

.iconBox img {
  width: 52px;
  height: 52px;
  object-fit: contain;
  display: block;
}

.emoji {
  font-size: 30px;
  line-height: 1;
}

.label {
  margin-top: 10px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: #2f3e36;
  text-align: center;
}

/* ===== Cards / two column section ===== */
.twoCol {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
}

@media (max-width: 850px) {
  .twoCol {
    grid-template-columns: 1fr;
  }
}

.card {
  background: var(--bg-card);
  border-radius: 18px;
  padding: 16px;
}

.cardTitle {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
}

.bullets {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* Make input blend in */
.locationInput {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  padding: 12px 14px;
  font-family: inherit;
}

/* Ensure button stays blue */
.blockSearch .primaryBtn {
  background: var(--accent);
  color: white;
}

/* Optional sizing tweak */
.locationBtn {
  padding: 12px 22px;
  font-size: 16px;
  border-radius: 999px;
}


/* Demo block */
.demo {
  min-height: 160px;
  display: grid;
  place-items: center;
  color: var(--text-secondary);
}

/* Footer */
.footer {
  padding: 24px 0;
}

.footerInner {
  border-top: 1px solid #e5e7eb;
  padding-top: 18px;
}

.footerText {
  margin: 0;
  color: var(--text-secondary);
}

.footerText {
  margin: 0;
  color: var(--text-secondary);
}

.menuBtn {
  display: none;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  font-size: 24px;
  cursor: pointer;
  color: #2f3e36;
}

.mobileMenu {
  position: absolute;
  top: 100%;
  right: 24px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 200px;
  z-index: 999;
}

.mobileNavLink {
  text-decoration: none;
  font-family: "Cormorant Garamond", serif;
  font-size: 18px;
  font-weight: 600;
  color: #2f3e36;
  padding: 6px 4px;
}

.mobileLanguageSelect {
  margin-top: 4px;
}

@media (max-width: 768px) {
  .desktopNav {
    display: none;
  }

  .menuBtn {
    display: block;
  }

  .topbar {
    position: relative;
  }
}

.searchPill {
  flex: 1;
  min-width: 260px;
  background: var(--bg-card);
  border-radius: 999px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.searchInput {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  color: var(--text-primary);
}

.searchIcon {
  margin-left: 10px;
  opacity: 0.7;
}

/* ===== LOCATION BUTTON FIX ===== */
.locationBtn {
  padding: 12px 22px;
  border-radius: 999px;
}

.blockSearch {
  background: #fff;
  border-radius: 999px;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.locationInput {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  padding: 12px 14px;
}

</style>
