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
  INTERNAL_ERROR = 9003,
  // 配置管理相关错误 (6001-6999)
  CONFIG_GET_ERROR = 6001,
  CONFIG_MISSING_DATA = 6002,
  CONFIG_SAVE_ERROR = 6003,
  CONFIG_SAVE_DETAILED_ERROR = 6004,
  ENCOUNTER_GROUPS_ERROR = 6005,
  // OpenAI生成相关错误 (7001-7999)
  OPENAI_MISSING_CONTENT = 7001,
  OPENAI_PROMPT_FILE_ERROR = 7002,
  OPENAI_API_KEY_MISSING = 7003,
  OPENAI_CLIENT_ERROR = 7004,
  OPENAI_GENERATE_FAILED = 7005,
  OPENAI_JSON_TEXT_MISSING = 7006,
  OPENAI_JSON_FORMAT_ERROR = 7007,
  OPENAI_AI_ERROR = 7008,
  OPENAI_MISSING_REQUIRED_FIELDS = 7009,
  OPENAI_PARSE_FAILED = 7010,
  OPENAI_NONSTREAM_MISSING_CONTENT = 7011,
  OPENAI_NONSTREAM_PROMPT_FILE_ERROR = 7012,
  OPENAI_NONSTREAM_API_KEY_MISSING = 7013,
  OPENAI_NONSTREAM_CLIENT_ERROR = 7014,
  OPENAI_API_CALL_FAILED = 7015,
  OPENAI_PARSE_AI_JSON_FAILED = 7016,
  OPENAI_NONSTREAM_AI_ERROR = 7017,
  OPENAI_GENERATED_JSON_MISSING_FIELDS = 7018,
  OPENAI_GENERATE_AND_PARSE_FAILED = 7019,
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

  // 新增字段 - 卡片基本信息
  illustrator?: string;        // 插画作者
  encounter_group?: string;    // 遭遇组
  encounter_sequence?: string; // 遭遇组序号
  card_sequence?: string;      // 卡牌序号
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

// 在 types.ts 文件末尾添加以下类型定义

// 配置项对象类型
export interface ConfigData {
  encounter_groups_dir?: string;
  other_setting?: string;
  [key: string]: any; // 允许其他配置项
}

// 获取配置响应数据类型
export interface GetConfigData {
  config: ConfigData;
}

// 保存配置请求数据类型
export interface SaveConfigRequest {
  config: ConfigData;
}

// 遭遇组列表响应数据类型
export interface EncounterGroupsData {
  encounter_groups: string[];
}

// API响应类型
export type GetConfigResponse = BaseResponse<GetConfigData>;
export type SaveConfigResponse = BaseResponse<null>;
export type EncounterGroupsResponse = BaseResponse<EncounterGroupsData>;


// OpenAI卡牌生成相关类型定义
// 流式生成卡牌JSON信息请求类型
export interface GenerateCardInfoStreamRequest {
  content: string;
}
// 流式数据块类型
export interface StreamDataChunk {
  content?: string;
  done?: boolean;
  error?: string;
}
// 解析卡牌JSON请求类型
export interface ParseCardJsonRequest {
  json_text: string;
}
// 解析卡牌JSON响应数据类型
export interface ParseCardJsonData {
  card_json: CardData;
}
// 生成并解析卡牌请求类型
export interface GenerateAndParseCardRequest {
  content: string;
}
// 生成并解析卡牌响应数据类型
export interface GenerateAndParseCardData {
  card_json: CardData;
  raw_response: string;
}
// OpenAI相关API响应类型
export type ParseCardJsonResponse = BaseResponse<ParseCardJsonData>;
export type GenerateAndParseCardResponse = BaseResponse<GenerateAndParseCardData>;


// TTS导出相关类型定义

// 在资源管理器中打开目录请求类型
export interface OpenDirectoryRequest {
  directory_path: string;
}

// 导出牌库图片请求类型
export interface ExportDeckImageRequest {
  deck_name: string;
  format?: 'JPG' | 'PNG';
  quality?: number;
}

