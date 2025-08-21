import { HttpMethod, type ApiConfig } from './types';

// API基础配置
export const API_BASE_URL = '/';

// API接口端点配置
export const API_ENDPOINTS = {
  // 选择目录接口
  SELECT_DIRECTORY: {
    url: '/api/select-directory',
    method: HttpMethod.GET,
    timeout: 300000 // 300秒超时
  } as ApiConfig,

  // 获取服务状态接口
  GET_STATUS: {
    url: '/api/status',
    method: HttpMethod.GET,
    timeout: 5000 // 5秒超时
  } as ApiConfig,

  // 快速开始相关接口
  GET_RECENT_DIRECTORIES: {
    url: '/api/recent-directories',
    method: HttpMethod.GET,
    timeout: 5000
  } as ApiConfig,

  OPEN_WORKSPACE: {
    url: '/api/open-workspace',
    method: HttpMethod.POST,
    timeout: 10000
  } as ApiConfig,

  CLEAR_RECENT_DIRECTORIES: {
    url: '/api/recent-directories',
    method: HttpMethod.DELETE,
    timeout: 5000
  } as ApiConfig,

  REMOVE_RECENT_DIRECTORY: {
    url: '/api/recent-directories',
    method: HttpMethod.DELETE,
    timeout: 5000
  } as ApiConfig,

  // 工作空间相关接口
  GET_FILE_TREE: {
    url: '/api/file-tree',
    method: HttpMethod.GET,
    timeout: 10000
  } as ApiConfig,

  CREATE_DIRECTORY: {
    url: '/api/create-directory',
    method: HttpMethod.POST,
    timeout: 10000
  } as ApiConfig,

  CREATE_FILE: {
    url: '/api/create-file',
    method: HttpMethod.POST,
    timeout: 10000
  } as ApiConfig,

  RENAME_ITEM: {
    url: '/api/rename-item',
    method: HttpMethod.PUT,
    timeout: 10000
  } as ApiConfig,

  DELETE_ITEM: {
    url: '/api/delete-item',
    method: HttpMethod.DELETE,
    timeout: 10000
  } as ApiConfig,

  GET_FILE_CONTENT: {
    url: '/api/file-content',
    method: HttpMethod.GET,
    timeout: 10000
  } as ApiConfig,

  SAVE_FILE_CONTENT: {
    url: '/api/file-content',
    method: HttpMethod.PUT,
    timeout: 10000
  } as ApiConfig,

  // 图片和文件信息相关接口
  GET_IMAGE_CONTENT: {
    url: '/api/image-content',
    method: HttpMethod.GET,
    timeout: 15000 // 图片加载可能需要较长时间
  } as ApiConfig,

  GET_FILE_INFO: {
    url: '/api/file-info',
    method: HttpMethod.GET,
    timeout: 5000
  } as ApiConfig,

  // 卡牌生成相关接口
  GENERATE_CARD: {
    url: '/api/generate-card',
    method: HttpMethod.POST,
    timeout: 30000 // 30秒超时，卡牌生成可能需要较长时间
  } as ApiConfig,

  SAVE_CARD: {
    url: '/api/save-card',
    method: HttpMethod.POST,
    timeout: 30000 // 30秒超时
  } as ApiConfig,

  // 配置管理相关接口
  GET_CONFIG: {
    url: '/api/config',
    method: HttpMethod.GET,
    timeout: 5000
  } as ApiConfig,
  SAVE_CONFIG: {
    url: '/api/config',
    method: HttpMethod.PUT,
    timeout: 10000
  } as ApiConfig,
  GET_ENCOUNTER_GROUPS: {
    url: '/api/encounter-groups',
    method: HttpMethod.GET,
    timeout: 10000
  } as ApiConfig,
} as const;


// 导出API端点类型
export type ApiEndpoints = typeof API_ENDPOINTS;
export type ApiEndpointKey = keyof ApiEndpoints;
