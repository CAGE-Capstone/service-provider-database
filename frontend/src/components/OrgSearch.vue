<template>

    <!-- search bar -->
    <div>
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
    <div>
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

    const CATEGORIES = ref([])

    const searchQuery = ref('')

    function searchKeyword(q) {
        console.log("Search requested for:", q)
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