// 牌库卡片项类型
export interface DeckCardItem {
  index: number;
  type: 'image' | 'card' | 'cardback';
  path: string;
}

// 牌库JSON数据类型
export interface DeckData {
  name: string;
  width: number;
  height: number;
  frontCards: DeckCardItem[];
  backCards: DeckCardItem[];
}

// TTS导出相关错误码扩展
export enum TtsExportErrorCode {
  // 目录操作相关错误码 (9001-9099)
  DIRECTORY_PATH_MISSING = 9001,
  DIRECTORY_OPEN_FAILED = 9002,
  DIRECTORY_SYSTEM_ERROR = 9003,
  WORKSPACE_OPEN_FAILED = 9004,
  WORKSPACE_SYSTEM_ERROR = 9005,
  FILE_PATH_MISSING = 9006,
  FILE_LOCATION_OPEN_FAILED = 9007,
  FILE_LOCATION_SYSTEM_ERROR = 9008,

  // 牌库导出相关错误码 (8001-8099)
  DECK_NAME_MISSING = 8001,
  EXPORT_FORMAT_INVALID = 8002,
  QUALITY_INVALID = 8003,
  DECK_EXPORT_FAILED = 8004,
  DECK_EXPORT_SYSTEM_ERROR = 8005,
}

// API响应类型
export type OpenDirectoryResponse = BaseResponse<null>;
export type ExportDeckImageResponse = BaseResponse<null>;



// GitHub 相关错误码
export enum GitHubErrorCode {
  // GitHub相关错误码 (10001-10099)
  GITHUB_TOKEN_MISSING = 10001,
  GITHUB_LOGIN_FAILED = 10002,
  GITHUB_LOGIN_SYSTEM_ERROR = 10003,
  GITHUB_TOKEN_NOT_CONFIGURED = 10004,
  GITHUB_REPOSITORIES_FETCH_FAILED = 10005,
  GITHUB_REPOSITORIES_SYSTEM_ERROR = 10006,
  GITHUB_IMAGE_PATH_MISSING = 10007,
  GITHUB_INSTANCE_ERROR = 10008,
  GITHUB_REPO_NOT_CONFIGURED = 10009,
  GITHUB_IMAGE_PATH_INVALID = 10010,
  GITHUB_UPLOAD_FAILED = 10011,
  GITHUB_UPLOAD_SYSTEM_ERROR = 10012,
  GITHUB_STATUS_SYSTEM_ERROR = 10013,
}
// GitHub 登录请求类型
export interface GitHubLoginRequest {
  token: string;
}
// GitHub 登录响应数据类型
export interface GitHubLoginData {
  username: string;
}
// GitHub 仓库信息类型
export interface GitHubRepository {
  name: string;
  full_name: string;
  private: boolean;
  description: string;
  updated_at: string;
}
// GitHub 仓库列表响应数据类型
export interface GitHubRepositoriesData {
  repositories: GitHubRepository[];
}
// GitHub 上传图片请求类型
export interface GitHubUploadRequest {
  image_path: string;
}
// GitHub 上传图片响应数据类型
export interface GitHubUploadData {
  url: string;
  repo: string;
  branch: string;
  folder: string;
}
// GitHub 状态信息类型
export interface GitHubStatus {
  is_logged_in: boolean;
  username: string | null;
  has_config: boolean;
  last_error: string;
}
// GitHub 状态响应数据类型
export interface GitHubStatusData {
  status: GitHubStatus;
}
// GitHub 配置类型
export interface GitHubConfig {
  github_token?: string;
  github_repo?: string;
  github_branch?: string;
  github_folder?: string;
}
// GitHub API响应类型
export type GitHubLoginResponse = BaseResponse<GitHubLoginData>;
export type GitHubRepositoriesResponse = BaseResponse<GitHubRepositoriesData>;
export type GitHubUploadResponse = BaseResponse<GitHubUploadData>;
export type GitHubStatusResponse = BaseResponse<GitHubStatusData>;