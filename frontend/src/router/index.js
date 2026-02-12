import {createRouter, createWebHistory} from 'vue-router'
import OrgSearch from '../views/OrgSearch.vue'
import ResultsPage from '../views/ResultsPage.vue'

const routes = [
    {
        path: '/',
        component: OrgSearch
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