<template>

<!-- search bar -->
<div>
      <input
        v-model="searchQuery"
        @keyup.enter="searchKeyword(searchQuery)"
        placeholder="Search by keyword"
      />
      <button @click="searchKeyword(searchQuery)"">
        Search
      </button>
</div>

</template>