<template>

    <div>
        <h1>Results for {{query}}</h1>
        
        <div v-if = 'loading'> Loading... </div>

        <div v-else-if = 'results.length === 0'> No results. Try another search. </div>

        <div v-else class = 'results'>
            <button
                v-for='res in results'
            >
                {{res.name}}
            </button>
        </div>
    </div>

</template>

<script setup>

    import {ref, onMounted, watch} from 'vue'
    import {useRoute} from 'vue-router'

    const route = useRoute()

    const results = ref([])
    const loading = ref(true)
    const query = ref('')

    async function getResults() {
        const type = route.params.type
        const q = route.params.query

        query.value = q

        loading.value = true

        try {
            const res = await fetch('http://127.0.0.1:5000/api/organizations')
            const data = await res.json()

            if (type == 'category') {
                results.value = data.filter(org => 
                    org.category.toUpperCase() === q.toUpperCase()
                )

            } else {
                results.value = data.filter(org =>
                    org.name.toUpperCase().includes(q.toUpperCase())
                )
            }
        } catch (err) {
            console.error('Error fetching results:', err)
            results.value = []
        } finally {
            loading.value = false
        }
    }

    onMounted(getResults)

</script>