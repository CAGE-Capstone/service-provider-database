<template>

    <!-- search bar -->
    <div class = 'search-bar'>
        <input
            v-model="searchQuery"
            @keyup.enter="searchKeyword(searchQuery)"
            placeholder="Search by keyword"
        />
        <button @click="searchKeyword(searchQuery)">
            Search
        </button>
    </div>

    <!-- category buttons -->
    <div class = 'cat-buttons'>
        <p>Filter by category</p>
        <router-link
            v-for = 'cat in CATEGORIES'
            :key = 'cat'
            @click = "clickCategory(cat)"
        >
            <button>{{cat}}</button>
        </router-link>
    </div>

</template>

<script setup>

    import {ref, onMounted} from 'vue'
    import {useRouter} from 'vue-router'

    const CATEGORIES = ref([])

    const searchQuery = ref('')

    const router = useRouter()

    function searchKeyword(query) {
        if (!query) {
            return
        }

        router.push(`results/keyword/${encodeURIComponent(query)}`)
    }

    function clickCategory(cat) {
        console.log("Category clicked for:", cat)
    }

    onMounted(async () => {
        try {
            const res = await fetch('http://127.0.0.1:5000/api/categories')
            CATEGORIES.value = await res.json()
        } catch (err) {
            console.error('Failed to fetch categories:', err)
        }
    })

</script>