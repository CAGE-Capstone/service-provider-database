import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultsPage from '../views/ResultsPage.vue'

const routes = [
    {
        path: '/',
        component: HomeView
    },
    {
        path: '/results/:type/:query',
        component: ResultsPage
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router