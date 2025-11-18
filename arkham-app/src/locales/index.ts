import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'

const messages = {
  zh,
  en
}

// 默认使用中文，语言设置由后端配置管理
const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: 'zh',
  fallbackLocale: 'zh',
  messages,
  globalInjection: true // 全局注入$t
})

export default i18n

// 导出切换语言函数
// 注意：语言设置应通过后端配置保存，此函数仅更新运行时语言
export const setLanguage = (locale: string) => {
  i18n.global.locale.value = locale
}

// 导出当前语言
export const getCurrentLanguage = () => {
  return i18n.global.locale.value
}
