<template>
    <div 
        class="rune-dial-wrapper" 
        :class="[themeClass, { active: isOpen }]"
        ref="wrapperRef"
    >
        <!-- 1. 背景盘 (Backplate) -->
        <div class="dial-backplate"></div>

        <!-- 2. 符文环 (Ring) -->
        <div class="rune-ring">
            <div 
                v-for="(btn, index) in dialConfig.buttons" 
                :key="index"
                class="rune-item"
                :class="{ 'rune-edit': btn.type === 'edit' }"
                :style="getButtonStyle(index, dialConfig.buttons.length)"
                @click.stop="handleButtonClick(btn)"
            >
                {{ btn.txt }}
            </div>
        </div>

        <!-- 3. 核心 (Core) -->
        <div 
            class="dial-core" 
            :class="{ 'input-mode': isInputMode }"
            @click.stop="toggle"
        >
            <span class="current-value">{{ displayValue }}</span>
            <!-- 移除内部标签显示，避免重复 -->
            <!-- <span class="label-text">{{ label }}</span> -->
            <input 
                v-if="hasInputMode"
                ref="inputRef"
                v-model="inputValue"
                type="number" 
                class="core-input"
                @keydown.enter="confirmInput"
                @blur="handleInputBlur"
                @click.stop
            >
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';

interface Props {
    value: number;
    label?: string; // 虽然不显示，但保留prop接口
    theme: 'health' | 'sanity' | 'level' | 'cost';
}

const props = withDefaults(defineProps<Props>(), {
    value: 0,
    theme: 'health'
});

const emit = defineEmits<{
    (e: 'update:value', value: number): void;
}>();

// 状态
const isOpen = ref(false);
const isInputMode = ref(false);
const inputValue = ref<string | number>('');
const wrapperRef = ref<HTMLElement | null>(null);
const inputRef = ref<HTMLInputElement | null>(null);

// 全局状态管理
const DIAL_OPEN_EVENT = 'rune-dial-open';

const themeClass = computed(() => `theme-${props.theme}`);

const hasInputMode = computed(() => {
    // Level 类型没有自定义输入模式 (no custom range)
    return props.theme !== 'level';
});

// 配置定义
interface DialButton {
    val: number | string;
    txt: string;
    type?: 'normal' | 'edit' | 'special';
}

const dialConfig = computed(() => {
    const config: { buttons: DialButton[] } = { buttons: [] };

    switch (props.theme) {
        case 'health':
        case 'sanity':
            // 生命/理智: 1-9, ∞(-2), None(-1), Edit
            config.buttons = [
                { val: 1, txt: '1' }, { val: 2, txt: '2' }, { val: 3, txt: '3' },
                { val: 4, txt: '4' }, { val: 5, txt: '5' }, { val: 6, txt: '6' },
                { val: 7, txt: '7' }, { val: 8, txt: '8' }, { val: 9, txt: '9' },
                { val: -1, txt: '➖', type: 'special' }, // 无 (-1)
                { val: -2, txt: '♾️', type: 'special' }, // 无限 (-2)
                { val: 'edit', txt: '✎', type: 'edit' }
            ];
            break;

        case 'cost':
            // 费用: 0-9, X(-2), None(-1), Edit
            config.buttons = [
                { val: 1, txt: '1' }, { val: 2, txt: '2' }, { val: 3, txt: '3' },
                { val: 4, txt: '4' }, { val: 5, txt: '5' }, { val: 6, txt: '6' },
                { val: 7, txt: '7' }, { val: 8, txt: '8' }, { val: 9, txt: '9' },
                { val: 0, txt: '0' },
                { val: -1, txt: '➖', type: 'special' }, // 无 (-1)
                { val: -2, txt: 'X', type: 'special' }, // X (-2)
                { val: 'edit', txt: '✎', type: 'edit' }
            ];
            break;

        case 'level':
            // 等级: 0-5, None(-1), Custom(-2), No Edit Button
            config.buttons = [
                { val: 1, txt: '1' }, { val: 2, txt: '2' }, { val: 3, txt: '3' },
                { val: 4, txt: '4' }, { val: 5, txt: '5' },
                { val: 0, txt: '0' },
                { val: -1, txt: '➖', type: 'special' }, // 无 (-1)
                { val: -2, txt: '🧩', type: 'special' }  // 定制 (-2)
            ];
            break;
    }
    return config;
});

const displayValue = computed(() => {
    if (props.value === -1) {
        return '➖';
    }
    if (props.value === -2) {
        if (props.theme === 'cost') return 'X';
        if (props.theme === 'level') return '🧩';
        return '♾️';
    }
    return props.value;
});

const getButtonStyle = (index: number, total: number) => {
    const radius = 75; // 调整半径适配新的大小
    // 将按钮均匀分布在圆周上，从 -90度 (12点钟) 开始
    // 或者根据习惯调整起始角度。为了美观，通常将 0/1 放在上方或右上方
    
    // 这里使用简单的平均分布
    const startAngle = -60; // 起始角度
    const step = 360 / total;
    
    const angle = (index * step) + startAngle;
    const rad = angle * (Math.PI / 180);
    const x = Math.cos(rad) * radius;
    const y = Math.sin(rad) * radius;
    
    return {
        left: `calc(50% + ${x}px - 18px)`, // 18px 是按钮半径的一半略少
        top: `calc(50% + ${y}px - 18px)`
    };
};

const toggle = () => {
    if (isInputMode.value) {
        inputRef.value?.focus();
        return;
    }

    if (isOpen.value) {
        close();
    } else {
        open();
    }
};

