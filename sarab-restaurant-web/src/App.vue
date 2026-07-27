<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { initTelegramUI } from '@/services/telegram'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  initTelegramUI()
  await authStore.initAuth()
})
</script>

<template>
  <div class="app-container">
    <div v-if="authStore.isLoading" class="loading-screen">
      <div class="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>

    <div v-else-if="authStore.error" class="error-screen">
      <p>{{ authStore.error }}</p>
    </div>

    <RouterView v-else />
  </div>
</template>

<style>
:root {
  --tg-bg-color: #ffffff;
  --tg-text-color: #000000;
  --tg-button-color: #e63946;
  --tg-button-text-color: #ffffff;
  --tg-hint-color: #999999;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--tg-bg-color);
  color: var(--tg-text-color);
}
.loading-screen, .error-screen {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100vh; gap: 16px;
}
.spinner {
  width: 40px; height: 40px; border: 4px solid #eee;
  border-top-color: var(--tg-button-color); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>