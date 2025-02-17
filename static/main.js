// 字段配置对象
const fieldConfigs = {
    common: {
        class: {
            type: 'select',
            options: ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立', '弱点'],
            required: true
        },
        name: {
            type: 'text',
            required: true
        },
        body: {
            type: 'textarea',
            required: true
        },
        traits: { 
            type: 'array',
            required: true 
        }
    },
    weakness: {
        weakness_type: {
            type: 'select',
            options: ['弱点', '基础弱点'],
            required: true
        }
    },
    技能卡: {
        submit_icon: { type: 'array', options: ['意志', '战力', '敏捷', '智力', '狂野'] },
        level: { 
            type: 'number',
            isInteger: true,
            min: -1,
            placeholder: '等级(-1表示无等级)'
        },
        flavor: { type: 'textarea' }
    },
    支援卡: {
        cost: { 
            type: 'number',
            isInteger: true,
            min: -2,
            placeholder: '费用(-1表示无费用, -2表示X费用)'
        },
        submit_icon: { type: 'array', options: ['意志', '战力', '敏捷', '智力', '狂野'] },
        level: { 
            type: 'number',
            isInteger: true,
            min: -1,
            placeholder: '等级(-1表示无等级)'
        },
        slots: { 
            type: 'select',
            options: ['空', '双手', '双法术', '塔罗', '手部', '法术', '盟友', '身体', '饰品']
        },
        health: { 
            type: 'number',
            isInteger: true,
            min: 0
        },
        horror: { 
            type: 'number',
            isInteger: true,
            min: 0
        },
        flavor: { type: 'textarea' },
        subclass: {
            type: 'multiselect',
            options: ['守护者', '探求者', '流浪者', '潜修者', '生存者'],
            maxSelect: 2,
            required: true
        }
    },
    事件卡: {
        cost: { 
            type: 'number',
            isInteger: true,
            min: -2,
            placeholder: '费用(-1表示无费用, -2表示X费用)'
        },
        level: { 
            type: 'number',
            isInteger: true,
            min: -1,
            placeholder: '等级(-1表示无等级)'
        },
        submit_icon: { type: 'array', options: ['意志', '战力', '敏捷', '智力', '狂野'] },
        flavor: { type: 'textarea' },
        subclass: {
            type: 'multiselect',
            options: ['守护者', '探求者', '流浪者', '潜修者', '生存者'],
            maxSelect: 2,
            required: true
        }
    },
    调查员卡: {
        subtitle: {
            type: 'text',
            required: true
        },
        attribute: { type: 'attribute' },
        traits: {  // 添加 traits 字段
            type: 'array',
            required: true
        },
        body: {  // 这个字段来自 common，但我们在这里显式定义以控制顺序
            type: 'textarea',
            required: true
        },
        flavor: { 
            type: 'textarea',
            required: false
        },
        health: { 
            type: 'number',
            isInteger: true,
            min: 0
        },
        horror: { 
            type: 'number',
            isInteger: true,
            min: 0
        },
        card_back: { type: 'card_back' }
    },
    升级卡: {
        // 只需要name和body
    }
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化配置
    loadConfig();
    
    // 绑定表单提交事件
    document.getElementById('configForm').addEventListener('submit', handleConfigSubmit);
    document.getElementById('generateForm').addEventListener('submit', handleGenerateSubmit);
    document.getElementById('cardForm').addEventListener('submit', handleCardSubmit);
    
    // 监听卡牌类型变化
    document.getElementById('cardType').addEventListener('change', updateDynamicFields);
    
    // 监听 class 选择变化
    document.getElementById('cardForm').addEventListener('change', function(event) {
        if (event.target.name === 'class') {
            handleClassChange(event.target.value);
        }
    });
    
    // 初始化动态字段
    updateDynamicFields();
    
    // 添加导出按钮事件监听
    document.getElementById('exportJson').addEventListener('click', handleExportJson);
    
    // 添加导入按钮事件监听
    document.getElementById('importJson').addEventListener('change', handleImportJson);
});

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        if (data.code === 0) {
            const form = document.getElementById('configForm');
            form.base_url.value = data.data.base_url;
            form.api_key.value = data.data.api_key;
            form.model.value = data.data.model;
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

// 处理配置提交
async function handleConfigSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const config = Object.fromEntries(formData);
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        const data = await response.json();
        if (data.code === 0) {
            showToast('配置保存成功', '成功', 'success');
        } else {
            showToast('配置保存失败: ' + data.msg, '错误', 'error');
        }
    } catch (error) {
        showToast('配置保存失败: ' + error.message, '错误', 'error');
    }
}

