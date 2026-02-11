import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import ResourceDesciption from "../views/ResourceDesciption.vue"; // (yes, spelled like your filename)

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },

    // ✅ resource detail page
    { path: "/resource/:id", name: "resource", component: ResourceDesciption },
  ],
});

export default router;
