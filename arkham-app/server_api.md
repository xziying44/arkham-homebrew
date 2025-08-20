我来更新这个API文档，主要需要修改获取文件树接口的部分：

```markdown
# 文件管理服务 API 文档

## 概述

文件管理服务是一个基于Flask的后端服务，为桌面应用程序提供文件和目录管理功能。服务运行在本地，通过HTTP接口与前端应用交互。

- **服务地址**: `http://localhost:5000`
- **协议**: HTTP
- **数据格式**: JSON
- **版本**: 2.0.0

## 统一响应格式

所有API接口均使用以下统一响应格式：

```json
{
  "code": 0,
  // 响应码，0表示成功，非0表示错误
  "msg": "操作结果描述",
  // 响应消息
  "data": {}
  // 响应数据，可为null、对象或数组
}
```

## 错误码说明

| 错误码范围     | 分类     | 说明          |
|-----------|--------|-------------|
| 0         | 成功     | 操作成功        |
| 1001-1999 | 目录选择相关 | 目录选择操作相关错误  |
| 2001-2999 | 快速开始相关 | 最近目录管理相关错误  |
| 3001-3999 | 工作空间相关 | 工作空间操作相关错误  |
| 9001-9999 | 系统错误   | HTTP状态码相关错误 |

### 详细错误码

| 错误码       | 说明                |
|-----------|-------------------|
| 0         | 成功                |
| 1001      | 目录选择操作正在进行中，请稍后再试 |
| 1002      | 操作超时，请重试          |
| 1003      | 用户取消了选择           |
| 1004      | 选择目录时出错           |
| 1005      | 未能获取选择结果          |
| 1006      | 服务器错误             |
| 1007      | 创建工作空间失败          |
| 2001-2008 | 最近目录管理相关错误        |
| 3001      | 请先选择或打开工作目录       |
| 3002-3020 | 工作空间操作相关错误        |
| 9001      | 接口不存在 (404)       |
| 9002      | 请求方法不支持 (405)     |
| 9003      | 服务器内部错误 (500)     |

---

# 快速开始相关接口

## 1. 选择目录接口

### 基本信息

- **接口名称**: 选择目录
- **请求地址**: `/api/select-directory`
- **请求方法**: `GET`
- **功能描述**: 打开系统目录选择对话框，用户选择目录后返回目录路径，并自动添加到最近目录记录，创建工作空间实例

### 请求参数

无需传入参数

### 响应格式

| 字段             | 类型          | 说明              |
|----------------|-------------|-----------------|
| code           | integer     | 响应码             |
| msg            | string      | 响应消息            |
| data           | object/null | 响应数据            |
| data.directory | string      | 选择的目录路径（仅成功时返回） |

### 示例请求

```bash
curl -X GET /api/select-directory
```

### 示例响应

**成功选择目录**

```json
{
  "code": 0,
  "msg": "目录选择成功",
  "data": {
    "directory": "/Users/username/Documents/MyProject"
  }
}
```

## 2. 获取最近目录列表

### 基本信息

- **接口名称**: 获取最近目录列表
- **请求地址**: `/api/recent-directories`
- **请求方法**: `GET`
- **功能描述**: 获取最近打开的目录列表（最多20条）

### 响应格式

| 字段                                | 类型      | 说明     |
|-----------------------------------|---------|--------|
| data.directories                  | array   | 最近目录列表 |
| data.directories[].path           | string  | 目录路径   |
| data.directories[].name           | string  | 目录名称   |
| data.directories[].timestamp      | integer | 时间戳    |
| data.directories[].formatted_time | string  | 格式化时间  |

### 示例响应

```json
{
  "code": 0,
  "msg": "获取最近目录成功",
  "data": {
    "directories": [
      {
        "path": "/Users/username/Documents/Project1",
        "name": "Project1",
        "timestamp": 1699123456,
        "formatted_time": "2023-11-05 14:30:56"
      },
      {
        "path": "/Users/username/Desktop/MyApp",
        "name": "MyApp",
        "timestamp": 1699120000,
        "formatted_time": "2023-11-05 13:33:20"
      }
    ]
  }
}
```

