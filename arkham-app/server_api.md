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
| 4001-4999 | 卡牌生成相关 | 卡牌生成和保存相关错误 |
| 5001-5999 | 文件内容相关 | 图片和文件信息相关错误 |
| 6001-6999 | 配置管理相关 | 配置项和遭遇组相关错误 |
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
| 4001      | 请提供卡牌JSON数据       |
| 4002      | 生成卡图失败            |
| 4003      | 生成卡图失败（详细错误信息）    |
| 4004      | 请提供卡牌JSON数据和文件名   |
| 4005      | 保存卡图失败            |
| 4006      | 保存卡图失败（详细错误信息）    |
| 5001      | 请提供图片路径           |
| 5002      | 图片文件不存在或无法读取      |
| 5003      | 获取图片内容失败          |
| 5004      | 请提供文件路径           |
| 5005      | 文件不存在或无法访问        |
| 5006      | 获取文件信息失败          |
| 6001      | 获取配置失败            |
| 6002      | 请提供配置数据           |
| 6003      | 保存配置失败            |
| 6004      | 保存配置失败（详细错误信息）    |
| 6005      | 获取遭遇组列表失败         |
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

## 13. 获取图片内容

### 基本信息

- **接口名称**: 获取图片内容
- **请求地址**: `/api/image-content`
- **请求方法**: `GET`
- **功能描述**: 获取图片文件并转换为base64格式

### 请求参数

| 参数名  | 类型     | 必填 | 说明   |
|------|--------|----|------|
| path | string | 是  | 图片路径 |

### 请求示例

```bash
curl -X GET "/api/image-content?path=/path/to/image.png"
```

### 响应示例

```json
{
  "code": 0,
  "msg": "获取图片内容成功",
  "data": {
    "content": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

## 14. 获取文件信息

### 基本信息

- **接口名称**: 获取文件信息
- **请求地址**: `/api/file-info`
- **请求方法**: `GET`
- **功能描述**: 获取文件的详细信息

### 请求参数

| 参数名  | 类型     | 必填 | 说明   |
|------|--------|----|------|
| path | string | 是  | 文件路径 |

### 响应格式

| 字段                      | 类型      | 说明         |
|-------------------------|---------|------------|
| data.fileInfo.path      | string  | 文件绝对路径     |
| data.fileInfo.type      | string  | 文件类型       |
| data.fileInfo.is_file   | boolean | 是否为文件      |
| data.fileInfo.is_directory | boolean | 是否为目录      |
| data.fileInfo.is_image  | boolean | 是否为图片文件    |
| data.fileInfo.size      | integer | 文件大小（字节）   |
| data.fileInfo.modified  | integer | 修改时间戳      |
| data.fileInfo.modified_formatted | string | 格式化的修改时间 |

### 请求示例

```bash
curl -X GET "/api/file-info?path=/path/to/file.txt"
```

### 响应示例

```json
{
  "code": 0,
  "msg": "获取文件信息成功",
  "data": {
    "fileInfo": {
      "path": "/Users/username/Documents/MyProject/file.txt",
      "type": "text",
      "is_file": true,
      "is_directory": false,
      "is_image": false,
      "size": 1024,
      "modified": 1699123456,
      "modified_formatted": "2023-11-05 14:30:56"
    }
  }
}
```

---

# 配置管理相关接口

## 15. 获取配置项

### 基本信息

- **接口名称**: 获取配置项
- **请求地址**: `/api/config`
- **请求方法**: `GET`
- **功能描述**: 获取工作目录下config.json的配置内容

### 请求参数

无需传入参数

### 响应格式

| 字段        | 类型     | 说明    |
|-----------|--------|-------|
| data.config | object | 配置项对象 |

### 示例请求

```bash
curl -X GET /api/config
```

### 示例响应

```json
{
  "code": 0,
  "msg": "获取配置成功",
  "data": {
    "config": {
      "encounter_groups_dir": "encounters",
      "other_setting": "some_value"
    }
  }
}
```

## 16. 保存配置项

### 基本信息

- **接口名称**: 保存配置项
- **请求地址**: `/api/config`
- **请求方法**: `PUT`
- **功能描述**: 保存配置到工作目录下的config.json文件

### 请求参数

| 参数名    | 类型     | 必填 | 说明    |
|--------|--------|----|-------|
| config | object | 是  | 配置项对象 |

### 请求示例

```bash
curl -X PUT /api/config \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "encounter_groups_dir": "encounters",
      "other_setting": "new_value"
    }
  }'
