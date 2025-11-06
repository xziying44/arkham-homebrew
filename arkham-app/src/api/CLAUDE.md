[根目录](../../../CLAUDE.md) > [arkham-app](../../) > [src](../) > **api**

## 变更记录 (Changelog)

- 2025-11-06: 首次生成 API 服务层文档（架构、API 参考、集成模式、错误处理）

## 模块职责与架构概览

本目录提供前端与后端通信的“服务层”，以 TypeScript 类封装所有 REST API 调用：

- 分层组成
  - `types.ts`: 统一的请求/响应与业务类型定义
  - `endpoints.ts`: 所有后端端点与超时配置常量
  - `http-client.ts`: 基于 Axios 的 HTTP 客户端与统一错误处理（`ApiError`）
  - 各服务模块：将具体业务 API 封装为方法（目录/工作区/卡牌/配置/TTS 导出/GitHub/图床/ArkhamDB 导入）
  - `index.ts`: 汇总导出入口（统一从一个模块导入各服务）

- 统一约定
  - 所有请求走 `httpClient`，统一拦截器、超时与错误映射
  - 端点与方法、超时通过 `API_ENDPOINTS` 管理，避免硬编码
  - 公开类多提供“便捷方法解构导出”，便于按需导入使用

- 返回值与包装
  - HTTP 层返回形如 `BaseResponse<T> { code, msg, data }`
  - 业务方法通常返回 `data`（已解包）
  - 注意：部分实现存在返回层级不一致（见“错误处理与返回约定”中的“已知偏差”）

## 端点与配置

- 基础 URL
  - `API_BASE_URL = '/'`（见 `endpoints.ts:4`）

- 端点集中定义（节选）
  - 目录/工作区：`/api/select-directory`, `/api/status`, `/api/file-tree`, `/api/create-file`, `/api/file-content`, ...
  - 卡牌：`/api/generate-card`, `/api/save-card`, `/api/export-card`
  - 配置：`/api/config`, `/api/encounter-groups`
  - TTS：`/api/open-directory`, `/api/export-deck-image`, `/api/export-deck-pdf`, `/api/export-tts`
  - GitHub 图床：`/api/github/login`, `/api/github/repositories`, `/api/github/upload`, `/api/github/status`
  - 通用图床：`/api/image-host/upload`, `/api/image-host/check`

- 超时策略
  - 普通查询 5–10s，列表/树形 10–60s，生成/导出 30–120s，TTS/上传等可能 60s 以上
  - 具体见 `endpoints.ts` 中对应 `timeout`

## 公共 API 参考（完整方法签名）

以下仅列出“服务层公开方法”签名与参数说明（按文件分组）。返回类型为声明的类型；部分实现存在返回层级不一致，已在文末“已知偏差”注明。

1) directory-service.ts

```ts
class DirectoryService {
  static selectDirectory(): Promise<DirectorySelectData | null>;
  static getRecentDirectories(): Promise<RecentDirectoriesData>;
  static openWorkspace(directory: string): Promise<void>;
  static clearRecentDirectories(): Promise<void>;
  static removeRecentDirectory(directoryPath: string): Promise<void>;
  static getServiceStatus(): Promise<ServiceStatusData>;
  static isServiceAvailable(): Promise<boolean>;
  static isSelecting(): Promise<boolean>;
  static hasWorkspace(): Promise<boolean>;
  static getCurrentWorkspacePath(): Promise<string | null>;
}
// 便捷解构导出：selectDirectory, getRecentDirectories, openWorkspace, ...
```

- 参数说明
  - `directory`: 要打开的工作目录路径（字符串）
  - `directoryPath`: 最近目录中要移除的路径

2) workspace-service.ts

```ts
class WorkspaceService {
  static getFileTree(includeHidden?: boolean): Promise<FileTreeData>;
  static createDirectory(name: string, parentPath?: string): Promise<void>;
  static createFile(name: string, content?: string, parentPath?: string): Promise<void>;
  static renameItem(oldPath: string, newName: string): Promise<void>;
  static deleteItem(path: string): Promise<void>;
  static getFileContent(path: string): Promise<string>;
  static getImageContent(path: string): Promise<string>; // base64 with data URL
  static getFileInfo(path: string): Promise<FileInfo>;
  static saveFileContent(path: string, content: string): Promise<void>;
}
// 便捷解构导出：getFileTree, createDirectory, createFile, ...
```

- 参数说明
  - `includeHidden`: 是否包含隐藏文件（默认 false）
  - `name/content/parentPath`: 文件或目录创建参数
  - `oldPath/newName`: 重命名参数
  - `path`: 文件路径