const open = () => {
    window.dispatchEvent(new CustomEvent(DIAL_OPEN_EVENT, { 
        detail: { target: wrapperRef.value } 
    }));
    isOpen.value = true;
};

const close = () => {
    if (isInputMode.value) {
        confirmInput();
    }
    isOpen.value = false;
    isInputMode.value = false;
};

const handleGlobalClick = (e: MouseEvent) => {
    if (isOpen.value && wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
        close();
    }
};

const handleDialOpen = (e: Event) => {
    const customEvent = e as CustomEvent;
    if (customEvent.detail.target !== wrapperRef.value) {
        close();
    }
};

const handleButtonClick = (btn: DialButton) => {
    if (btn.type === 'edit') {
        enterInputMode();
    } else {
        updateValue(Number(btn.val));
        close();
    }
};

const enterInputMode = () => {
    if (!hasInputMode.value) return;
    isInputMode.value = true;
    inputValue.value = ''; 
    nextTick(() => {
        inputRef.value?.focus();
    });
};

const confirmInput = () => {
    const raw = parseInt(String(inputValue.value));
    if (!isNaN(raw)) {
        let val = raw;
        // 范围限制
        let min = 0;
        if (props.theme === 'health' || props.theme === 'sanity') min = 1; // 生命理智通常非负且非0? 或许0也可以，但快捷键从1开始。保持跟旧组件逻辑一致，通常是正整数。
        // 按照用户反馈 "Custom range 1-99" for HP/SAN
        if (props.theme === 'cost') min = 0; // Cost 0-99
        
        if (val < min) val = min;
        if (val > 99) val = 99;
        
        updateValue(val);
    }
    isInputMode.value = false;
};

const handleInputBlur = () => {
    // 失去焦点时不自动关闭，等待点击其他地方关闭，以避免冲突
};

const updateValue = (newVal: number) => {
    emit('update:value', newVal);
};

onMounted(() => {
    document.addEventListener('click', handleGlobalClick);
    window.addEventListener(DIAL_OPEN_EVENT, handleDialOpen);
});

onUnmounted(() => {
    document.removeEventListener('click', handleGlobalClick);
    window.removeEventListener(DIAL_OPEN_EVENT, handleDialOpen);
});

</script>

<style scoped>
/* --- 主题定义 --- */
.theme-health { --theme-color: #d12a2a; --theme-sub-color: #ffcccc; --theme-bg: #fff0f0; }
.theme-sanity { --theme-color: #2b5f8f; --theme-sub-color: #cceeff; --theme-bg: #f0f8ff; }
.theme-level  { --theme-color: #d4af37; --theme-sub-color: #faeeb7; --theme-bg: #fffdf0; }
.theme-cost   { --theme-color: #4e7a27; --theme-sub-color: #d4eeb7; --theme-bg: #f2fff0; }

.rune-dial-wrapper {
    position: relative;
    width: 60px;
    height: 60px;
    z-index: 1;
    margin: 0 auto; /* 居中 */
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    user-select: none;
}

/* 激活时层级最高 */
.rune-dial-wrapper.active {
    z-index: 100;
}

/* 1. 背景盘 */
.dial-backplate {
    position: absolute;
    top: 50%; left: 50%;
    width: 58px; height: 58px;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: transparent;
    pointer-events: none;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    z-index: -1;
    border: 1px solid transparent;
}

/* 展开后的背景盘 */
.rune-dial-wrapper.active .dial-backplate {
    width: 220px; 
    height: 220px;
    opacity: 1;
    background: #ffffff;
    border-width: 1px;
    border-color: rgba(0,0,0,0.1);
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

/* 2. 核心显示 */
.dial-core {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: var(--theme-bg);
    border: 2px solid var(--theme-color);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    position: relative;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.rune-dial-wrapper.active .dial-core {
    background: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: scale(1.1);
}

.dial-core:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}


.current-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--theme-color);
    line-height: 1;

    /* 新增以下两行 */
    position: relative; /* 确保 transform 生效 */
    transform: translateY(-2px); /* 向上移动 2px，具体数值可以微调 */
}


/* 3. 符文环 */
.rune-ring {
    position: absolute;
    top: 50%; left: 50%;
    width: 200px; height: 200px;
    transform: translate(-50%, -50%) scale(0.8);
    pointer-events: none;
    opacity: 0;
    transition: all 0.25s ease-out;
    z-index: 2;
}

.rune-dial-wrapper.active .rune-ring {
    opacity: 1;
    pointer-events: auto;
    transform: translate(-50%, -50%) scale(1);
}

/* 单个按钮 */
.rune-item {
    position: absolute;
    width: 36px; height: 36px;
    line-height: 36px;
    text-align: center;
    border-radius: 50%;
    background: #fff; 
    color: var(--theme-color);
    border: 1px solid var(--theme-sub-color);
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: 0.2s;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.rune-item:hover {
    background: var(--theme-color);
    color: #fff;
    border-color: var(--theme-color);
    transform: scale(1.15);
    box-shadow: 0 4px 8px rgba(var(--theme-color), 0.3);
    z-index: 10;
}

.rune-edit {
    border-style: dashed;
}

/* 4. 输入框 */
.core-input {
    position: absolute;
    width: 46px;
    height: 32px;
    background: transparent;
    border: none;
    border-bottom: 2px solid var(--theme-color);
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    color: var(--theme-color);
    outline: none;
    display: none;
}

.dial-core.input-mode .current-value {
    opacity: 0;
}

.dial-core.input-mode .core-input {
    display: block;
}
</style>