// src/api/workspace-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
    FileTreeData,
    FileContentData,
    ImageContentData,
    FileInfoData,
    FileInfo,
    CreateDirectoryRequest,
    CreateFileRequest,
    RenameItemRequest,
    DeleteItemRequest,
    FileContentRequest
} from './types';

/**
 * 工作空间文件管理服务API
 */
export class WorkspaceService {
    /**
     * 获取文件树
     * @param includeHidden 是否包含隐藏文件，默认false
     * @returns 文件树结构
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getFileTree(includeHidden: boolean = false): Promise<FileTreeData> {
        try {
            const url = `${API_ENDPOINTS.GET_FILE_TREE.url}?include_hidden=${includeHidden}`;
            const response = await httpClient.get<FileTreeData>(url, {
                timeout: API_ENDPOINTS.GET_FILE_TREE.timeout
            });
            return response.data.data!;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3002, '获取文件树失败', error);
        }
    }

    /**
     * 创建目录
     * @param name 目录名称
     * @param parentPath 父目录路径，可选
     * @throws {ApiError} 当创建失败时抛出错误
     */
    public static async createDirectory(name: string, parentPath?: string): Promise<void> {
        try {
            const requestData: CreateDirectoryRequest = {
                name,
                parent_path: parentPath
            };
            
            await httpClient.post(
                API_ENDPOINTS.CREATE_DIRECTORY.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.CREATE_DIRECTORY.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3003, '创建目录失败', error);
        }
    }

    /**
     * 创建文件
     * @param name 文件名称
     * @param content 文件内容，可选
     * @param parentPath 父目录路径，可选
     * @throws {ApiError} 当创建失败时抛出错误
     */
    public static async createFile(name: string, content?: string, parentPath?: string): Promise<void> {
        try {
            const requestData: CreateFileRequest = {
                name,
                content,
                parent_path: parentPath
            };
            
            await httpClient.post(
                API_ENDPOINTS.CREATE_FILE.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.CREATE_FILE.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3004, '创建文件失败', error);
        }
    }

    /**
     * 重命名文件或目录
     * @param oldPath 原路径
     * @param newName 新名称
     * @throws {ApiError} 当重命名失败时抛出错误
     */
    public static async renameItem(oldPath: string, newName: string): Promise<void> {
        try {
            const requestData: RenameItemRequest = {
                old_path: oldPath,
                new_name: newName
            };
            
            await httpClient.put(
                API_ENDPOINTS.RENAME_ITEM.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.RENAME_ITEM.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3005, '重命名失败', error);
        }
    }

    /**
     * 删除文件或目录
     * @param path 要删除的文件或目录路径
     * @throws {ApiError} 当删除失败时抛出错误
     */
    public static async deleteItem(path: string): Promise<void> {
        try {
            const requestData: DeleteItemRequest = { path };
            
            await httpClient.delete(
                API_ENDPOINTS.DELETE_ITEM.url,
                {
                    data: requestData,
                    timeout: API_ENDPOINTS.DELETE_ITEM.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3006, '删除失败', error);
        }
    }

    /**
     * 获取文件内容
     * @param path 文件路径
     * @returns 文件内容
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getFileContent(path: string): Promise<string> {
        try {
            const url = `${API_ENDPOINTS.GET_FILE_CONTENT.url}?path=${encodeURIComponent(path)}`;
            const response = await httpClient.get<FileContentData>(url, {
                timeout: API_ENDPOINTS.GET_FILE_CONTENT.timeout
            });
            return response.data.data!.content;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3007, '获取文件内容失败', error);
        }
    }

    /**
     * 获取图片内容（base64格式）
     * @param path 图片文件路径
     * @returns base64编码的图片数据，包含data URL前缀
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getImageContent(path: string): Promise<string> {
        try {
            const url = `${API_ENDPOINTS.GET_IMAGE_CONTENT.url}?path=${encodeURIComponent(path)}`;
            const response = await httpClient.get<ImageContentData>(url, {
                timeout: API_ENDPOINTS.GET_IMAGE_CONTENT.timeout
            });
            return response.data.data!.content;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(5003, '获取图片内容失败', error);
        }
    }

    /**
     * 获取文件信息
     * @param path 文件路径
     * @returns 文件详细信息
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getFileInfo(path: string): Promise<FileInfo> {
        try {
            const url = `${API_ENDPOINTS.GET_FILE_INFO.url}?path=${encodeURIComponent(path)}`;
            const response = await httpClient.get<FileInfoData>(url, {
                timeout: API_ENDPOINTS.GET_FILE_INFO.timeout
            });
            return response.data.data!.fileInfo;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(5006, '获取文件信息失败', error);
        }
    }

    /**
     * 保存文件内容
     * @param path 文件路径
     * @param content 文件内容
     * @throws {ApiError} 当保存失败时抛出错误
     */
    public static async saveFileContent(path: string, content: string): Promise<void> {
        try {
            const requestData: FileContentRequest = {
                path,
                content
            };
            
            await httpClient.put(
                API_ENDPOINTS.SAVE_FILE_CONTENT.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.SAVE_FILE_CONTENT.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(3008, '保存文件失败', error);
        }
    }
}

// 导出便捷方法
export const {
    getFileTree,
    createDirectory,
    createFile,
    renameItem,
    deleteItem,
    getFileContent,
    getImageContent,
    getFileInfo,
    saveFileContent
} = WorkspaceService;

export default WorkspaceService;
