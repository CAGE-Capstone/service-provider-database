import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import ResourceDesciption from "./views/ResourceDesciption.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/resource/:id", name: "resource", component: ResourceDesciption }, 
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
