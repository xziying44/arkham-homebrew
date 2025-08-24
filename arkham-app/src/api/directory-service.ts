// src/api/directory-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
    DirectorySelectResponse,
    ServiceStatusResponse,
    RecentDirectoriesResponse,
    DirectorySelectData,
    ServiceStatusData,
    RecentDirectoriesData,
    BasicResponse,
    OpenWorkspaceRequest
} from './types';

/**
 * 目录选择服务API
 */
export class DirectoryService {
    /**
     * 选择目录
     * @returns 选择的目录路径信息
     * @throws {ApiError} 当选择失败、用户取消或操作冲突时抛出错误
     */
    public static async selectDirectory(): Promise<DirectorySelectData | null> {
        try {
            const response = await httpClient.get<DirectorySelectData>(
                API_ENDPOINTS.SELECT_DIRECTORY.url,
                {
                    timeout: API_ENDPOINTS.SELECT_DIRECTORY.timeout
                }
            );
            return response.data.data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(1006, '选择目录时发生未知错误', error);
        }
    }

    /**
     * 获取最近目录列表
     * @returns 最近目录列表
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getRecentDirectories(): Promise<RecentDirectoriesData> {
        try {
            const response = await httpClient.get<RecentDirectoriesData>(
                API_ENDPOINTS.GET_RECENT_DIRECTORIES.url,
                {
                    timeout: API_ENDPOINTS.GET_RECENT_DIRECTORIES.timeout
                }
            );
            return response.data.data!;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(2001, '获取最近目录列表失败', error);
        }
    }

    /**
     * 打开工作空间
     * @param directory 要打开的目录路径
     * @throws {ApiError} 当打开失败时抛出错误
     */
    public static async openWorkspace(directory: string): Promise<void> {
        try {
            const requestData: OpenWorkspaceRequest = { directory };
            await httpClient.post(
                API_ENDPOINTS.OPEN_WORKSPACE.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.OPEN_WORKSPACE.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(1007, '打开工作空间失败', error);
        }
    }

    /**
     * 清空最近目录列表
     * @throws {ApiError} 当清空失败时抛出错误
     */
    public static async clearRecentDirectories(): Promise<void> {
        try {
            await httpClient.delete(
                API_ENDPOINTS.CLEAR_RECENT_DIRECTORIES.url,
                {
                    timeout: API_ENDPOINTS.CLEAR_RECENT_DIRECTORIES.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(2001, '清空最近目录失败', error);
        }
    }

    /**
     * 移除指定最近目录
     * @param directoryPath 要移除的目录路径
     * @throws {ApiError} 当移除失败时抛出错误
     */
    public static async removeRecentDirectory(directoryPath: string): Promise<void> {
        try {
            // URL编码路径以处理特殊字符
            const encodedPath = encodeURIComponent(directoryPath);
            const url = `${API_ENDPOINTS.REMOVE_RECENT_DIRECTORY.url}/${encodedPath}`;
            
            await httpClient.delete(url, {
                timeout: API_ENDPOINTS.REMOVE_RECENT_DIRECTORY.timeout
            });
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(2001, '移除最近目录失败', error);
        }
    }

    /**
     * 获取服务状态
     * @returns 服务状态信息
     * @throws {ApiError} 当获取状态失败时抛出错误
     */
    public static async getServiceStatus(): Promise<ServiceStatusData> {
        try {
            const response = await httpClient.get<ServiceStatusData>(
                API_ENDPOINTS.GET_STATUS.url,
                {
                    timeout: API_ENDPOINTS.GET_STATUS.timeout
                }
            );
            return response.data.data!;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(1006, '获取服务状态时发生未知错误', error);
        }
    }

    /**
     * 检查服务是否可用
     * @returns 服务是否可用
     */
    public static async isServiceAvailable(): Promise<boolean> {
        try {
            await this.getServiceStatus();
            return true;
        } catch (error) {
            console.warn('服务不可用:', error);
            return false;
        }
    }

    /**
     * 检查是否正在选择目录
     * @returns 是否正在选择目录
     */
    public static async isSelecting(): Promise<boolean> {
        try {
            const status = await this.getServiceStatus();
            return status.is_selecting;
        } catch (error) {
            console.warn('无法获取选择状态:', error);
            return false;
        }
    }

    /**
     * 检查是否已打开工作空间
     * @returns 是否已打开工作空间
     */
    public static async hasWorkspace(): Promise<boolean> {
        try {
            const status = await this.getServiceStatus();
            return status.has_workspace;
        } catch (error) {
            console.warn('无法获取工作空间状态:', error);
            return false;
        }
    }

    /**
     * 获取当前工作空间路径
     * @returns 工作空间路径，如果没有打开工作空间则返回null
     */
    public static async getCurrentWorkspacePath(): Promise<string | null> {
        try {
            const status = await this.getServiceStatus();
            return status.workspace_path;
        } catch (error) {
            console.warn('无法获取工作空间路径:', error);
            return null;
        }
    }
}

// 导出便捷方法
export const {
    selectDirectory,
    getRecentDirectories,
    openWorkspace,
    clearRecentDirectories,
    removeRecentDirectory,
    getServiceStatus,
    isServiceAvailable,
    isSelecting,
    hasWorkspace,
    getCurrentWorkspacePath
} = DirectoryService;

export default DirectoryService;
