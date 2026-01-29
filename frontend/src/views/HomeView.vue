<script setup>
import homepageIcon from "../assets/icons/main-image-homepage.png";
import housingIcon from "../assets/icons/house-symbol.png";

const categories = [
  { key: "Housing", img: housingIcon },
  { key: "Recovery", icon: "🩹" },
  { key: "Health", icon: "❤️" },
  { key: "Education", icon: "🎓" },
  { key: "Food", icon: "🍽️" },
  { key: "Employment", icon: "🧑‍💼" },
];
</script>

<template>
  <div class="page">
    <header class="header">
    <h1 class="brand">Service Provider Database</h1>
    <img
        class="heroImage"
        :src="homepageIcon"
        alt="Service Provider Database homepage illustration"
    />
    </header>
    
    <main class="content">
      <div class="searchBar">
        <span class="searchText">Search</span>
        <span class="searchIcon">🔍</span>
      </div>

      <h2 class="sectionTitle">Categories</h2>

      <div class="grid">
        <button v-for="c in categories" :key="c.key" class="cat" type="button">
          <div class="iconBox">
            <img v-if="c.img" :src="c.img" :alt="c.key" />
            <span v-else class="emoji" aria-hidden="true">{{ c.icon }}</span>
          </div>
          <div class="label">{{ c.key }}</div>
        </button>
      </div>

      <button class="searchBtn" type="button">Search</button>

      <section class="block">
        <div class="blockSearch">
          <span class="searchText">Search Location</span>
          <span class="searchIcon">🔍</span>
        </div>
        <div class="map">This is a map</div>
      </section>

      <h2 class="sectionTitle">Demographic Information</h2>
      <div class="demo">Input options here</div>
    </main>
  </div>
</template>

<style scoped>
/* Colors in ONE place */
.page {
  --bg-page: #DBE2EF;
  --bg-header: #4fa5d8;
  --bg-surface: #F9F7F7;
  --bg-block: #F9F7F7;
  --bg-map: #F9F7F7;

  --text-primary: #111111;
  --text-secondary: #555555;
  --accent: #2563eb;

  min-height: 100vh;
  width: 100%;
  background: var(--bg-page);
  color: var(--text-primary);

  /* Body font */
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}
/* Playfair Display for titles */
.brand,
.sectionTitle {
  font-family: "Playfair Display", serif;
  letter-spacing: 0.4px;
}

.brand {
  font-weight: 800;
}

.sectionTitle {
  font-weight: 700;
}

/* Full-width header */
.header {
  background: var(--bg-header);
  padding: 32px 0;
  text-align: center;
  width: 100%;
}

.brand {
  font-size: 32px;
  font-weight: 900;
  margin: 0;
}

/* Content container: centered on desktop, full-width on mobile */
.content {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

.searchBar {
  background: var(--bg-surface);
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
  opacity: 0.8;
}

.sectionTitle {
  margin: 18px 0 10px;
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
}

/* Responsive grid: 3 cols on mobile, more on desktop */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 12px;
  align-items: start;
}

@media (min-width: 900px) {
  .grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

.cat {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.iconBox {
  background: var(--bg-surface);
  height: 90px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  overflow: hidden;
  transition: outline 120ms ease;
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
  text-align: center;
  margin-top: 6px;
  font-weight: 600;
  color: var(--text-primary);
}

.searchBtn {
  margin-left: auto;
  display: block;
  padding: 8px 18px;
  border-radius: 999px;
  border: none;
  background: var(--bg-surface);
  font-weight: 700;
  cursor: pointer;
  transition: background 120ms ease, color 120ms ease;
}

/* Optional hover polish (desktop) */
.cat:hover .iconBox {
  outline: 2px solid var(--accent);
}

.searchBtn:hover {
  background: var(--accent);
  color: #fff;
}

.block {
  background: var(--bg-block);
  border-radius: 16px;
  padding: 12px;
  margin-top: 14px;
}

.blockSearch {
  background: var(--bg-page);
  border-radius: 999px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map {
  margin-top: 12px;
  height: 200px;
  background: var(--bg-map);
  border-radius: 14px;
  display: grid;
  place-items: center;
}

.demo {
  background: var(--bg-block);
  border-radius: 16px;
  height: 160px;
  display: grid;
  place-items: center;
}
</style>