// 处理AI生成JSON
async function handleGenerateSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = document.getElementById('generateSpinner');
    
    try {
        // 显示等待图标，禁用按钮
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        
        // 先生成 JSON
        const response = await fetch('/api/generate-json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: form.text.value
            })
        });
        const data = await response.json();
        
        if (data.code === 0) {
            // 填充表单
            fillCardForm(data.data);
            
            // 准备生成图片
            const formData = new FormData();
            formData.append('json', JSON.stringify(data.data));
            
            // 如果有上传图片，使用生成表单中的图片
            const imageFile = form.image.files[0];
            if (imageFile) {
                formData.append('image', imageFile);
            }
            
            // 生成图片
            const imgResponse = await fetch('/api/generate-image', {
                method: 'POST',
                body: formData
            });
            const imgData = await imgResponse.json();
            
            if (imgData.code === 0) {
                updatePreview(imgData.data.url, imgData.data.back_url);
                showToast('卡牌生成成功！', '成功', 'success');
            } else {
                showToast('生成图片失败: ' + imgData.msg, '错误', 'error');
            }
        } else {
            showToast('生成JSON失败: ' + data.msg, '错误', 'error');
        }
    } catch (error) {
        showToast('生成失败: ' + error.message, '错误', 'error');
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        spinner.style.display = 'none';
    }
}

// 处理卡牌生成
async function handleCardSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData();
    
    // 创建基础 JSON 对象，包含所有必需字段
    const jsonData = {
        type: '',
        class: '',
        name: '',
        body: '',
        traits: [],
        weakness_type: '',
        subtitle: '',
        attribute: [],
        cost: 0,
        submit_icon: [],
        level: -1,
        flavor: '',
        slots: '',
        health: 0,
        horror: 0,
        card_back: {
            size: 30,
            option: [],
            requirement: '',
            other: '',
            story: ''
        },
        msg: ''
    };
    
    // 获取表单类型
    const type = form.type.value;
    jsonData.type = type;
    
    if (type === '升级卡') {
        // 升级卡只需要 name 和 body
        jsonData.name = form.name.value;
        jsonData.body = form.body.value;
    } else {
        // 添加通用字段
        Object.keys(fieldConfigs.common).forEach(field => {
            if (field === 'traits') {
                // 特别处理 traits 数组
                const traitsContainer = document.getElementById('traits-items');
                if (traitsContainer) {
                    const traitsInputs = traitsContainer.querySelectorAll('[name="traits[]"]');
                    jsonData.traits = Array.from(traitsInputs)
                        .map(input => input.value)
                        .filter(value => value.trim() !== '');
                }
            } else if (form[field]) {
                jsonData[field] = form[field].value;
            }
        });
        
        // 如果是弱点类型，添加 weakness_type
        if (jsonData.class === '弱点') {
            const weaknessType = form['weakness_type'];
            if (weaknessType) {
                jsonData.weakness_type = weaknessType.value;
            }
        }
        
        // 如果是调查员卡，处理 attribute 数组
        if (type === '调查员卡') {
            const attributeInputs = form.querySelectorAll('[name="attribute[]"]');
            jsonData.attribute = Array.from(attributeInputs).map(input => 
                parseInt(input.value) || 0
            );
        }
        
        // 添加特定类型字段
        if (fieldConfigs[type]) {
            Object.keys(fieldConfigs[type]).forEach(field => {
                if (field === 'card_back') {
                    // 特别处理 card_back 对象
                    const cardBack = {
                        size: parseInt(form['card_back.size']?.value) || 30,
                        option: [],
                        requirement: form['card_back.requirement']?.value || '',
                        other: form['card_back.other']?.value || '',
                        story: form['card_back.story']?.value || ''
                    };
                    
                    // 处理 option 数组
                    const optionContainer = document.getElementById('card_back-option-items');
                    if (optionContainer) {
                        const optionInputs = optionContainer.querySelectorAll('[name="card_back.option[]"]');
                        cardBack.option = Array.from(optionInputs)
                            .map(input => input.value)
                            .filter(value => value.trim() !== '');
                    }
                    
                    jsonData.card_back = cardBack;
                } else if (field === 'submit_icon') {
                    // 处理 submit_icon 数组
                    const submitIconContainer = document.getElementById('submit_icon-items');
                    if (submitIconContainer) {
                        const items = submitIconContainer.querySelectorAll('[name="submit_icon[]"]');
                        jsonData.submit_icon = Array.from(items)
                            .map(input => input.value)
                            .filter(value => value.trim() !== '');
                    }
                } else if (form[field]) {
                    const config = fieldConfigs[type][field];
                    if (config.type === 'number' && config.isInteger) {
                        // 确保数字字段为整数
                        const value = parseInt(form[field].value) || 0;
                        // 根据配置的最小值来限制
                        const minValue = config.min !== undefined ? config.min : 0;
                        jsonData[field] = Math.max(minValue, value);
                    } else if (config.type === 'textarea' || config.type === 'text') {
                        // 文本类型字段使用空字符串作为默认值
                        jsonData[field] = form[field].value || '';
                    } else {
                        // 其他类型字段保持原值
                        jsonData[field] = form[field].value;
                    }
                }
            });
        }
    }
    
    // 在 handleCardSubmit 函数中添加 subclass 处理
    if (jsonData.class === '多职阶' && (type === '事件卡' || type === '支援卡')) {
        const subclassInputs = form.querySelectorAll('[name="subclass[]"]:checked');
        jsonData.subclass = Array.from(subclassInputs).map(input => input.value);
    }
    
    // 将json对象转为字符串
    formData.append('json', JSON.stringify(jsonData));
    
    // 添加图片文件（如果有）
    const imageFile = form.image.files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.code === 0) {
            updatePreview(data.data.url, data.data.back_url);
            showToast('卡牌生成成功！', '成功', 'success');
        } else {
            showToast('生成失败: ' + data.msg, '错误', 'error');
        }
    } catch (error) {
        showToast('生成失败: ' + error.message, '错误', 'error');
    }
}