## 3. 打开工作空间

### 基本信息

- **接口名称**: 打开工作空间
- **请求地址**: `/api/open-workspace`
- **请求方法**: `POST`
- **功能描述**: 打开指定目录作为工作空间

### 请求参数

| 参数名       | 类型     | 必填 | 说明       |
|-----------|--------|----|----------|
| directory | string | 是  | 要打开的目录路径 |

### 请求示例

```bash
curl -X POST /api/open-workspace \
  -H "Content-Type: application/json" \
  -d '{"directory": "/Users/username/Documents/MyProject"}'
```

## 4. 清空最近目录

### 基本信息

- **接口名称**: 清空最近目录
- **请求地址**: `/api/recent-directories`
- **请求方法**: `DELETE`
- **功能描述**: 清空所有最近目录记录

### 示例请求

```bash
curl -X DELETE /api/recent-directories
```

## 5. 移除指定最近目录

### 基本信息

- **接口名称**: 移除指定最近目录
- **请求地址**: `/api/recent-directories/<path:directory_path>`
- **请求方法**: `DELETE`
- **功能描述**: 移除指定的最近目录记录

### 请求参数

| 参数名            | 类型     | 位置    | 说明       |
|----------------|--------|-------|----------|
| directory_path | string | URL路径 | 要移除的目录路径 |

### 示例请求

```bash
curl -X DELETE "/api/recent-directories//Users/username/Documents/Project1"
```

---

# 工作空间相关接口

## 6. 获取文件树

### 基本信息

- **接口名称**: 获取文件树
- **请求地址**: `/api/file-tree`
- **请求方法**: `GET`
- **功能描述**: 获取工作目录的标准文件树结构，以工作空间目录为根节点，递归展示所有子目录和文件

### 请求参数

| 参数名            | 类型      | 必填 | 说明               |
|----------------|---------|----|------------------|
| include_hidden | boolean | 否  | 是否包含隐藏文件，默认false |

### 响应格式

返回标准的文件树结构，根节点为工作空间目录：

```typescript
interface TreeNode {
    label: string;           // 显示名称
    key: string;            // 唯一键值
    type: string;           // 类型标识
    path: string;           // 文件/目录完整路径
    children?: TreeNode[];  // 子节点数组（仅目录有此属性）
}
```

### 节点类型说明

| 类型        | 说明                         |
|-----------|----------------------------|
| workspace | 工作空间根节点                    |
| directory | 目录节点                       |
| card      | 卡牌文件 (.card)               |
| image     | 图片文件 (.png, .jpg, .svg等)   |
| config    | 配置文件 (.json, .yml等)        |
| text      | 文本文件 (.txt, .md等)          |
| style     | 样式文件 (.css等)               |
| data      | 数据文件 (.xml等)               |
| file      | 其他类型文件                     |

### 示例请求

```bash
curl -X GET "/api/file-tree?include_hidden=false"
```

### 示例响应

```json
{
  "code": 0,
  "msg": "获取文件树成功",
  "data": {
    "fileTree": {
      "label": "MyProject",
      "key": "workspace_1699123456000000",
      "type": "workspace",
      "path": "/Users/username/Documents/MyProject",
      "children": [
        {
          "label": "investigators",
          "key": "/Users/username/Documents/MyProject/investigators_1699123456000001",
          "type": "directory",
          "path": "/Users/username/Documents/MyProject/investigators",
          "children": [
            {
              "label": "Roland-Banks.card",
              "key": "/Users/username/Documents/MyProject/investigators/Roland-Banks.card_1699123456000002",
              "type": "card",
              "path": "/Users/username/Documents/MyProject/investigators/Roland-Banks.card"
            },
            {
              "label": "portraits",
              "key": "/Users/username/Documents/MyProject/investigators/portraits_1699123456000003",
              "type": "directory", 
              "path": "/Users/username/Documents/MyProject/investigators/portraits",
              "children": [
                {
                  "label": "roland.png",
                  "key": "/Users/username/Documents/MyProject/investigators/portraits/roland.png_1699123456000004",
                  "type": "image",
                  "path": "/Users/username/Documents/MyProject/investigators/portraits/roland.png"
                }
              ]
            }
          ]
        },
        {
          "label": "config.json",
          "key": "/Users/username/Documents/MyProject/config.json_1699123456000005",
          "type": "config",
          "path": "/Users/username/Documents/MyProject/config.json"
        },
        {
          "label": "README.md",
          "key": "/Users/username/Documents/MyProject/README.md_1699123456000006", 
          "type": "text",
          "path": "/Users/username/Documents/MyProject/README.md"
        }
      ]
    }
  }
}
```