3) card-service.ts

```ts
class CardService {
  static generateCard(cardData: CardData): Promise<any>; // 实际为 { image: string }
  static saveCard(cardData: CardData, filename: string, parentPath?: string): Promise<void>;
  static saveCardEnhanced(
    cardData: CardData,
    filename: string,
    options?: { parentPath?: string; format?: 'PNG' | 'JPG'; quality?: number; rotateLandscape?: boolean }
  ): Promise<string[]>; // 保存的文件相对路径列表
  static generateAndSaveCard(
    cardData: CardData,
    filename: string,
    parentPath?: string
  ): Promise<{ image: string }>;
  static validateCardData(cardData: CardData): { isValid: boolean; errors: string[] };
  static createDefaultCardData(type?: string): CardData;
}
// 便捷解构导出：generateCard, saveCard, saveCardEnhanced, ...
```

- 参数说明
  - `cardData`: 卡牌 JSON 数据（见 `types.ts` 中 `CardData`）
  - `filename`: 文件名（`saveCard` 含扩展名；`saveCardEnhanced` 不含扩展名）
  - `options`: 导出格式、质量、是否旋转横图等

4) config-service.ts

```ts
class ConfigService {
  static getConfig(): Promise<ConfigData>;
  static saveConfig(config: ConfigData): Promise<void>;
  static getEncounterGroups(): Promise<string[]>;
  static updateConfigItem(key: string, value: any): Promise<void>;
  static getConfigItem<T = any>(key: string, defaultValue?: T): Promise<T>;
  static setEncounterGroupsDirectory(directory: string): Promise<void>;
  static getEncounterGroupsDirectory(): Promise<string | null>;
  static validateConfig(config: ConfigData): { isValid: boolean; errors: string[]; warnings: string[] };
  static createDefaultConfig(): ConfigData;
}
```

- 参数说明
  - `config`: 配置对象（`encounter_groups_dir` 等自定义键）
  - `key/value`: 单项更新/读取参数

5) tts-export-service.ts

```ts
class TtsExportService {
  static openDirectory(directoryPath: string): Promise<void>;
  static exportDeckImage(deckName: string, format?: 'JPG' | 'PNG', quality?: number): Promise<void>;
  static exportDeckPdf(deckName: string, pdfFilename?: string): Promise<ExportDeckPdfData>;
  static exportTtsItem(deckName: string, faceUrl: string, backUrl: string): Promise<void>;
  static exportCard(
    cardPath: string,
    exportFilename: string,
    exportParams: ExportCardParams,
    paramsHash: string
  ): Promise<void>;
}
// 便捷解构导出：openDirectory, exportDeckImage, exportDeckPdf, exportTtsItem, exportCard
```

- 参数说明
  - `deckName`: 牌库名（相对 DeckBuilder 文件夹）
  - `format/quality`: 图片导出格式与质量
  - `pdfFilename`: 自定义 PDF 文件名（可选）
  - `cardPath/exportFilename/exportParams/paramsHash`: 单卡导出参数

6) image-host-service.ts

```ts
class ImageHostService {
  static uploadImage(data: ImageHostUploadRequest): Promise<ImageHostUploadResponse>;
  static checkImageExists(data: ImageHostCheckRequest): Promise<ImageHostCheckResponse>;
  static uploadToCloudinary(imagePath: string, onlineName?: string): Promise<ImageHostUploadResponse>;
  static uploadToImgBB(imagePath: string, onlineName?: string): Promise<ImageHostUploadResponse>;
  static checkCloudinaryImage(onlineName: string): Promise<ImageHostCheckResponse>;
  static checkImgBBImage(onlineName: string): Promise<ImageHostCheckResponse>;
  static smartUpload(imagePath: string, hostType: ImageHostType, onlineName?: string): Promise<ImageHostUploadResponse>;
}
```

- 参数说明
  - `imagePath`: 本地图片路径（相对工作区）
  - `onlineName`: 线上文件名（可选，覆盖/命名控制）
  - `hostType`: 图床类型（`cloudinary` | `imgbb` | `local`）

7) github-service.ts

```ts
class GitHubService {
  static login(token: string): Promise<GitHubLoginData>;
  static getRepositories(): Promise<GitHubRepository[]>;
  static uploadImage(imagePath: string): Promise<GitHubUploadData>;
  static getStatus(): Promise<GitHubStatusData>;
  static isLoggedIn(): Promise<boolean>;
  static getSupportedImageFormats(): string[];
  static isSupportedImageFormat(filename: string): boolean;
}
// 便捷解构导出：login, getRepositories, uploadImage, ...
```

