# Steam Cloud Upload Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为内容包上传流程新增 `Steam 云` 图床类型，通过现有本地 Flask 服务提供工作区导出图片的 HTTP URL，使用户无需配置第三方图床即可在 TTS 中完成 Steam 云上传。

**Architecture:** 后端在 `bin/image_uploader.py` 中新增 `SteamCloudUploader`，仅返回基于工作区相对路径的本地 HTTP URL；`server.py` 新增受控静态图片路由并扩展图床上传/检查接口支持 `steam`。前端在 `UniversalUploadDialog.vue` 中增加 `Steam 云` 选项和教程展示，复用现有上传逻辑。

**Tech Stack:** Python 3、Flask、TypeScript、Vue 3、unittest

---

### Task 1: 为后端图床工厂新增 Steam 上传器

**Files:**
- Modify: `bin/image_uploader.py`
- Test: `tests/test_image_uploader_public_id.py`

**Step 1: Write the failing test**

新增测试，验证：

- `create_uploader({ image_host: "steam" })` 返回 Steam 上传器
- 相同文件名但不同目录的图片得到不同 URL

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_image_uploader_public_id.py`
Expected: FAIL，提示 `steam` 类型不支持或 URL 唯一性不满足。

**Step 3: Write minimal implementation**

在 `bin/image_uploader.py` 中：

- 新增 `SteamCloudUploader`
- 新增稳定 URL 构造函数
- 更新 `create_uploader()` 支持 `steam`

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_image_uploader_public_id.py`
Expected: PASS

### Task 2: 为 Flask 增加 Steam 静态图片路由和接口支持

**Files:**
- Modify: `server.py`
- Create: `tests/test_steam_cloud_routes.py`

**Step 1: Write the failing test**

新增测试，验证：

- `/api/image-host/upload` 接受 `host_type = steam`
- `/api/image-host/check` 接受 `host_type = steam`
- `/api/image-host/steam/<path>` 只允许访问 `.cards/.banner/.encounters`

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_steam_cloud_routes.py`
Expected: FAIL

**Step 3: Write minimal implementation**

在 `server.py` 中：

- 放宽 host_type 校验列表，加入 `steam`
- `steam` 不要求 Cloudinary/ImgBB 配置
- 新增 Steam 路由，受工作区路径校验保护

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_steam_cloud_routes.py`
Expected: PASS

### Task 3: 前端 API 与上传弹窗支持 Steam 云

**Files:**
- Modify: `arkham-app/src/api/types.ts`
- Modify: `arkham-app/src/api/image-host-service.ts`
- Modify: `arkham-app/src/components/UniversalUploadDialog.vue`
- Modify: `arkham-app/src/locales/zh/contentPackage.ts`
- Modify: `arkham-app/src/locales/en/contentPackage.ts`

**Step 1: Add failing UI-level assertions**

如果当前仓库没有前端测试框架，则至少通过组件逻辑可验证点确保：

- `steam` 出现在图床选项中
- `steam` 不要求配置
- `steam` 模式显示教程区域

**Step 2: Implement minimal frontend changes**

- `ImageHostType` 增加 `STEAM`
- 上传弹窗新增 `Steam 云` 选项
- `validateConfig()` 对 `steam` 返回 true
- 增加教程文案和两张配图展示

**Step 3: Verify**

Run: `npm --prefix arkham-app run build`
Expected: 构建通过

### Task 4: 全量相关回归

**Files:**
- Modify: `bin/image_uploader.py`
- Modify: `server.py`
- Modify: `arkham-app/src/...`
- Test: `tests/test_image_uploader_public_id.py`
- Test: `tests/test_steam_cloud_routes.py`
- Test: `tests/test_workspace_path_normalization.py`
- Test: `tests/test_large_player_card_type_labels.py`
- Test: `tests/test_card_numbering.py`

**Step 1: Run backend tests**

Run: `python3 -m unittest tests/test_image_uploader_public_id.py tests/test_steam_cloud_routes.py tests/test_workspace_path_normalization.py tests/test_large_player_card_type_labels.py tests/test_card_numbering.py`

Expected: PASS

**Step 2: Run frontend build**

Run: `npm --prefix arkham-app run build`

Expected: PASS

**Step 3: Commit**

```bash
git add bin/image_uploader.py server.py arkham-app/src/api/types.ts arkham-app/src/api/image-host-service.ts arkham-app/src/components/UniversalUploadDialog.vue arkham-app/src/locales/zh/contentPackage.ts arkham-app/src/locales/en/contentPackage.ts tests/test_image_uploader_public_id.py tests/test_steam_cloud_routes.py docs/plans/2026-03-15-steam-cloud-upload-design.md docs/plans/2026-03-15-steam-cloud-upload.md
git commit -m "feat: 支持 Steam 云上传方式"
```
