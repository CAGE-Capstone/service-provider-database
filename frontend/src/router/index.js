import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultsPage from '../views/ResultsPage.vue'
import ResourceDesciption from '../views/ResourceDesciption.vue'

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
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router