### 文件树结构说明

- **根节点**: 始终是工作空间目录，类型为 `workspace`
- **目录节点**: 包含 `children` 数组，递归包含子目录和文件
- **文件节点**: 不包含 `children` 属性，根据扩展名自动识别类型
- **路径字段**: 所有节点都包含完整的文件系统路径
- **唯一键值**: 使用路径+微秒时间戳生成，确保前端渲染时的唯一性

## 7. 创建目录

### 基本信息

- **接口名称**: 创建目录
- **请求地址**: `/api/create-directory`
- **请求方法**: `POST`
- **功能描述**: 在工作空间中创建新目录

### 请求参数

| 参数名         | 类型     | 必填 | 说明               |
|-------------|--------|----|------------------|
| name        | string | 是  | 目录名称             |
| parent_path | string | 否  | 父目录路径，默认为工作空间根目录 |

### 请求示例

```bash
curl -X POST /api/create-directory \
  -H "Content-Type: application/json" \
  -d '{"name": "新目录", "parent_path": "/path/to/parent"}'
```

## 8. 创建文件

### 基本信息

- **接口名称**: 创建文件
- **请求地址**: `/api/create-file`
- **请求方法**: `POST`
- **功能描述**: 在工作空间中创建新文件

### 请求参数

| 参数名         | 类型     | 必填 | 说明               |
|-------------|--------|----|------------------|
| name        | string | 是  | 文件名称             |
| content     | string | 否  | 文件内容，默认为空        |
| parent_path | string | 否  | 父目录路径，默认为工作空间根目录 |

### 请求示例

```bash
curl -X POST /api/create-file \
  -H "Content-Type: application/json" \
  -d '{"name": "新文件.txt", "content": "Hello World", "parent_path": "/path/to/parent"}'
```

## 9. 重命名文件或目录

### 基本信息

- **接口名称**: 重命名文件或目录
- **请求地址**: `/api/rename-item`
- **请求方法**: `PUT`
- **功能描述**: 重命名工作空间中的文件或目录

### 请求参数

| 参数名      | 类型     | 必填 | 说明  |
|----------|--------|----|-----|
| old_path | string | 是  | 原路径 |
| new_name | string | 是  | 新名称 |

### 请求示例

```bash
curl -X PUT /api/rename-item \
  -H "Content-Type: application/json" \
  -d '{"old_path": "/path/to/old-name.txt", "new_name": "new-name.txt"}'
```

## 10. 删除文件或目录

### 基本信息

- **接口名称**: 删除文件或目录
- **请求地址**: `/api/delete-item`
- **请求方法**: `DELETE`
- **功能描述**: 删除工作空间中的文件或目录

### 请求参数

| 参数名  | 类型     | 必填 | 说明          |
|------|--------|----|-------------|
| path | string | 是  | 要删除的文件或目录路径 |

### 请求示例

```bash
curl -X DELETE /api/delete-item \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/file-or-directory"}'
```

## 11. 获取文件内容

### 基本信息

- **接口名称**: 获取文件内容
- **请求地址**: `/api/file-content`
- **请求方法**: `GET`
- **功能描述**: 读取指定文件的内容

### 请求参数

| 参数名  | 类型     | 必填 | 说明   |
|------|--------|----|------|
| path | string | 是  | 文件路径 |

### 请求示例

```bash
curl -X GET "/api/file-content?path=/path/to/file.txt"
```

### 响应示例

