// 在 index.ts 文件中添加 GitHub 服务的导出

// 现有导出...
export * from './types';
export * from './endpoints';
export * from './http-client';
export * from './directory-service';
export * from './workspace-service';
export * from './card-service';
export * from './config-service';
export * from './tts-export-service';
export * from './github-service'; // 新增

// 默认导出所有服务
export { default as DirectoryService } from './directory-service';
export { default as WorkspaceService } from './workspace-service';
export { default as CardService } from './card-service';
export { default as ConfigService } from './config-service';
export { default as AIService } from './ai-service';
export { default as httpClient } from './http-client';
export { default as TtsExportService } from './tts-export-service';
export { default as GitHubService } from './github-service'; // 新增
