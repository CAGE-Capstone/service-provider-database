<script setup>
import { computed, ref, nextTick, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();

const language = ref("en");

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

const organizations = ref([])

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/organizations");
    const data = await res.json();
    organizations.value = data;
  } catch (err) {
    console.error("Error fetching organizations:", err);
  }
});

const resource = computed(() => {
  const id = route.params.id;

  if (!organizations.value.length) return null;

  const found = organizations.value.find(
    (org) => org.name === id
  );

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
    website: row[6] || "",
    services: row[7]
      ? row[7].split(",").map((s) => s.trim())
      : [],
    hours: []
  };
});


/**
 * TEMP Data
 */
// const MOCK_RESOURCES = [
//   {
//     id: "BMAC Food Bank",
//     name: "BMAC Food Bank",
//     phone: "(509) 529-4980",
//     email: "No email provided",
//     description:
//       "Provides food assistance through community pantries and distribution programs. The lead volunteer is Trevor Sandjathe.",
//     hours: ["Mon–Fri: 9am–4pm", "Sat: 10am–2pm"],
//     services: ["Food pantry", "Meal distribution", "Emergency groceries"],
//     website: "https://www.bmacww.org/programs/food",
//     address: "921 W Cherry Street, Walla Walla, WA 99362",
//     mapQuery: "921 W Cherry Street, Walla Walla, WA 99362",
//   },
// ];

// const resource = computed(() => {
//   const id = route.params.id;
//   return MOCK_RESOURCES.find((r) => r.id === id) || null;
// });

const mapUrl = computed(() => {
  if (!resource.value) return "";
  const q = encodeURIComponent(resource.value.mapQuery || resource.value.address || "");
  return `https://www.google.com/maps?q=${q}&output=embed`;
});

function goBack() {
  router.back();
}
</script>

<template>
  <div class="page">
    <!-- TOP BAR -->
        <header class="topbar">
        <!-- LEFT: Back -->
        <button class="backBtn" type="button" @click="goBack" aria-label="Back">
            ←
        </button>

        <!-- CENTER: Title -->
        <h1 class="title">{{ resource?.name || "Resource" }}</h1>

        <!-- RIGHT: Nav + Language -->
        <nav class="topNav">
            <router-link to="/" class="navLink">Home</router-link>

            <a href="#" class="navLink" @click.prevent="scrollToSearch">Search</a>

            <router-link to="/organizations" class="navLink">Organizations</router-link>
            <router-link to="/about" class="navLink">About</router-link>

            <select v-model="language" class="languageSelect" aria-label="Language">
            <option value="en">English</option>
            <option value="es">Español</option>
            </select>
        </nav>
        </header>


    <main class="content" v-if="resource">
      <!-- CONTACT -->
      <section class="section">
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

      <!-- DESCRIPTION -->
      <section class="section">
        <h2 class="sectionTitle">Description</h2>
        <div class="card">
          <p class="bodyText">{{ resource.description }}</p>
        </div>
      </section>

      <!-- HOURS + SERVICES -->
      <section class="section">
        <div class="twoCol">
          <div>
            <h2 class="sectionTitle">Hours</h2>
            <div class="card">
              <ul class="list">
                <li v-for="(h, i) in resource.hours" :key="i">{{ h }}</li>
              </ul>
            </div>
          </div>

          <div>
            <h2 class="sectionTitle">Services</h2>
            <div class="card">
              <ul class="list">
                <li v-for="(s, i) in resource.services" :key="i">{{ s }}</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- WEBSITE -->
      <section class="section" v-if="resource.website">
        <h2 class="sectionTitle">Website</h2>
        <a class="pill" :href="resource.website" target="_blank" rel="noreferrer">
          <span class="pillValue">{{ resource.website }}</span>
        </a>
      </section>

      <!-- DIRECTIONS + MAP -->
      <section class="section">
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
  --bg-header: #e7e7e7;
  --bg-card: #f4f4f4;

  --text-primary: #111111;
  --text-secondary: #334155;

  min-height: 100vh;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: var(--font-body, system-ui, -apple-system, Segoe UI, Roboto, sans-serif);
}

/* Top bar */
    .topbar {
    background: var(--bg-header);
    padding: 14px 18px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    }

    /* left back button pinned */
    .backBtn {
    position: absolute;
    left: 18px;
    width: 44px;
    height: 44px;
    border-radius: 999px;
    border: none;
    background: var(--bg-card);
    font-size: 20px;
    cursor: pointer;
    }

    /* centered title */
    .title {
    margin: 0;
    font-family: "Cormorant Garamond", serif;
    font-size: 26px;
    font-weight: 700;
    }

    /* right nav pinned */
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
    color: #2563eb;
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


/* Layout */
.content {
  padding: 18px 16px 34px;
  max-width: 900px;
  margin: 0 auto;
}

.section {
  margin-top: 18px;
}

.sectionTitle {
  margin: 0 0 10px;
  font-family: var(--font-title, "Cormorant Garamond", serif);
  font-size: 26px;
  font-weight: 700;
}

.card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 14px;
}

.bodyText {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
  font-family: var(--font-body, system-ui, -apple-system, Segoe UI, Roboto, sans-serif);
}

/* Pills */
.pillList {
  display: grid;
  gap: 10px;
}

.pill {
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 10px 12px;
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

/* Lists */
.list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* Hours/services grid */
.twoCol {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 850px) {
  .twoCol {
    grid-template-columns: 1fr 1fr;
  }
}

/* Map */
.map {
  margin-top: 12px;
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
