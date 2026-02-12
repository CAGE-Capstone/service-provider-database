<template>

    <!-- DUMMY PAGE - hi Ella, do not worry about this page, just used it to get the search functionality down ~Gabby -->

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
        <button
            v-for = 'cat in CATEGORIES'
            :key = 'cat'
            @click = "clickCategory(cat)"
        >
            {{cat}}
    </button>
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

        router.push(`/results/keyword/${encodeURIComponent(query)}`)
    }

    function clickCategory(cat) {
        router.push(`/results/category/${encodeURIComponent(cat)}`)
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