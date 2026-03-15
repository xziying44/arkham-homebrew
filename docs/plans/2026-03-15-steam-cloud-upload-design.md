# Steam 云上传设计文档

## 目标

为现有内容包上传流程新增一个与 `Cloudinary`、`ImgBB` 同级的 `Steam 云` 上传方式。

它的本质不是调用 Steam API，而是：

1. 本地先导出图片；
2. 应用提供一个可被 TTS 访问的本地 HTTP 地址；
3. 导出的 JSON 使用这些本地 HTTP URL；
4. 用户在 TTS 中加载物品后，通过“上传所有载入文件”写入 Steam 云。

## 用户需求

- `Steam 云` 需要出现在前端图床选择中，和 `Cloudinary` 同级。
- 不需要用户填写任何配置。
- 封面、卡牌、遭遇组都要支持这个方式。
- 页面中要直接提供教程，使用 `arkham-app/src/assets/steam-cloud/01.png` 和 `02.png`。
- 必须避免不同目录同名文件在 URL 上互相覆盖。

## 参考实现

参考仓库：`/Volumes/RepoVault/诡镇简中包/TranslationBag`

其原理是 `LocalHostUploader` + 本地 HTTP 静态文件服务。

但当前项目已经存在本地 Flask 服务，因此不需要额外再起一套 FastAPI/uvicorn。直接复用现有 Flask 服务，新增一个受控静态资源路由即可。

## 设计决策

### 1. 图床类型

新增 `steam` 图床类型：

- 后端上传器：`SteamCloudUploader`
- 前端枚举：`ImageHostType.STEAM`
- 前端 UI：显示为 `Steam 云`

### 2. URL 方案

不使用简单文件名，而是使用工作区相对路径构造 URL，例如：

`http://127.0.0.1:5000/api/image-host/steam/.cards/白金/asset_front.jpg`

这样天然避免不同子目录中同名文件互相覆盖。

### 3. 后端服务

新增 Flask 路由：

`GET /api/image-host/steam/<path:relative_path>`

规则：

- 仅允许访问当前工作区内的导出目录：
  - `.cards/`
  - `.banner/`
  - `.encounters/`
- 必须通过现有工作区路径校验，禁止路径穿越。
- 返回真实图片文件内容，由 TTS 通过本地 HTTP 拉取。

### 4. 上传语义

`SteamCloudUploader.upload_file(...)` 不做真实上传，只做：

- 验证路径位于工作区中；
- 生成 `steam` 本地 HTTP URL；
- 返回该 URL。

`check_file_exists(...)` 对 `steam` 返回基于本地文件存在性的结果即可。

### 5. 前端交互

在 `UniversalUploadDialog.vue` 中：

- 图床选项新增 `Steam 云`
- 不显示配置表单
- 复用现有上传逻辑
- 在 `selectedHost === 'steam'` 时展示操作教程和两张配图

### 6. 教程内容

教程说明放在上传弹窗页面中，内容包括：

1. 使用 Steam 云方式导出 JSON；
2. 将 JSON 放到 TTS 保存对象目录；
3. 进入 TTS 空桌加载物品；
4. 打开 `MOD -> Steam 云存储管理`；
5. 创建分类文件夹；
6. 点击“上传所有载入文件”；
7. 等待绿色成功提示；
8. 重新右键保存物品到你的物品，避免关闭游戏后丢失。

## 涉及文件

后端：

- `bin/image_uploader.py`
- `server.py`

前端：

- `arkham-app/src/api/types.ts`
- `arkham-app/src/api/image-host-service.ts`
- `arkham-app/src/components/UniversalUploadDialog.vue`
- `arkham-app/src/locales/zh/contentPackage.ts`
- `arkham-app/src/locales/en/contentPackage.ts`

测试：

- `tests/test_image_uploader_public_id.py`（扩展或新增邻近测试）
- 新增 Steam 上传器/路由测试

## 风险

### 1. 本地地址可达性

当前应用默认监听 `127.0.0.1:5000` 或 macOS 下 `127.0.0.1:5091`。TTS 在本机运行时可访问，但 URL 不能写死，应从当前请求来源推导，优先保持与前端当前 host 一致。

### 2. 路径安全

必须保证 Steam 静态路由只能访问工作区允许的导出目录，不能访问任意文件。

### 3. 同名文件冲突

必须使用相对路径生成 URL，不能只用 basename。

## 测试策略

最少覆盖：

- 同名不同目录图片生成不同 Steam URL
- `steam` 图床类型可被创建
- Steam 路由拒绝非法路径
- `steam` 模式下前端无需配置即可上传
- `steam` 模式下教程区显示