// 更新动态字段
function updateDynamicFields() {
    const type = document.getElementById('cardType').value;
    const container = document.getElementById('dynamicFields');
    container.innerHTML = '';
    
    if (type === '升级卡') {
        // 升级卡只需要 name 和 body
        addField(container, 'name', {
            type: 'text',
            required: true
        });
        addField(container, 'body', {
            type: 'textarea',
            required: true
        });
    } else {
        // 添加 class 字段（根据卡牌类型提供不同的选项）
        const classConfig = {
            type: 'select',
            options: ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立'],
            required: true
        };
        
        // 如果不是调查员卡，添加弱点选项
        if (type !== '调查员卡') {
            classConfig.options.push('弱点');
        }
        
        // 如果是事件卡或支援卡，添加多职阶选项
        if (type === '事件卡' || type === '支援卡') {
            classConfig.options.push('多职阶');
        }
        
        addField(container, 'class', classConfig);
        
        // 添加其他字段
        if (type === '调查员卡') {
            // 调查员卡使用特定顺序
            const fields = ['name', 'subtitle', 'attribute', 'traits','body', 'flavor',  'health', 'horror', 'card_back'];
            fields.forEach(field => {
                const config = fieldConfigs.调查员卡[field] || fieldConfigs.common[field];
                if (config) {
                    addField(container, field, config);
                }
            });
        } else {
            // 其他卡牌类型使用统一的字段顺序
            // 1. 先添加通用字段（除了 class）
            const commonFields = ['name', 'body'];
            commonFields.forEach(field => {
                if (fieldConfigs.common[field]) {
                    addField(container, field, fieldConfigs.common[field]);
                }
            });
            
            // 2. 添加特定类型字段（除了 flavor）
            if (fieldConfigs[type]) {
                const typeFields = Object.entries(fieldConfigs[type])
                    .filter(([field]) => field !== 'flavor' && field !== 'class' && field !== 'subclass');
                typeFields.forEach(([field, config]) => {
                    addField(container, field, config);
                });
            }
            
            // 3. 添加 traits
            if (fieldConfigs.common.traits) {
                addField(container, 'traits', fieldConfigs.common.traits);
            }
            
            // 4. 添加 flavor（如果存在）
            if (fieldConfigs[type]?.flavor) {
                addField(container, 'flavor', fieldConfigs[type].flavor);
            }
        }
        
        // 使用 setTimeout 确保 DOM 已更新
        setTimeout(() => {
            const classSelect = container.querySelector('[name="class"]');
            if (classSelect && classSelect.value === '弱点') {
                handleClassChange('弱点');
            }
        }, 0);
    }
}

