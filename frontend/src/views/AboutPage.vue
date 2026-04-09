<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const translateToSpanish = window.translateToSpanish;
const translateToEnglish = window.translateToEnglish;

function goBack() {
  router.back();
}
</script>

<template>
  <div class="page">
    <header class="topbar">
    <div class="left">
        <button class="iconBtn" @click="goBack">←</button>
    </div>

    <div class="centerTitle">
        About Walla Walla Community Resources
    </div>

    <div class="right">
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
    </div>
    </header>

    <main class="main">

      <h2 class="sectionTitle">About This Directory</h2>
      <p class="text">
        Walla Walla Community Resources is a directory designed to help people
        find local support services more easily.
      </p>

      <h2 class="sectionTitle">Our Purpose</h2>
      <p class="text">
        This site brings together organizations and programs in the Walla Walla
        area, including food, housing, health, education, legal, transportation,
        and family services.
      </p>

      <h2 class="sectionTitle">How to Use</h2>
      <p class="text">
        Browse by category, search for services, and click on an organization to
        view more details.
      </p>

      <h2 class="sectionTitle">Important Note</h2>
      <p class="text">
        Information may change, so please contact organizations directly to
        confirm services, hours, and eligibility.
      </p>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #fff;
  color: #2f3e36;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

/* TOP BAR */
.topbar {
  background: #e6e6e6;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  color: #2563eb;
}

/* LANGUAGE DROPDOWN */
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

/* BACK BUTTON */
.iconBtn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 999px;
  background: rgba(255,255,255,0.75);
  cursor: pointer;
  font-size: 20px;
}

/* MAIN CONTENT */
.main {
  max-width: 850px;
  margin: 0 auto;
  padding: 24px;
}

/* TITLE */
.title {
  font-family: "Cormorant Garamond", serif;
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 20px;
}

/* SECTION HEADERS */
.sectionTitle {
  font-family: "Cormorant Garamond", serif;
  font-size: 22px;
  font-weight: 700;
  margin-top: 20px;
}

/* BODY TEXT */
.text {
  margin-top: 6px;
  line-height: 1.7;
  color: #4b5563;
  font-weight: 500;
}

.topbar {
  background: #e6e6e6;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

/* left + right keep layout stable */
.left,
.right {
  display: flex;
  align-items: center;
}

/* CENTER TITLE */
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

/* nav stays same */
.topNav {
  display: flex;
  gap: 18px;
  align-items: center;
}
</style>