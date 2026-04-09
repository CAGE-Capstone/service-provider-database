import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultsPage from '../views/ResultsPage.vue'
import ResourceDesciption from '../views/ResourceDesciption.vue'
import AboutPage from '../views/AboutPage.vue'

const routes = [
  {
    path: '/',
    component: HomeView
  },
  {
    path: '/results/:type/:query',
    component: ResultsPage
  },
  {
    path: '/resource/:id',
    component: ResourceDesciption
  },
  {
    path: '/results',
    component: ResultsPage
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router