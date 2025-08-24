import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'

const messages = {
  zh,
  en
}

// 从localStorage获取语言设置，默认中文
const savedLanguage = localStorage.getItem('language') || 'zh'

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: savedLanguage,
  fallbackLocale: 'zh',
  messages,
  globalInjection: true // 全局注入$t
})

export default i18n

// 导出切换语言函数
export const setLanguage = (locale: string) => {
  i18n.global.locale.value = locale
  localStorage.setItem('language', locale)
}

// 导出当前语言
export const getCurrentLanguage = () => {
  return i18n.global.locale.value
}