// 添加表单字段
function addField(container, field, config) {
    const div = document.createElement('div');
    div.className = 'mb-3';
    
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = field;
    div.appendChild(label);
    
    switch (config.type) {
        case 'text':
            div.appendChild(createTextInput(field, config));
            break;
        case 'number':
            div.appendChild(createNumberInput(field, config));
            break;
        case 'textarea':
            div.appendChild(createTextArea(field, config));
            break;
        case 'select':
            div.appendChild(createSelect(field, config));
            break;
        case 'array':
            div.appendChild(createArrayInput(field, config));
            break;
        case 'attribute':
            div.appendChild(createAttributeInput(field));
            break;
        case 'card_back':
            div.appendChild(createCardBackInput(field));
            break;
        case 'multiselect':
            div.appendChild(createMultiSelect(field, config));
            break;
    }
    
    container.appendChild(div);
}

// 创建文本输入
function createTextInput(name, config) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = name;
    input.className = 'form-control';
    input.required = config.required;
    return input;
}

// 创建数字输入
function createNumberInput(name, config) {
    const input = document.createElement('input');
    input.type = 'number';
    input.name = name;
    input.className = 'form-control';
    input.required = config.required;
    
    // 如果是整数类型，设置 step 为 1
    if (config.isInteger) {
        input.step = '1';
        // 设置最小值
        if (config.min !== undefined) {
            input.min = config.min;
        } else {
            input.min = '0';  // 默认最小值为 0
        }
    }
    
    // 添加提示文本
    if (config.placeholder) {
        input.placeholder = config.placeholder;
    }
    
    // 添加浮动提示
    if (config.min === -1 || config.min === -2) {
        const wrapper = document.createElement('div');
        wrapper.className = 'input-group';
        
        const tooltip = document.createElement('span');
        tooltip.className = 'input-group-text';
        tooltip.setAttribute('data-bs-toggle', 'tooltip');
        tooltip.setAttribute('data-bs-placement', 'top');
        tooltip.title = config.placeholder;
        tooltip.innerHTML = '<i class="bi bi-question-circle"></i>';
        
        wrapper.appendChild(input);
        wrapper.appendChild(tooltip);
        
        // 初始化 tooltip
        setTimeout(() => {
            new bootstrap.Tooltip(tooltip);
        }, 0);
        
        return wrapper;
    }
    
    return input;
}

// 创建文本区域输入
function createTextArea(name, config) {
    const container = document.createElement('div');
    
    // 创建文本区域
    const textarea = document.createElement('textarea');
    textarea.className = 'form-control mb-2';
    textarea.name = name;
    textarea.rows = name === 'body' ? 8 : 3;  // body 字段使用更大的输入框
    if (config.required) {
        textarea.required = true;
    }
    
    // 如果是 body 字段，添加输入提示
    if (name === 'body') {
        // 创建提示区域
        const helpText = document.createElement('div');
        helpText.className = 'form-text small';
        helpText.innerHTML = `
            <p class="mb-1"><strong>特殊标签说明：</strong></p>
            <ul class="list-unstyled mb-2">
                <li>【文本】：思源黑体</li>
                <li>{文本}：方正舒体</li>
            </ul>
            <p class="mb-1"><strong>特殊图标标签：</strong></p>
            <div class="d-flex flex-wrap gap-2 mb-2">
                <span class="badge bg-secondary">&lt;独特&gt;</span>
                <span class="badge bg-secondary">&lt;一&gt;</span>
                <span class="badge bg-secondary">&lt;点&gt;</span>
                <span class="badge bg-secondary">&lt;反应&gt;</span>
                <span class="badge bg-secondary">&lt;启动&gt;</span>
                <span class="badge bg-secondary">&lt;免费&gt;</span>
            </div>
            <div class="d-flex flex-wrap gap-2 mb-2">
                <span class="badge bg-secondary">&lt;骷髅&gt;</span>
                <span class="badge bg-secondary">&lt;异教徒&gt;</span>
                <span class="badge bg-secondary">&lt;石板&gt;</span>
                <span class="badge bg-secondary">&lt;古神&gt;</span>
                <span class="badge bg-secondary">&lt;触手&gt;</span>
                <span class="badge bg-secondary">&lt;旧印&gt;</span>
            </div>
            <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-secondary">&lt;拳&gt;</span>
                <span class="badge bg-secondary">&lt;书&gt;</span>
                <span class="badge bg-secondary">&lt;脚&gt;</span>
                <span class="badge bg-secondary">&lt;脑&gt;</span>
                <span class="badge bg-secondary">&lt;诅咒&gt;</span>
                <span class="badge bg-secondary">&lt;祝福&gt;</span>
                <span class="badge bg-secondary">&lt;调查员&gt;</span>
            </div>
        `;
        
        container.appendChild(textarea);
        container.appendChild(helpText);
    } else {
        container.appendChild(textarea);
    }
    
    return container;
}

