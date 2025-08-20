<template>
  <div 
    class="splitter splitter-vertical"
    :class="{ 'is-active': isActive }" 
    @mousedown="handleMouseDown"
    :title="title"
  >
    <div class="splitter-handle">
      <div class="splitter-dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  isActive?: boolean;
  title?: string;
}

defineProps<Props>();

const emit = defineEmits<{
  'start-resize': [event: MouseEvent];
}>();

const handleMouseDown = (event: MouseEvent) => {
  emit('start-resize', event);
};
</script>

<style scoped>
.splitter {
  position: relative;
  cursor: col-resize;
  background: linear-gradient(180deg, #e2e8f0 0%, #cbd5e0 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  transition: background 0.2s ease;
  user-select: none;
}

.splitter:hover,
.splitter.is-active {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.splitter-vertical {
  width: 6px;
  min-width: 6px;
  max-width: 6px;
}

.splitter-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.splitter-dots {
  display: flex;
  flex-direction: column;
  gap: 3px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.splitter:hover .splitter-dots,
.splitter.is-active .splitter-dots {
  opacity: 1;
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: currentColor;
}

.splitter:hover .dot,
.splitter.is-active .dot {
  background: white;
}
</style>
