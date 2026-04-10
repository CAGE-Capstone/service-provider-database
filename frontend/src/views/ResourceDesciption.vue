<script setup>
import { computed, ref, nextTick, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
const menuOpen = ref(false);

const translateToSpanish = window.translateToSpanish;
const translateToEnglish = window.translateToEnglish;

const scrollToSearch = async () => {
  if (router.currentRoute.value.path !== "/") {
    await router.push("/");
    await nextTick();
  }

  const section = document.getElementById("searchSection");
  if (section) {
    section.scrollIntoView({ behavior: "smooth" });
  }
};

const organizations = ref([]);

onMounted(async () => {
  try {
    const res = await fetch("https://service-provider-database-lb3m.onrender.com/api/organizations");
    const data = await res.json();
    organizations.value = data;
  } catch (err) {
    console.error("Error fetching organizations:", err);
  }
});

const resource = computed(() => {
  const id = route.params.id;

  if (!organizations.value.length) return null;

  const found = organizations.value.find((org) => org.name === id);
  if (!found) return null;

  const row = found.data;

  return {
    id: found.id,
    name: found.name,
    category: found.category,
    description: row[1] || "",
    phone: row[2] || "",
    contact: row[3] || "",
    email: row[4] || "",
    address: row[5] || "",
    website: row[6] || ""
  };
});

const mapUrl = computed(() => {
  if (!resource.value) return "";
  const q = encodeURIComponent(resource.value.address || "");
  return `https://www.google.com/maps?q=${q}&output=embed`;
});

function goBack() {
  router.back();
}
</script>

<template>
  <div class="page">
    <header class="topbar">
      <button class="backBtn" type="button" @click="goBack" aria-label="Back">
        ←
      </button>

      <h1 class="title">{{ resource?.name || "Resource" }}</h1>

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

    <main class="content" v-if="resource">
      <section class="section" v-if="resource.phone || resource.email">
        <h2 class="sectionTitle">Contact</h2>

        <div class="pillList">
          <a class="pill" :href="`tel:${resource.phone}`" v-if="resource.phone">
            <span class="pillLabel">Phone</span>
            <span class="pillValue">{{ resource.phone }}</span>
          </a>

          <a class="pill" :href="`mailto:${resource.email}`" v-if="resource.email">
            <span class="pillLabel">Email</span>
            <span class="pillValue">{{ resource.email }}</span>
          </a>
        </div>
      </section>

      <section class="section" v-if="resource.description">
        <h2 class="sectionTitle">Description</h2>
        <div class="card">
          <p class="bodyText">{{ resource.description }}</p>
        </div>
      </section>

      <section class="section" v-if="resource.website">
        <h2 class="sectionTitle">Website</h2>
        <a class="pill" :href="resource.website" target="_blank" rel="noreferrer">
          <span class="pillValue">{{ resource.website }}</span>
        </a>
      </section>

      <section class="section" v-if="resource.address">
        <h2 class="sectionTitle">Directions</h2>

        <div class="card">
          <p class="bodyText">{{ resource.address }}</p>

          <div class="map">
            <iframe
              :src="mapUrl"
              width="100%"
              height="100%"
              style="border:0;"
              loading="lazy"
              allowfullscreen
              referrerpolicy="no-referrer-when-downgrade"
              title="Map"
            ></iframe>
          </div>
        </div>
      </section>
    </main>

    <main class="content" v-else>
      <div class="card">
        <p class="bodyText">Resource not found.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  --bg-page: #ffffff;
  --bg-header: #DBE2EF;
  --bg-card: #F5F5F5;

  --text-primary: #2f3e36;
  --text-secondary: #4b5563;
  --accent: #2563eb;

  min-height: 100vh;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

.topbar {
  background: var(--bg-header);
  padding: 14px 18px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.backBtn {
  position: absolute;
  left: 18px;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: none;
  background: rgba(255, 255, 255, 0.75);
  font-size: 20px;
  cursor: pointer;
}

.title {
  margin: 0;
  font-family: "Cormorant Garamond", serif;
  font-size: 26px;
  font-weight: 700;
  color: #2f3e36;
}

.topNav {
  position: absolute;
  right: 18px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.navLink {
  text-decoration: none;
  font-family: "Cormorant Garamond", serif;
  font-size: 18px;
  font-weight: 600;
  color: #2f3e36;
}

.navLink:hover {
  color: var(--accent);
}

.languageSelect {
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  font-family: "Cormorant Garamond", serif;
  font-size: 16px;
  color: #2f3e36;
  cursor: pointer;
}

.content {
  padding: 24px 16px 40px;
  max-width: 900px;
  margin: 0 auto;
}

.section {
  margin-top: 24px;
}

.sectionTitle {
  margin: 0 0 12px;
  font-family: "Cormorant Garamond", serif;
  font-size: 26px;
  font-weight: 700;
  color: #2f3e36;
}

.card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 16px;
}

.bodyText {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.pillList {
  display: grid;
  gap: 12px;
}

.pill {
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 12px 14px;
  text-decoration: none;
  color: inherit;
}

.pillLabel {
  font-weight: 700;
  color: var(--text-primary);
}

.pillValue {
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}

.menuBtn {
  display: none;
  position: absolute;
  right: 18px;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.75);
  font-size: 24px;
  cursor: pointer;
  color: #2f3e36;
}

.mobileMenu {
  position: absolute;
  top: calc(100% + 8px);
  right: 18px;
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

  .title {
    max-width: 55%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 22px;
  }
}

.map {
  margin-top: 14px;
  height: 300px;
  border-radius: 14px;
  overflow: hidden;
  background: #e5e5e5;
}

@media (min-width: 850px) {
  .map {
    height: 360px;
  }
}
</style>