// 创建选择框
function createSelect(name, config) {
    const select = document.createElement('select');
    select.name = name;
    select.className = 'form-select';
    select.required = config.required;
    
    config.options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.textContent = option;
        select.appendChild(opt);
    });
    
    return select;
}

// 创建数组输入
function createArrayInput(name, config) {
    const container = document.createElement('div');
    container.className = 'array-container';
    
    const itemsContainer = document.createElement('div');
    itemsContainer.id = `${name}-items`;
    
    const addButton = document.createElement('button');
    addButton.type = 'button';
    addButton.className = 'btn btn-outline-secondary btn-sm';
    addButton.textContent = '添加';
    addButton.onclick = () => addArrayItem(name, itemsContainer, config);
    
    container.appendChild(itemsContainer);
    container.appendChild(addButton);
    
    return container;
}

// 添加数组项
function addArrayItem(name, container, config) {
    const div = document.createElement('div');
    div.className = 'form-array-item mb-2';
    
    if (config.options) {
        // 如果有预定义选项，使用选择框
        const select = document.createElement('select');
        select.className = 'form-select';
        select.name = `${name}[]`;
        
        // 添加空选项
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '请选择';
        select.appendChild(emptyOption);
        
        // 添加预定义选项
        config.options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.textContent = option;
            select.appendChild(opt);
        });
        
        div.appendChild(select);
    } else {
        // 否则使用文本输入框
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        input.name = `${name}[]`;
        div.appendChild(input);
    }
    
    // 添加删除按钮
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'btn btn-outline-danger btn-sm';
    removeButton.textContent = '删除';
    removeButton.onclick = () => div.remove();
    
    div.appendChild(removeButton);
    container.appendChild(div);
}

// 更新预览图片
function updatePreview(url, backUrl = null) {
    const previewContainer = document.querySelector('.preview-container');
    const preview = document.getElementById('previewImage');
    const backPreview = document.getElementById('backPreviewImage');
    const backPreviewContainer = backPreview.parentElement;
    const placeholder = document.getElementById('placeholder');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadBackBtn = document.getElementById('downloadBackBtn');
    
    // 显示正面图片
    preview.src = url;
    preview.style.display = 'block';
    placeholder.style.display = 'none';
    downloadBtn.href = url;
    downloadBtn.download = 'card_front.png';
    downloadBtn.style.display = 'inline-block';
    
    // 处理背面图片
    if (backUrl) {
        backPreview.src = backUrl;
        backPreviewContainer.style.display = 'block';
        downloadBackBtn.href = backUrl;
        downloadBackBtn.download = 'card_back.png';
        downloadBackBtn.style.display = 'inline-block';
        previewContainer.classList.add('has-back');  // 添加标记类
    } else {
        backPreviewContainer.style.display = 'none';
        downloadBackBtn.style.display = 'none';
        previewContainer.classList.remove('has-back');  // 移除标记类
    }
}

