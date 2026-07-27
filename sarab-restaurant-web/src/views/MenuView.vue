<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const categories = ref([])
const menuItems = ref([])
const selectedCategory = ref(null)
const isLoading = ref(true)

async function loadCategories() {
  const response = await api.get('/categories/')
  categories.value = response.data
  if (categories.value.length > 0) {
    await selectCategory(categories.value[0].id)
  }
}

async function selectCategory(categoryId) {
  selectedCategory.value = categoryId
  isLoading.value = true
  const response = await api.get('/menu-items/', { params: { category: categoryId } })
  menuItems.value = response.data
  isLoading.value = false
}

onMounted(loadCategories)
</script>

<template>
  <div class="menu-page">
    <h1>🍽️ Sarab Restaurant</h1>

    <div class="categories">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['category-btn', { active: selectedCategory === cat.id }]"
        @click="selectCategory(cat.id)"
      >
        {{ cat.name }}
      </button>
    </div>

    <div v-if="isLoading" class="loading">Yuklanmoqda...</div>

    <div v-else class="items-grid">
      <div v-for="item in menuItems" :key="item.id" class="item-card">
        <img v-if="item.image" :src="item.image" :alt="item.name" class="item-image" />
        <div class="item-info">
          <h3>{{ item.name }}</h3>
          <p class="item-description">{{ item.description }}</p>
          <span class="item-price">{{ item.price }} so'm</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.menu-page { padding: 16px; padding-bottom: 80px; }
h1 { font-size: 20px; margin-bottom: 16px; }
.categories { display: flex; gap: 8px; overflow-x: auto; margin-bottom: 16px; padding-bottom: 8px; }
.category-btn { flex-shrink: 0; padding: 8px 16px; border-radius: 20px; border: 1px solid var(--tg-hint-color); background: transparent; color: var(--tg-text-color); font-size: 14px; }
.category-btn.active { background: var(--tg-button-color); color: var(--tg-button-text-color); border-color: var(--tg-button-color); }
.loading { text-align: center; padding: 40px; color: var(--tg-hint-color); }
.items-grid { display: flex; flex-direction: column; gap: 12px; }
.item-card { display: flex; border: 1px solid #eee; border-radius: 12px; overflow: hidden; }
.item-image { width: 90px; height: 90px; object-fit: cover; flex-shrink: 0; }
.item-info { padding: 10px 12px; flex: 1; }
.item-info h3 { margin: 0 0 4px; font-size: 15px; }
.item-description { font-size: 13px; color: var(--tg-hint-color); margin: 0 0 6px; }
.item-price { font-weight: bold; color: var(--tg-button-color); }
</style>