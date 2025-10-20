// content-package-service.ts
import { httpClient, ApiError } from './http-client';
import type { ApiResponse } from './types';

/**
 * 内容包导出TTS物品的请求数据结构
 */
export interface ExportContentPackageTtsRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
}

/**
 * 内容包导出TTS物品的响应数据结构
 */
export interface ExportContentPackageTtsData {
    /** 操作日志信息 */
    logs: string[];
    /** TTS保存目录的文件路径（Windows系统） */
    tts_path?: string;
    /** 内容包目录的文件路径 */
    local_path?: string;
}

/**
 * 内容包导出ArkhamDB格式的请求数据结构
 */
export interface ExportContentPackageArkhamdbRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
    /** 可选的输出文件路径 */
    output_path?: string;
}

/**
 * 内容包导出ArkhamDB格式的响应数据结构
 */
export interface ExportContentPackageArkhamdbData {
    /** 操作日志信息 */
    logs: string[];
    /** ArkhamDB格式数据 */
    arkhamdb_data?: any;
    /** 输出文件路径 */
    output_path?: string;
}

/**
 * 内容包相关服务API
 */
export class ContentPackageService {
    /**
     * 导出内容包到TTS物品
     * @param packagePath 内容包文件的相对路径
     * @returns 导出结果，包含日志信息和文件路径
     * @throws {ApiError} 当导出失败时抛出错误
     */
    public static async exportToTts(
        packagePath: string
    ): Promise<ExportContentPackageTtsData> {
        try {
            const requestData: ExportContentPackageTtsRequest = {
                package_path: packagePath
            };

            const response = await httpClient.post<ExportContentPackageTtsData>(
                '/api/content-package/export-tts',
                requestData,
                {
                    timeout: 60000 // TTS导出可能较耗时，设置60秒超时
                }
            );

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            return response;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14003, '导出内容包到TTS失败（系统错误）', error);
        }
    }

    /**
     * 导出内容包到ArkhamDB格式
     * @param packagePath 内容包文件的相对路径
     * @param outputPath 可选的输出文件路径
     * @returns 导出结果，包含日志信息、ArkhamDB数据和文件路径
     * @throws {ApiError} 当导出失败时抛出错误
     */
    public static async exportToArkhamdb(
        packagePath: string,
        outputPath?: string
    ): Promise<ExportContentPackageArkhamdbData> {
        try {
            const requestData: ExportContentPackageArkhamdbRequest = {
                package_path: packagePath,
                output_path: outputPath
            };

            const response = await httpClient.post<ExportContentPackageArkhamdbData>(
                '/api/content-package/export-arkhamdb',
                requestData,
                {
                    timeout: 120000 // ArkhamDB导出可能更耗时，设置120秒超时
                }
            );

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            return response;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14005, '导出内容包到ArkhamDB失败（系统错误）', error);
        }
    }
}

// 导出便捷方法
export const { exportToTts, exportToArkhamdb } = ContentPackageService;

export default ContentPackageService;