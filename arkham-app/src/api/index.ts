// 在 index.ts 文件中添加服务的导出

// 现有导出...
export * from './types';
export * from './endpoints';
export * from './http-client';
export * from './directory-service';
export * from './workspace-service';
export * from './card-service';
export * from './config-service';
export * from './tts-export-service';
export * from './github-service'; // GitHub服务
export * from './image-host-service'; // 图床服务
export * from './content-package-service'; // 内容包服务
export * from './arkhamdb-service'; // ArkhamDB导入服务
export * from './language-config-service'; // 多语言配置服务

// 默认导出所有服务
export { default as DirectoryService } from './directory-service';
export { default as WorkspaceService } from './workspace-service';
export { default as CardService } from './card-service';
export { default as TtsScriptService } from './tts-script-service';
export { default as ConfigService } from './config-service';
export { default as httpClient } from './http-client';
export { default as TtsExportService } from './tts-export-service';
export { default as GitHubService } from './github-service'; // GitHub服务
export { default as ImageHostService } from './image-host-service'; // 图床服务
export { default as ContentPackageService } from './content-package-service'; // 内容包服务
export { default as ArkhamDBService } from './arkhamdb-service'; // ArkhamDB导入服务
export { default as LanguageConfigService } from './language-config-service'; // 多语言配置服务
