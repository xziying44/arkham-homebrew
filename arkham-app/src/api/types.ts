// src/api/types.ts
// API响应基础类型
export interface BaseResponse<T = any> {
  code: number;
  msg: string;
  data: T | null;
}

// 错误码枚举
export enum ErrorCode {
  SUCCESS = 0,
  // 目录选择相关错误
  SELECTING_IN_PROGRESS = 1001,
  TIMEOUT = 1002,
  USER_CANCELLED = 1003,
  SELECT_ERROR = 1004,
  NO_RESULT = 1005,
  SERVER_ERROR = 1006,
  WORKSPACE_CREATE_FAILED = 1007,
  // 最近目录管理相关错误 (2001-2008)
  RECENT_DIRECTORY_ERROR = 2001,
  // 工作空间相关错误
  NO_WORKSPACE = 3001,
  WORKSPACE_ERROR_START = 3002,
  WORKSPACE_ERROR_END = 3020,
  // 卡牌生成相关错误 (4001-4006)
  CARD_MISSING_DATA = 4001,
  CARD_GENERATE_ERROR = 4002,
  CARD_GENERATE_DETAILED_ERROR = 4003,
  CARD_MISSING_DATA_AND_FILENAME = 4004,
  CARD_SAVE_ERROR = 4005,
  CARD_SAVE_DETAILED_ERROR = 4006,
  // 图片和文件信息相关错误 (5001-5006)
  IMAGE_MISSING_PATH = 5001,
  IMAGE_NOT_FOUND = 5002,
  IMAGE_READ_ERROR = 5003,
  FILE_INFO_MISSING_PATH = 5004,
  FILE_INFO_NOT_FOUND = 5005,
  FILE_INFO_READ_ERROR = 5006,
  // 系统错误
  NOT_FOUND = 9001,
  METHOD_NOT_ALLOWED = 9002,
  INTERNAL_ERROR = 9003
}

// 目录选择响应数据类型
export interface DirectorySelectData {
  directory: string;
}

// 最近目录项类型
export interface RecentDirectoryItem {
  path: string;
  name: string;
  timestamp: number;
  formatted_time: string;
}

// 最近目录列表响应数据类型
export interface RecentDirectoriesData {
  directories: RecentDirectoryItem[];
}

// 文件树节点类型
export interface TreeOption {
  label: string;
  key: string;
  type: 'directory' | 'folder' | 'card-category' | 'image-category' | 'other-category' | 'card' | 'image' | 'config' | 'text' | 'style' | 'data' | 'workspace' | 'error';
  path?: string;
  children?: TreeOption[];
}

// 文件树响应数据类型
export interface FileTreeData {
  fileTree: TreeOption;
}

// 文件内容响应数据类型
export interface FileContentData {
  content: string;
}

// 图片内容响应数据类型
export interface ImageContentData {
  content: string; // base64编码的图片数据，包含data URL前缀
}

// 文件信息类型
export interface FileInfo {
  path: string;
  type: string;
  is_file: boolean;
  is_directory: boolean;
  is_image: boolean;
  size: number;
  modified: number;
  modified_formatted: string;
}

// 文件信息响应数据类型
export interface FileInfoData {
  fileInfo: FileInfo;
}

// 服务状态响应数据类型
export interface ServiceStatusData {
  service: string;
  version: string;
  is_selecting: boolean;
  has_workspace: boolean;
  workspace_path: string | null;
}

// 卡牌数据类型
export interface CardData {
  type?: string;
  name?: string;
  id?: string;
  created_at?: string;
  version?: string;
  subtitle?: string;
  class?: string;
  subclass?: string[];
  health?: number;
  horror?: number;
  slots?: string;
  slots2?: string;
  level?: number;
  cost?: number;
  submit_icon?: string[];
  traits?: string[];
  body?: string;
  flavor?: string;
  picture_path?: string;
}

// 生成卡图请求数据类型
export interface GenerateCardRequest {
  json_data: CardData;
}

// 保存卡图请求数据类型
export interface SaveCardRequest {
  json_data: CardData;
  filename: string;
  parent_path?: string;
}

// 生成卡图响应数据类型
export interface GenerateCardData {
  image: string; // base64编码的图片数据，包含data URL前缀
}

// 请求参数类型
export interface OpenWorkspaceRequest {
  directory: string;
}

export interface CreateDirectoryRequest {
  name: string;
  parent_path?: string;
}

export interface CreateFileRequest {
  name: string;
  content?: string;
  parent_path?: string;
}

export interface RenameItemRequest {
  old_path: string;
  new_name: string;
}

export interface DeleteItemRequest {
  path: string;
}

export interface FileContentRequest {
  path: string;
  content?: string; // 用于保存文件时
}

// API响应类型
export type DirectorySelectResponse = BaseResponse<DirectorySelectData>;
export type RecentDirectoriesResponse = BaseResponse<RecentDirectoriesData>;
export type FileTreeResponse = BaseResponse<FileTreeData>;
export type FileContentResponse = BaseResponse<FileContentData>;
export type ImageContentResponse = BaseResponse<ImageContentData>;
export type FileInfoResponse = BaseResponse<FileInfoData>;
export type ServiceStatusResponse = BaseResponse<ServiceStatusData>;
export type GenerateCardResponse = BaseResponse<GenerateCardData>;
export type SaveCardResponse = BaseResponse<null>;
export type BasicResponse = BaseResponse<null>;

// HTTP方法枚举
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE'
}

// API接口配置类型
export interface ApiConfig {
  url: string;
  method: HttpMethod;
  timeout?: number;
}
