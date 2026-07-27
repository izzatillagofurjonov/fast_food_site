export function getTelegramWebApp() {
  return window.Telegram?.WebApp || null
}

export function isRunningInTelegram() {
  const tg = getTelegramWebApp()
  return !!(tg && tg.initData)
}

export function getInitData() {
  const tg = getTelegramWebApp()
  return tg?.initData || null
}

export function initTelegramUI() {
  const tg = getTelegramWebApp()
  if (!tg) return

  tg.ready()
  tg.expand()

  const root = document.documentElement
  root.style.setProperty('--tg-bg-color', tg.themeParams.bg_color || '#ffffff')
  root.style.setProperty('--tg-text-color', tg.themeParams.text_color || '#000000')
  root.style.setProperty('--tg-button-color', tg.themeParams.button_color || '#e63946')
  root.style.setProperty('--tg-button-text-color', tg.themeParams.button_text_color || '#ffffff')
  root.style.setProperty('--tg-hint-color', tg.themeParams.hint_color || '#999999')
}