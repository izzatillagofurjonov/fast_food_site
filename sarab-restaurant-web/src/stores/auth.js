import { defineStore } from 'pinia'
import api from '@/services/api'
import { getInitData, isRunningInTelegram } from '@/services/telegram'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  }),

  actions: {
    async initAuth() {
      this.isLoading = true

      if (!isRunningInTelegram()) {
        this.isLoading = false
        this.error = 'Bu ilova faqat Telegram ichida to\'liq ishlaydi.'
        return
      }

      try {
        const initData = getInitData()
        const response = await api.post('/telegram-auth/', { init_data: initData })

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)

        this.user = response.data.user
        this.isAuthenticated = true
      } catch (err) {
        this.error = 'Kirishda xatolik yuz berdi.'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.user = null
      this.isAuthenticated = false
    },
  },
})