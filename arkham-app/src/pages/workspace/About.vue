<template>
  <div class="about-container">
    <div class="about-content">
      <div class="about-header">
        <div class="app-logo">🎲</div>
        <h1 class="app-title">{{ $t('about.header.title') }}</h1>
        <p class="app-subtitle">{{ $t('about.header.subtitle') }}</p>
      </div>

      <div class="about-sections">
        <!-- 项目简介 -->
        <div class="section">
          <h2>{{ $t('about.sections.about.title') }}</h2>
          <p class="section-text">{{ $t('about.sections.about.description') }}</p>
        </div>

        <!-- 作者信息 -->
        <div class="section">
          <h2>{{ $t('about.sections.author.title') }}</h2>
          <div class="author-card">
            <div class="author-avatar">👤</div>
            <div class="author-info">
              <h3>{{ $t('about.sections.author.name') }}</h3>
              <p>{{ $t('about.sections.author.role') }}</p>
              <div class="contact-info">
                <div class="contact-item">
                  <span class="contact-label">{{ $t('about.sections.author.email') }}</span>
                  <span class="contact-value copyable" @click="copyToClipboard('xziying@vip.qq.com')">
                    xziying@vip.qq.com
                    <span class="copy-hint">{{ $t('about.sections.author.copyHint') }}</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 开源信息 -->
        <div class="section">
          <h2>{{ $t('about.sections.opensource.title') }}</h2>
          <div class="github-card">
            <div class="github-icon">⭐</div>
            <div class="github-info">
              <h3>{{ $t('about.sections.opensource.name') }}</h3>
              <p>{{ $t('about.sections.opensource.description') }}</p>
              <div class="github-link" @click="copyToClipboard('https://github.com/xziying44/arkham-homebrew')">
                <span class="link-text">https://github.com/xziying44/arkham-homebrew</span>
                <button class="copy-btn">{{ $t('about.sections.opensource.copyLink') }}</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 功能特色 -->
        <div class="section">
          <h2>{{ $t('about.sections.features.title') }}</h2>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">🎨</div>
              <h4>{{ $t('about.sections.features.items.visual.title') }}</h4>
              <p>{{ $t('about.sections.features.items.visual.description') }}</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📦</div>
              <h4>{{ $t('about.sections.features.items.tts.title') }}</h4>
              <p>{{ $t('about.sections.features.items.tts.description') }}</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔄</div>
              <h4>{{ $t('about.sections.features.items.batch.title') }}</h4>
              <p>{{ $t('about.sections.features.items.batch.description') }}</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💾</div>
              <h4>{{ $t('about.sections.features.items.storage.title') }}</h4>
              <p>{{ $t('about.sections.features.items.storage.description') }}</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <h4>{{ $t('about.sections.features.items.arkham.title') }}</h4>
              <p>{{ $t('about.sections.features.items.arkham.description') }}</p>
            </div>
          </div>
        </div>

        <!-- 版本信息 -->
        <div class="section">
          <h2>{{ $t('about.sections.version.title') }}</h2>
          <div class="version-info">
            <div class="version-item">
              <span class="version-label">{{ $t('about.sections.version.current') }}</span>
              <span class="version-value">v3.1</span>
            </div>
            <div class="version-item">
              <span class="version-label">{{ $t('about.sections.version.buildTime') }}</span>
              <span class="version-value">2025/10/30</span>
            </div>
            <div class="version-item">
              <span class="version-label">{{ $t('about.sections.version.tech') }}</span>
              <span class="version-value">Vue 3 + python + naive-ui</span>
            </div>
          </div>
        </div>

        <!-- 致谢 -->
        <div class="section">
          <h2>{{ $t('about.sections.thanks.title') }}</h2>
          <div class="section-text" v-html="$t('about.sections.thanks.description')"></div>
        </div>

        <!-- 底部支撑盒子 - 防止内容被裁切 -->
        <div class="spacer-section">
          <div class="spacer-content">
            <div class="heart-icon">💖</div>
            <p>{{ $t('about.sections.footer.thanks') }}</p>
          </div>
        </div>
      </div>

      <!-- 复制成功提示 -->
      <div v-if="showCopySuccess" class="copy-success">
        {{ $t('about.messages.copySuccess') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const showCopySuccess = ref(false);

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('复制失败:', err);
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);

    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  }
};
</script>

<style scoped>
.about-container {
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.about-content {
  max-width: 800px;
  margin: 0 auto;
}

.about-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.app-logo {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.app-title {
  color: #2c3e50;
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.app-subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.about-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 3rem;
  /* 增加底部内边距 */
}

.section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.section:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.section h2 {
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-text {
  color: #5a6c7d;
  line-height: 1.6;
  margin: 0;
}

.author-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.author-avatar {
  font-size: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-info h3 {
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
  font-size: 1.2rem;
}

.author-info>p {
  color: #7f8c8d;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.contact-label {
  font-weight: 500;
  color: #5a6c7d;
  font-size: 0.9rem;
}

.contact-value {
  position: relative;
}

.copyable {
  background: #e3f2fd;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: monospace;
  font-size: 0.9rem;
}

.copyable:hover {
  background: #bbdefb;
}

.copy-hint {
  position: absolute;
  bottom: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
  white-space: nowrap;
}

.copyable:hover .copy-hint {
  opacity: 1;
}

.github-card {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.github-icon {
  font-size: 2.5rem;
  color: #f39c12;
}

.github-info h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.github-info>p {
  color: #7f8c8d;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.github-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #e8f5e8;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.github-link:hover {
  background: #d4edda;
}

.link-text {
  flex: 1;
  font-family: monospace;
  color: #2c3e50;
  font-size: 0.9rem;
  word-break: break-all;
}

.copy-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;
  white-space: nowrap;
}

.copy-btn:hover {
  background: #218838;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.feature-item {
  text-align: center;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.feature-item h4 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.feature-item p {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.4;
}

.version-info {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.version-item:last-child {
  border-bottom: none;
}

.version-label {
  font-weight: 500;
  color: #5a6c7d;
}

.version-value {
  font-family: monospace;
  color: #2c3e50;
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* 底部支撑盒子样式 */
.spacer-section {
  background: linear-gradient(135deg, #fef3e7 0%, #f3e8ff 100%);
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  border: 2px dashed rgba(147, 51, 234, 0.2);
  margin-bottom: 2rem;
  /* 确保底部有足够空间 */
}

.spacer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.heart-icon {
  font-size: 2rem;
  animation: heartbeat 2s ease-in-out infinite;
}

.spacer-content p {
  color: #7c3aed;
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
}

@keyframes heartbeat {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

.copy-success {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: #28a745;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .about-container {
    padding: 1rem;
  }

  .author-card {
    flex-direction: column;
    text-align: center;
  }

  .github-link {
    flex-direction: column;
    gap: 0.5rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .version-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
