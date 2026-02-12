import {ref, onMounted} from 'vue'

export function orgSearch(){

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

    return {
        CATEGORIES, 
        searchQuery, 
        searchKeyword,
        clickCategory
    }
}