```json
{
  "code": 0,
  "msg": "获取文件内容成功",
  "data": {
    "content": "文件内容..."
  }
}
```

## 12. 保存文件内容

### 基本信息

- **接口名称**: 保存文件内容
- **请求地址**: `/api/file-content`
- **请求方法**: `PUT`
- **功能描述**: 保存内容到指定文件

### 请求参数

| 参数名     | 类型     | 必填 | 说明   |
|---------|--------|----|------|
| path    | string | 是  | 文件路径 |
| content | string | 是  | 文件内容 |

### 请求示例

```bash
curl -X PUT /api/file-content \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/file.txt", "content": "新的文件内容"}'
```

---

# 系统接口

## 13. 服务状态接口

### 基本信息

- **接口名称**: 获取服务状态
- **请求地址**: `/api/status`
- **请求方法**: `GET`
- **功能描述**: 获取服务运行状态和相关信息

### 响应格式

| 字段                  | 类型          | 说明           |
|---------------------|-------------|--------------|
| data.service        | string      | 服务名称         |
| data.version        | string      | 服务版本         |
| data.is_selecting   | boolean     | 是否正在进行目录选择操作 |
| data.has_workspace  | boolean     | 是否已打开工作空间    |
| data.workspace_path | string/null | 当前工作空间路径     |

### 示例响应

```json
{
  "code": 0,
  "msg": "服务正常运行",
  "data": {
    "service": "file-manager",
    "version": "2.0.0",
    "is_selecting": false,
    "has_workspace": true,
    "workspace_path": "/Users/username/Documents/MyProject"
  }
}
```

基于您的需求，我来为API文档添加两个新的卡牌生成相关接口。在文档末尾的"系统接口"之前添加一个新的章节：

```markdown
---

# 卡牌生成相关接口

## 14. 生成卡图

### 基本信息

- **接口名称**: 生成卡图
- **请求地址**: `/api/generate-card`
- **请求方法**: `POST`
- **功能描述**: 根据卡牌JSON数据生成卡图，返回base64编码的图片数据

### 请求参数

| 参数名       | 类型     | 必填 | 说明      |
|-----------|--------|----|---------|
| json_data | object | 是  | 卡牌数据JSON |

#### 卡牌数据格式 (json_data)

| 字段名          | 类型       | 必填 | 说明        | 示例值          |
|--------------|----------|----|-----------|--------------|
| type         | string   | 是  | 卡牌类型      | "支援卡"        |
| name         | string   | 是  | 卡牌名称      | "测试"          |
| id           | string   | 否  | 卡牌ID      | ""           |
| created_at   | string   | 否  | 创建时间      | ""           |
| version      | string   | 否  | 版本号       | "1.0"        |
| subtitle     | string   | 否  | 副标题       | "测试"          |
| class        | string   | 否  | 职阶        | "多职阶"        |
| subclass     | array    | 否  | 子职阶列表     | ["探求者", "流浪者"] |
| health       | integer  | 否  | 生命值       | 2            |
| horror       | integer  | 否  | 恐惧值       | 3            |
| slots        | string   | 否  | 装备栏位1     | "盟友"          |
| slots2       | string   | 否  | 装备栏位2     | "身体"          |
| level        | integer  | 否  | 等级        | 4            |
| cost         | integer  | 否  | 费用        | 6            |
| submit_icon  | array    | 否  | 提交图标列表    | ["战力", "战力"]  |
| traits       | array    | 否  | 特性列表      | ["测试"]       |
| body         | string   | 否  | 卡牌正文      | "测试测试【测试】测试" |
| flavor       | string   | 否  | 背景文本      | "测试测试测试"     |
| picture_path | string   | 否  | 卡牌图片路径    | "/path/to/image.png" |

### 请求示例

```bash
curl -X POST /api/generate-card \
  -H "Content-Type: application/json" \
  -d '{
    "json_data": {
      "type": "支援卡",
      "name": "测试",
      "id": "",
      "created_at": "",
      "version": "1.0",
      "subtitle": "测试",
      "class": "多职阶",
      "subclass": ["探求者", "流浪者"],
      "health": 2,
      "horror": 3,
      "slots": "盟友",
      "slots2": "身体", 
      "level": 4,
      "cost": 6,
      "submit_icon": ["战力", "战力"],
      "traits": ["测试"],
      "body": "测试测试【测试】测试",
      "flavor": "测试测试测试"
    }
  }'