// 填充卡牌表单
function fillCardForm(data) {
    const form = document.getElementById('cardForm');
    form.type.value = data.type;
    updateDynamicFields();
    
    // 使用 setTimeout 确保 DOM 已更新
    setTimeout(() => {
        // 处理本地图片
        if (data.localImage?.data) {
            // 从 base64 创建 File 对象
            const byteString = atob(data.localImage.data.split(',')[1]);
            const mimeString = data.localImage.data.split(',')[0].split(':')[1].split(';')[0];
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            const blob = new Blob([ab], { type: mimeString });
            const file = new File([blob], data.localImage.name, { type: mimeString });
            
            // 创建 DataTransfer 对象来设置 files
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            // 设置文件到所有图片输入框
            const imageInputs = form.querySelectorAll('[name="image"]');
            imageInputs.forEach(input => {
                input.files = dataTransfer.files;
            });
        }
        
        Object.entries(data).forEach(([key, value]) => {
            if (key === 'attribute' && Array.isArray(value)) {
                // 特别处理 attribute 数组
                const inputs = document.querySelectorAll('[name="attribute[]"]');
                const attributes = ['意志', '智力', '战力', '敏捷'];
                attributes.forEach((attr, index) => {
                    if (inputs[index] && value[index] !== undefined) {
                        inputs[index].value = value[index];
                    }
                });
            } else if (key === 'card_back' && typeof value === 'object') {
                // 特别处理 card_back 对象
                Object.entries(value).forEach(([field, fieldValue]) => {
                    if (field === 'option' && Array.isArray(fieldValue)) {
                        // 处理选项数组
                        const container = document.getElementById('card_back-option-items');
                        if (container) {
                            container.innerHTML = '';
                            // 为每个选项创建一个输入框并设置值
                            fieldValue.forEach(option => {
                                if (option && option.toString().trim()) {
                                    addArrayItem('card_back.option', container, { type: 'array' });
                                    // 获取最后添加的输入框
                                    const inputs = container.querySelectorAll('[name="card_back.option[]"]');
                                    const lastInput = inputs[inputs.length - 1];
                                    if (lastInput) {
                                        lastInput.value = option;
                                    }
                                }
                            });
                        }
                    } else {
                        // 处理其他字段
                        const element = form.querySelector(`[name="card_back.${field}"]`);
                        if (element) {
                            element.value = fieldValue;
                        }
                    }
                });
            } else if (Array.isArray(value)) {
                // 处理其他数组类型字段
                const container = document.getElementById(`${key}-items`);
                if (container) {
                    container.innerHTML = '';
                    // 确保 value 是一个一维数组
                    const items = Array.isArray(value[0]) ? value[0] : value;
                    
                    // 为每个值创建一个输入框并设置值
                    items.forEach((item, index) => {
                        if (item && item.toString().trim()) {
                            // 获取对应的配置
                            const config = fieldConfigs[data.type]?.[key] || fieldConfigs.common[key];
                            addArrayItem(key, container, config);
                            // 获取所有输入框并设置对应索引的值
                            const inputs = container.querySelectorAll(`[name="${key}[]"]`);
                            if (inputs[index]) {
                                inputs[index].value = item;
                            }
                        }
                    });
                }
            } else {
                const element = form.elements[key];
                if (element) {
                    element.value = value;
                    // 如果是 class 字段且值为弱点，触发 handleClassChange
                    if (key === 'class' && value === '弱点') {
                        handleClassChange('弱点');
                    }
                }
            }
        });
    }, 0);
}

// 处理 class 变化的函数
function handleClassChange(classValue) {
    const type = document.getElementById('cardType').value;
    if (type !== '升级卡') {
        const container = document.getElementById('dynamicFields');
        const weaknessContainer = container.querySelector('.weakness-type-container');
        const subclassContainer = container.querySelector('.subclass-container');
        
        // 处理弱点类型
        if (classValue === '弱点') {
            if (!weaknessContainer) {
                // 如果不存在 weakness_type，则添加
                const config = fieldConfigs.weakness.weakness_type;
                const div = document.createElement('div');
                div.className = 'mb-3 weakness-type-container';
                
                const label = document.createElement('label');
                label.className = 'form-label';
                label.textContent = 'weakness_type';
                div.appendChild(label);
                
                div.appendChild(createSelect('weakness_type', config));
                
                // 插入到 class 字段之后
                const classField = container.querySelector('[name="class"]').parentNode;
                classField.parentNode.insertBefore(div, classField.nextSibling);
            }
            // 移除 subclass 容器
            if (subclassContainer) {
                subclassContainer.remove();
            }
        } else if (classValue === '多职阶' && (type === '事件卡' || type === '支援卡')) {
            // 移除弱点容器
            if (weaknessContainer) {
                weaknessContainer.remove();
            }
            // 添加 subclass 选择
            if (!subclassContainer) {
                const config = fieldConfigs[type].subclass;
                const div = document.createElement('div');
                div.className = 'mb-3 subclass-container';
                
                const label = document.createElement('label');
                label.className = 'form-label';
                label.textContent = 'subclass';
                div.appendChild(label);
                
                div.appendChild(createMultiSelect('subclass', config));
                
                // 插入到 class 字段之后
                const classField = container.querySelector('[name="class"]').parentNode;
                classField.parentNode.insertBefore(div, classField.nextSibling);
            }
        } else {
            // 移除两个容器
            if (weaknessContainer) {
                weaknessContainer.remove();
            }
            if (subclassContainer) {
                subclassContainer.remove();
            }
        }
    }
}

