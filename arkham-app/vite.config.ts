import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
// 引入 unplugin-vue-components/vite
import Components from 'unplugin-vue-components/vite'
// 引入 NaiveUiResolver
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 按需引入配置
    Components({
      resolvers: [
        NaiveUiResolver()
      ]
    })
  ],
  // 添加路径别名配置
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        // target: 'https://bgjc.cnova-auto.com',
        changeOrigin: true
      }
    }
  }
})
