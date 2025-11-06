# Card Backs Asset Module

## Purpose and Scope

提供阿卡姆恐怖游戏卡牌的背面图像资源。本模块包含两种主要卡牌类型的背面设计：玩家卡（Player Cards）和遭遇卡（Encounter Cards）。这些图像资源用于前端UI渲染和卡牌导出功能。

## Structure Overview

本模块是一个纯资源目录，包含两个JPEG图像文件：

```
cardbacks/
├── player-back.jpg       (156.78 KB) - 玩家卡背面设计
└── encounter-back.jpg    (128.66 KB) - 遭遇卡背面设计
```

## Key Components

### 资源文件

#### `player-back.jpg`
- **用途**: 玩家卡牌的背面图像（调查员卡、技能卡、支援卡等）
- **尺寸**: 156.78 KB
- **用法**: 在卡牌渲染和TTS导出中用作玩家卡的标准背面
- **集成点**: 由`arkham-app/src/api`的卡牌导出模块和`bin/tts_card_converter.py`引用

#### `encounter-back.jpg`
- **用途**: 遭遇卡的背面图像（遭遇卡、弱点卡等）
- **尺寸**: 128.66 KB
- **用法**: 在卡牌渲染和TTS导出中用作遭遇卡的标准背面
- **集成点**: 由`arkham-app/src/api`的卡牌导出模块和`bin/tts_card_converter.py`引用

## Dependencies

### Internal Dependencies
- `arkham-app/src/api/` - API层使用这些资源进行卡牌导出
- `bin/tts_card_converter.py` - TTS卡牌转换器使用这些背面图像
- `export_helper/main.py` - 导出助手可能引用这些资源

### External Dependencies
- JPEG图像格式支持（浏览器原生支持）
- Pillow库 (Python图像处理，用于后端卡牌生成)

## Integration Points

### Public APIs
无直接API。资源通过文件路径引用：
- 前端: `/src/assets/cardbacks/player-back.jpg`
- 前端: `/src/assets/cardbacks/encounter-back.jpg`

### Data Flow
1. **前端卡牌编辑**: 用户在UI中查看卡牌预览时，背面由这些资源渲染
2. **导出流程**:
   - 用户请求导出卡牌组
   - 后端`tts_card_converter.py`或`create_card.py`读取这些背面图像
   - 将背面与卡牌前面组合生成最终图像
   - 生成PDF或TTS所需的格式

### 资源加载
- 前端通过Vite静态资源处理加载
- 后端通过相对路径`./arkham-app/src/assets/cardbacks/`加载

## Implementation Notes

### Design Patterns
- **资源外部化模式**: 静态资源与代码分离，便于维护和更新

### 技术决策
1. **JPEG格式选择**: 平衡图像质量和文件大小
2. **两种背面**: 分别处理玩家卡和遭遇卡，提供精确的视觉一致性

### 性能考虑
- 图像文件大小合理，前端加载性能良好
- 后端渲染时，这些作为静态参考，不需要处理密集操作

### 维护考虑
- 如需更新卡牌背面设计，直接替换相应的JPG文件
- 确保尺寸和格式与现有文件兼容

### 已知限制
- 当前仅支持标准背面，不支持可自定义背面
- 固定的卡牌背面设计，无条件变体支持