```

### 响应格式

| 字段        | 类型     | 说明                           |
|-----------|--------|------------------------------|
| data      | object | 响应数据                         |
| data.image| string | base64编码的图片数据，包含data URL前缀 |

### 示例响应

```json
{
  "code": 0,
  "msg": "生成卡图成功",
  "data": {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

### 错误响应

| 错误码 | 说明           |
|-----|--------------|
| 4001| 请提供卡牌JSON数据  |
| 4002| 生成卡图失败       |
| 4003| 生成卡图失败（详细错误） |

## 15. 保存卡图

### 基本信息

- **接口名称**: 保存卡图
- **请求地址**: `/api/save-card`
- **请求方法**: `POST`
- **功能描述**: 根据卡牌JSON数据生成卡图并保存为图片文件

### 请求参数

| 参数名         | 类型     | 必填 | 说明                |
|-------------|--------|----|-------------------|
| json_data   | object | 是  | 卡牌数据JSON（格式同上）    |
| filename    | string | 是  | 保存的文件名（含扩展名）      |
| parent_path | string | 否  | 保存的父目录路径，默认为工作空间根目录 |

### 请求示例

```bash
curl -X POST /api/save-card \
  -H "Content-Type: application/json" \
  -d '{
    "json_data": {
      "type": "支援卡",
      "name": "测试卡牌",
      "subtitle": "测试",
      "class": "多职阶",
      "subclass": ["探求者"],
      "health": 2,
      "horror": 3,
      "level": 4,
      "cost": 6,
      "body": "这是一张测试卡牌",
      "flavor": "用于测试的卡牌"
    },
    "filename": "test-card.png",
    "parent_path": "/Users/username/Documents/MyProject/cards"
  }'
```

### 响应格式

成功时返回标准成功响应，无额外数据字段。

### 示例响应

```json
{
  "code": 0,
  "msg": "保存卡图成功",
  "data": null
}
```

### 错误响应

| 错误码 | 说明               |
|-----|--------------------|
| 4004| 请提供卡牌JSON数据和文件名    |
| 4005| 保存卡图失败           |
| 4006| 保存卡图失败（详细错误）     |

### 注意事项

1. **依赖检查**: 卡牌生成功能依赖 `create_card.py` 模块和相关字体、图片资源
2. **资源路径**: 系统会自动在工作空间中查找 `fonts` 和 `images` 目录作为资源路径
3. **图片格式**: 生成的卡图默认保存为PNG格式
4. **路径安全**: 保存路径必须在工作空间内，防止路径遍历攻击
5. **文件覆盖**: 如果目标文件已存在，将会被覆盖
6. **目录创建**: 如果父目录不存在，系统会自动创建

---
```

现在更新错误码说明部分，在原有错误码表格后添加：


| 错误码范围     | 分类     | 说明          |
|-----------|--------|-------------|
| 0         | 成功     | 操作成功        |
| 1001-1999 | 目录选择相关 | 目录选择操作相关错误  |
| 2001-2999 | 快速开始相关 | 最近目录管理相关错误  |
| 3001-3999 | 工作空间相关 | 工作空间操作相关错误  |
| 4001-4999 | 卡牌生成相关 | 卡牌生成和保存相关错误 |
| 9001-9999 | 系统错误   | HTTP状态码相关错误 |


以及详细错误码表格中添加：


| 错误码       | 说明                |
|-----------|-------------------|
| 4001      | 请提供卡牌JSON数据       |
| 4002      | 生成卡图失败            |
| 4003      | 生成卡图失败（详细错误信息）    |
| 4004      | 请提供卡牌JSON数据和文件名   |
| 4005      | 保存卡图失败            |
| 4006      | 保存卡图失败（详细错误信息）    |


这样就完整地添加了两个卡牌生成相关的API接口文档。