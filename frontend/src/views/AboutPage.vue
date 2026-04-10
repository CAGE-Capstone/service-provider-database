<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const translateToSpanish = window.translateToSpanish;
const translateToEnglish = window.translateToEnglish;
const menuOpen = ref(false);

function goBack() {
  router.back();
}
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="left">
        <button class="iconBtn" @click="goBack" aria-label="Go back">←</button>
      </div>

      <div class="centerTitle">
        About Walla Walla Community Resources
      </div>

            <div class="right">
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
            </div>
    </header>

    <main class="main">
      <section class="infoCard">
        <h2 class="sectionTitle">About This Directory</h2>
        <p class="text">
          Walla Walla Community Resources is an online directory designed to help
          individuals and families find local support services more easily. This
          project was developed in collaboration with Communities In Schools of
          the Blue Mountain Region to improve access to essential resources
          across the Walla Walla community.
        </p>
      </section>

      <section class="infoCard">
        <h2 class="sectionTitle">Our Purpose</h2>
        <p class="text">
          Nearly one in four students in Washington does not graduate on time.
          Many of these challenges are connected to unmet basic needs such as
          food, housing, healthcare, and family support.
        </p>
        <p class="text">
          This directory was created to help connect people to the services they
          need, when they need them. It brings together local organizations,
          nonprofits, and service providers into one searchable place, making
          support easier to discover and access.
        </p>
      </section>

      <section class="infoCard">
        <h2 class="sectionTitle">How to Use</h2>

        <div class="step">
          <div class="stepNumber">1</div>
          <div class="stepContent">
            <h3 class="stepTitle">Search or browse</h3>
            <p class="text">
            Use the search bar to enter a keyword such as “food,” “housing,” or “health,” 
            or type the name of a specific organization. You can also browse by category 
            if you are not sure where to begin.
            </p>
          </div>
        </div>

        <div class="step">
          <div class="stepNumber">2</div>
          <div class="stepContent">
            <h3 class="stepTitle">Open a result</h3>
            <p class="text">
              Click on an organization to view more details, including what
              services they offer and how to contact them.
            </p>
          </div>
        </div>

        <div class="step">
          <div class="stepNumber">3</div>
          <div class="stepContent">
            <h3 class="stepTitle">Refine your results</h3>
            <p class="text">
            Use the sort and filter options to narrow your results by category or 
            demographic group (such as age, gender, or community), helping you find 
            more relevant services.
            </p>
          </div>
        </div>

        <div class="step">
          <div class="stepNumber">4</div>
          <div class="stepContent">
            <h3 class="stepTitle">Confirm details</h3>
            <p class="text">
              Before visiting or relying on a service, contact the organization
              directly to confirm hours, availability, and eligibility
              requirements.
            </p>
          </div>
        </div>
      </section>

      <section class="noteCard">
        <h2 class="sectionTitle">Important Note</h2>
        <p class="text">
          Service information may change over time, so we encourage users to
          contact organizations directly to confirm current details.
        </p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #ffffff;
  color: #2f3e36;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

/* TOP BAR */
.topbar {
  background: #dbe2ef;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.left,
.right {
  display: flex;
  align-items: center;
  z-index: 2;
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

.languageSelect {
  font-family: "Cormorant Garamond", serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #c7d2e3;
  background: white;
  color: #2f3e36;
  cursor: pointer;
}

.iconBtn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  font-size: 20px;
}

.menuBtn {
  display: none;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  font-size: 24px;
  color: #2f3e36;
}

.mobileMenu {
  position: absolute;
  top: calc(100% + 8px);
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

  .centerTitle {
    max-width: 52%;
  }
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

/* MAIN CONTENT */
.main {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 56px;
}

/* CARDS */
.infoCard,
.noteCard {
  background: #f5f5f5;
  border-radius: 20px;
  padding: 28px 30px;
  margin-bottom: 24px;
}

.noteCard {
  background: #f5f5f5;
}

/* HEADINGS */
.sectionTitle {
  font-family: "Cormorant Garamond", serif;
  font-size: 34px;
  font-weight: 700;
  margin: 0 0 14px;
  color: #2f3e36;
}

.stepTitle {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: #2f3e36;
}

/* TEXT */
.text {
  margin: 0;
  line-height: 1.8;
  color: #4b5563;
  font-weight: 500;
  font-size: 17px;
}

.text + .text {
  margin-top: 16px;
}

/* STEPS */
.step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-top: 20px;
}

.step:first-of-type {
  margin-top: 12px;
}

.stepNumber {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: #dbe2ef;
  color: #2f3e36;
  font-weight: 800;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stepContent {
  flex: 1;
}

/* MOBILE */
@media (max-width: 900px) {
  .centerTitle {
    font-size: 18px;
  }

  .topNav {
    gap: 14px;
  }

  .navLink {
    font-size: 17px;
  }
}

@media (max-width: 700px) {
  .main {
    padding: 28px 18px 40px;
  }

  .infoCard,
  .noteCard {
    padding: 22px 20px;
    border-radius: 16px;
  }

  .sectionTitle {
    font-size: 28px;
  }

  .stepTitle {
    font-size: 18px;
  }

  .text {
    font-size: 16px;
  }

  .step {
    gap: 12px;
  }

.centerTitle {
  font-size: 15px;
  max-width: 60%;
  text-align: center;
  line-height: 1.2;
  white-space: normal;
}

  .topNav {
    gap: 10px;
  }

  .navLink {
    font-size: 16px;
  }

  .languageSelect {
    font-size: 14px;
    padding: 6px 10px;
  }
}
</style>