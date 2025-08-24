import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
// 通用字体
import 'vfonts/Lato.css'
// 等宽字体
import 'vfonts/FiraCode.css'
// 多语言支持
import i18n from './locales'

// 全局禁用右键菜单，但保留输入框等可编辑元素的右键菜单
document.addEventListener('contextmenu', (event) => {
  const target = event.target as HTMLElement;
  
  // 允许在这些元素上显示右键菜单
  const allowedElements = [
    'input',
    'textarea', 
    '[contenteditable="true"]',
    '[contenteditable=""]'
  ];
  
  // 检查是否是允许的元素
  const isAllowedElement = allowedElements.some(selector => {
    if (selector.startsWith('[')) {
      // 属性选择器
      return target.matches(selector);
    } else {
      // 标签选择器
      return target.tagName.toLowerCase() === selector;
    }
  });
  
  // 检查是否在允许的元素内部（例如富文本编辑器内的元素）
  const isInsideAllowedElement = allowedElements.some(selector => {
    return target.closest(selector) !== null;
  });
  
  // 如果不是允许的元素，则禁用右键菜单
  if (!isAllowedElement && !isInsideAllowedElement) {
    event.preventDefault();
  }
}, false);

const app = createApp(App)
app.use(i18n)
app.mount('#app')