// 创建多选框
function createMultiSelect(name, config) {
    const container = document.createElement('div');
    container.className = 'multiselect-container';
    
    const selectedCount = document.createElement('div');
    selectedCount.className = 'text-muted mb-2';
    selectedCount.textContent = `请选择1-${config.maxSelect}个职阶`;
    container.appendChild(selectedCount);
    
    config.options.forEach(option => {
        const div = document.createElement('div');
        div.className = 'form-check';
        
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'form-check-input';
        input.name = `${name}[]`;
        input.value = option;
        input.id = `${name}_${option}`;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `${name}_${option}`;
        label.textContent = option;
        
        div.appendChild(input);
        div.appendChild(label);
        container.appendChild(div);
    });
    
    // 添加选择限制
    container.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            const checked = container.querySelectorAll('input:checked');
            if (checked.length > config.maxSelect) {
                e.target.checked = false;
                showToast(`最多只能选择${config.maxSelect}个职阶`, '提示', 'warning');
            }
            selectedCount.textContent = `已选择 ${checked.length}/${config.maxSelect} 个职阶`;
        }
    });
    
    return container;
}

// 添加显示提示的函数
function showToast(message, title = '提示', type = 'info') {
    const toast = document.getElementById('messageToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    // 设置标题和消息
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    // 设置样式
    toast.className = 'toast';
    switch (type) {
        case 'error':
            toast.classList.add('bg-danger', 'text-white');
            break;
        case 'success':
            toast.classList.add('bg-success', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-warning');
            break;
        default:
            toast.classList.add('bg-info', 'text-white');
    }
    
    // 显示 Toast
    const bsToast = new bootstrap.Toast(toast, {
        animation: true,
        autohide: true,
        delay: 3000
    });
    bsToast.show();
}

// 创建属性输入
function createAttributeInput(name) {
    const container = document.createElement('div');
    container.className = 'attribute-container';
    
    // 添加四个属性输入框
    const attributes = ['意志', '智力', '战力', '敏捷'];
    attributes.forEach(attr => {
        const div = document.createElement('div');
        div.className = 'mb-2';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = attr;
        
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control';
        input.name = `${name}[]`;
        input.min = '1';
        input.max = '9';  // 修改最大值为9
        input.step = '1';
        input.placeholder = '1-9';  // 更新提示文本
        
        div.appendChild(label);
        div.appendChild(input);
        container.appendChild(div);
    });
    
    return container;
}

// 创建卡牌背面输入
function createCardBackInput(name) {
    const container = document.createElement('div');
    container.className = 'card-back-container';
    
    // 添加卡牌背面的各个字段
    const fields = {
        size: { type: 'number', label: '卡牌尺寸', placeholder: '默认30' },
        option: { type: 'array', label: '选项' },
        requirement: { type: 'text', label: '要求' },
        other: { type: 'textarea', label: '其他' },
        story: { type: 'textarea', label: '背景故事' }
    };
    
    Object.entries(fields).forEach(([field, config]) => {
        const div = document.createElement('div');
        div.className = 'mb-2';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = config.label;
        div.appendChild(label);
        
        switch (config.type) {
            case 'number':
                const input = document.createElement('input');
                input.type = 'number';
                input.className = 'form-control';
                input.name = `${name}.${field}`;
                input.placeholder = config.placeholder;
                div.appendChild(input);
                break;
            case 'text':
                const textInput = document.createElement('input');
                textInput.type = 'text';
                textInput.className = 'form-control';
                textInput.name = `${name}.${field}`;
                div.appendChild(textInput);
                break;
            case 'textarea':
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control';
                textarea.name = `${name}.${field}`;
                textarea.rows = 3;
                div.appendChild(textarea);
                break;
            case 'array':
                const arrayContainer = document.createElement('div');
                arrayContainer.id = `${name}-${field}-items`;
                arrayContainer.className = 'array-container';
                
                const addButton = document.createElement('button');
                addButton.type = 'button';
                addButton.className = 'btn btn-outline-secondary btn-sm mb-2';
                addButton.textContent = '添加选项';
                addButton.onclick = () => addArrayItem(`${name}.${field}`, arrayContainer, { type: 'array' });
                
                div.appendChild(arrayContainer);
                div.appendChild(addButton);
                break;
        }
        
        container.appendChild(div);
    });
    
    return container;
}

// 导出 JSON 函数
async function handleExportJson() {
    const form = document.getElementById('cardForm');
    const jsonData = await getFormData(form);
    
    // 创建并下载 JSON 文件
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `card_${jsonData.name || 'unnamed'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 获取表单数据的辅助函数
async function getFormData(form) {
    const formData = new FormData(form);
    const jsonData = {
        type: form.type.value,
        class: '',
        name: '',
        body: '',
        traits: [],
        weakness_type: '',
        subtitle: '',
        attribute: [],
        cost: 0,
        submit_icon: [],
        level: -1,
        flavor: '',
        slots: '',
        health: 0,
        horror: 0,
        card_back: {
            size: 30,
            option: [],
            requirement: '',
            other: '',
            story: ''
        }
    };
    
    // 处理图片文件
    const imageFile = form.image.files[0];
    if (imageFile) {
        // 读取文件内容为 base64
        const base64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(imageFile);
        });
        
        jsonData.localImage = {
            name: imageFile.name,
            type: imageFile.type,
            size: imageFile.size,
            data: base64
        };
    }
    
    // 处理表单数据
    for (const [key, value] of formData.entries()) {
        if (key.includes('[]')) {
            // 处理数组类型字段
            const fieldName = key.replace('[]', '');
            if (!jsonData[fieldName]) {
                jsonData[fieldName] = [];
            }
            if (value.trim()) {
                jsonData[fieldName].push(value);
            }
        } else if (key.startsWith('card_back.')) {
            // 特别处理 card_back 对象的字段
            const field = key.replace('card_back.', '');
            if (field === 'size') {
                jsonData.card_back.size = parseInt(value) || 30;
            } else if (field !== 'option') { // 忽略 option 字段，因为会在后面特别处理
                jsonData.card_back[field] = value;
            }
        } else {
            // 处理普通字段
            const config = fieldConfigs[jsonData.type]?.[key] || fieldConfigs.common[key];
            if (config?.type === 'number' && config.isInteger) {
                // 数字类型字段转换为整数
                jsonData[key] = parseInt(value) || 0;
            } else {
                jsonData[key] = value;
            }
        }
    }
    
    // 特别处理 card_back.option 数组
    const optionContainer = document.getElementById('card_back-option-items');
    if (optionContainer) {
        const optionInputs = optionContainer.querySelectorAll('[name="card_back.option[]"]');
        jsonData.card_back.option = Array.from(optionInputs)
            .map(input => input.value)
            .filter(value => value.trim() !== '');
    }
    
    // 特别处理 attribute 数组，确保是整数数组
    if (jsonData.type === '调查员卡') {
        const attributeInputs = form.querySelectorAll('[name="attribute[]"]');
        jsonData.attribute = Array.from(attributeInputs).map(input => 
            parseInt(input.value) || 0
        );
    }
    
    // 确保数字字段为整数类型
    ['cost', 'level', 'health', 'horror'].forEach(field => {
        if (typeof jsonData[field] === 'string') {
            jsonData[field] = parseInt(jsonData[field]) || 0;
        }
    });
    
    return jsonData;
}

// 导入 JSON 函数
async function handleImportJson(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        const text = await file.text();
        const jsonData = JSON.parse(text);
        
        // 移除可能存在的图片URL
        delete jsonData.imageUrl;
        delete jsonData.backImageUrl;
        
        // 填充表单数据
        fillCardForm(jsonData);
        
        // 等待一下确保表单完全填充
        setTimeout(() => {
            // 模拟点击生成按钮
            const cardForm = document.getElementById('cardForm');
            const submitButton = cardForm.querySelector('button[type="submit"]');
            submitButton.click();
            
            showToast('JSON导入成功！', '成功', 'success');
        }, 100);
        
    } catch (error) {
        showToast('JSON格式错误', '错误', 'error');
    }
    
    // 清空文件输入，允许重复导入相同文件
    event.target.value = '';
} 