- 参数说明
  - `token`: GitHub Personal Access Token
  - `imagePath`: 图片文件的相对路径

8) arkhamdb-service.ts

```ts
class ArkhamDBService {
  static importContentPack(req: ArkhamDBImportRequest): Promise<ArkhamDBImportResponse>;
  static getImportLogs(): Promise<ArkhamDBLogsResponse>;
  static validateContentPack(req: ArkhamDBValidateRequest): Promise<ArkhamDBValidateResponse>;
  static validateMultipleContentPacks(reqs: ArkhamDBValidateRequest[]): Promise<ArkhamDBValidateResponse[]>;
  static hasImportRecords(): Promise<boolean>;
}
```

9) http-client.ts（基础设施）

```ts
class HttpClient {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<BaseResponse<T>>>;
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<BaseResponse<T>>>;
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<BaseResponse<T>>>;
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<BaseResponse<T>>>;
  request<T>(config: AxiosRequestConfig): Promise<AxiosResponse<BaseResponse<T>>>;
  setBaseURL(baseURL: string): void;
  setTimeout(timeout: number): void;
  setHeader(key: string, value: string): void;
}
export class ApiError extends Error { code: number; originalError?: any }
export const httpClient = new HttpClient();
```

## 集成模式（Integration Patterns）

- 统一导入
  - 推荐从 `src/api/index.ts` 进行按需导入：
    ```ts
    import { DirectoryService, generateCard, TtsExportService, ImageHostService } from '@/api';
    ```

- 典型工作流示例
  - 打开工作区 → 文件树 → 编辑/保存
    ```ts
    const dir = await DirectoryService.selectDirectory();
    if (dir) await DirectoryService.openWorkspace(dir.directory);
    const tree = await WorkspaceService.getFileTree();
    await WorkspaceService.saveFileContent('a.card', JSON.stringify(card));
    ```
  - 生成并保存卡图
    ```ts
    const { image } = await CardService.generateAndSaveCard(cardData, 'a.jpg', 'cards');
    ```
  - 导出（TTS / PDF / 单卡）
    ```ts
    await TtsExportService.exportTtsItem('deck1', faceUrl, backUrl);
    const pdf = await TtsExportService.exportDeckPdf('deck1', 'deck1.pdf');
    await TtsExportService.exportCard('d/a.card', 'a-export', { format: 'JPG', quality: 95 }, hash);
    ```
  - 图床与 GitHub
    ```ts
    const up1 = await ImageHostService.uploadToCloudinary('images/a.jpg', 'a-online');
    const ok  = await GitHubService.isLoggedIn();
    if (!ok) await GitHubService.login('<PAT>');
    const gh  = await GitHubService.uploadImage('images/a.jpg');
    ```

- 约定与建议
  - 所有方法为 `async`，建议统一 `try/catch` 捕获 `ApiError`
  - 需要长时任务（导出/上传）请关注超时设置并提供 UI 进度反馈
  - 依赖配置项（如遭遇组目录、图床配置）可通过 `ConfigService` 管理

## 错误处理与返回约定

- 拦截器与错误映射（`http-client.ts:22` 起）
  - 业务失败：当 `BaseResponse.code !== 0` 时抛出 `ApiError(code, msg, data)`
  - HTTP 错误：根据 `status` 映射为相应 `ErrorCode`（404→NOT_FOUND 等），并抛出 `ApiError`
  - 网络错误：抛出 `ApiError(SERVER_ERROR, '网络连接失败，请检查服务是否启动')`

- 统一返回包装
  - 标准响应：`AxiosResponse<BaseResponse<T>>`，业务方法通常返回 `T`
  - 错误处理：请在调用处统一捕获并展示 `error.message` 与必要的引导

- 已知偏差（实现与签名不完全一致）
  - `github-service.ts`: 返回使用了 `response.data`（BaseResponse），声明为解包后的 `T`（如 `GitHubLoginData`）（参见 `github-service.ts:18, 39`）
  - `content-package-service.ts`: 若干方法直接返回了 `response`，并在其上访问 `logs`；另一些使用了解包后的 `data`（参见 `content-package-service.ts` 多处）
  - `tts-export-service.ts`: `exportDeckPdf` 返回 `response`，签名为 `ExportDeckPdfData`（见 `tts-export-service.ts:53` 附近）
  - 集成时建议以签名为准，必要时在调用处做精简封装以统一返回层级