```

### 示例响应

```json
{
  "code": 0,
  "msg": "保存配置成功",
  "data": null
}
```

## 17. 获取遭遇组列表

### 基本信息

- **接口名称**: 获取遭遇组列表
- **请求地址**: `/api/encounter-groups`
- **请求方法**: `GET`
- **功能描述**: 根据配置中的遭遇组目录，搜索所有png图片文件并返回名称列表

### 请求参数

无需传入参数

### 响应格式

| 字段                     | 类型    | 说明        |
|------------------------|-------|-----------|
| data.encounter_groups  | array | 遭遇组名称列表   |

### 示例请求

```bash
curl -X GET /api/encounter-groups
```

### 示例响应

```json
{
  "code": 0,
  "msg": "获取遭遇组列表成功",
  "data": {
    "encounter_groups": [
      "boss_encounter",
      "minion_encounter", 
      "special_encounter"
    ]
  }
}
```

### 注意事项

1. **配置依赖**: 需要先通过 `/api/config` 接口设置 `encounter_groups_dir` 配置项
2. **目录检查**: 系统会检查配置的目录是否存在
3. **文件过滤**: 只搜索 `.png` 扩展名的文件
4. **名称处理**: 返回的名称列表不包含文件扩展名
5. **排序**: 返回的列表按名称字母顺序排序

---

# 卡牌生成相关接口

## 18. 生成卡图

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

| 字段名           | 类型       | 必填 | 说明         | 示例值                 |
|---------------|----------|----|------------|---------------------|
| type          | string   | 是  | 卡牌类型       | "支援卡"               |
| name          | string   | 是  | 卡牌名称       | "测试"                 |
| id            | string   | 否  | 卡牌ID       | ""                  |
| created_at    | string   | 否  | 创建时间       | ""                  |
| version       | string   | 否  | 版本号        | "1.0"               |
| subtitle      | string   | 否  | 副标题        | "测试"                 |
| class         | string   | 否  | 职阶         | "多职阶"               |
| subclass      | array    | 否  | 子职阶列表      | ["探求者", "流浪者"]       |
| health        | integer  | 否  | 生命值        | 2                   |
| horror        | integer  | 否  | 恐惧值        | 3                   |
| slots         | string   | 否  | 装备栏位1      | "盟友"                 |
| slots2        | string   | 否  | 装备栏位2      | "身体"                 |
| level         | integer  | 否  | 等级         | 4                   |
| cost          | integer  | 否  | 费用         | 6                   |
| submit_icon   | array    | 否  | 提交图标列表     | ["战力", "战力"]         |
| traits        | array    | 否  | 特性列表       | ["测试"]               |
| body          | string   | 否  | 卡牌正文       | "测试测试【测试】测试"        |
| flavor        | string   | 否  | 背景文本       | "测试测试测试"            |
| picture_path  | string   | 否  | 卡牌图片路径     | "/path/to/image.png" |
| picture_base64| string   | 否  | base64图片数据 | "data:image/png;base64,..." |

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

## 19. 保存卡图

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

### 示例响应

```json
{
  "code": 0,
  "msg": "保存卡图成功",
  "data": null
}
```

### 注意事项

1. **依赖检查**: 卡牌生成功能依赖 `create_card.py` 模块和相关字体、图片资源
2. **资源路径**: 系统会自动在工作空间中查找 `fonts` 和 `images` 目录作为资源路径
3. **图片格式**: 生成的卡图默认保存为PNG格式
4. **路径安全**: 保存路径必须在工作空间内，防止路径遍历攻击
5. **文件覆盖**: 如果目标文件已存在，将会被覆盖
6. **目录创建**: 如果父目录不存在，系统会自动创建

---

# 系统接口

## 20. 服务状态接口

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

---

# 附录

## 支持的文件类型

| 扩展名       | 文件类型 | 说明    |
|-----------|------|-------|
| .card     | card | 卡牌文件  |
| .png      | image| 图片文件  |
| .jpg      | image| 图片文件  |
| .jpeg     | image| 图片文件  |
| .gif      | image| 图片文件  |
| .svg      | image| 图片文件  |
| .bmp      | image| 图片文件  |
| .webp     | image| 图片文件  |
| .tiff     | image| 图片文件  |
| .ico      | image| 图片文件  |
| .json     | config| 配置文件 |
| .yml      | config| 配置文件 |
| .yaml     | config| 配置文件 |
| .xml      | data | 数据文件  |
| .css      | style| 样式文件  |
| .txt      | text | 文本文件  |
| .md       | text | 文本文件  |
| 其他        | file | 普通文件  |

## 常见问题

### Q: 为什么选择目录对话框没有响应？
A: 检查是否有其他目录选择操作正在进行，系统同时只允许一个选择操作。

### Q: 如何设置遭遇组目录？
A: 使用 `/api/config` 接口设置 `encounter_groups_dir` 配置项，指定相对于工作目录的路径。

### Q: 卡牌生成失败怎么办？
A: 确保工作空间中存在 `fonts` 和 `images` 目录，并包含必要的字体和图片资源文件。

### Q: 文件路径安全性如何保证？
A: 所有文件操作都限制在当前工作空间目录内，防止路径遍历攻击。