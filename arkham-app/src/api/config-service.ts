// src/api/config-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
    ConfigData,
    GetConfigData,
    SaveConfigRequest,
    EncounterGroupsData
} from './types';

/**
 * 配置管理服务API
 */
export class ConfigService {
    /**
     * 获取配置项
     * @returns 配置项对象
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getConfig(): Promise<ConfigData> {
        try {
            const response = await httpClient.get<GetConfigData>(
                API_ENDPOINTS.GET_CONFIG.url,
                {
                    timeout: API_ENDPOINTS.GET_CONFIG.timeout
                }
            );

            return response.data.data!.config;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(6001, '获取配置失败', error);
        }
    }

    /**
     * 保存配置项
     * @param config 配置项对象
     * @throws {ApiError} 当保存失败时抛出错误
     */
    public static async saveConfig(config: ConfigData): Promise<void> {
        try {
            // 验证配置数据
            if (!config || typeof config !== 'object') {
                throw new ApiError(6002, '请提供有效的配置数据');
            }

            const requestData: SaveConfigRequest = { config };

            await httpClient.put(
                API_ENDPOINTS.SAVE_CONFIG.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.SAVE_CONFIG.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(6003, '保存配置失败', error);
        }
    }

    /**
     * 获取遭遇组列表
     * @returns 遭遇组名称列表
     * @throws {ApiError} 当获取失败时抛出错误
     */
    public static async getEncounterGroups(): Promise<string[]> {
        try {
            const response = await httpClient.get<EncounterGroupsData>(
                API_ENDPOINTS.GET_ENCOUNTER_GROUPS.url,
                {
                    timeout: API_ENDPOINTS.GET_ENCOUNTER_GROUPS.timeout
                }
            );

            return response.data.data!.encounter_groups;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(6005, '获取遭遇组列表失败', error);
        }
    }

    /**
     * 更新特定配置项
     * @param key 配置项键名
     * @param value 配置项值
     * @throws {ApiError} 当更新失败时抛出错误
     */
    public static async updateConfigItem(key: string, value: any): Promise<void> {
        try {
            // 先获取当前配置
            const currentConfig = await this.getConfig();
            
            // 更新指定项
            const updatedConfig = {
                ...currentConfig,
                [key]: value
            };
            
            // 保存更新后的配置
            await this.saveConfig(updatedConfig);
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(6003, `更新配置项 ${key} 失败`, error);
        }
    }

    /**
     * 获取特定配置项
     * @param key 配置项键名
     * @param defaultValue 默认值
     * @returns 配置项值
     */
    public static async getConfigItem<T = any>(key: string, defaultValue?: T): Promise<T> {
        try {
            const config = await this.getConfig();
            return config[key] !== undefined ? config[key] : defaultValue;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(6001, `获取配置项 ${key} 失败`, error);
        }
    }

    /**
     * 设置遭遇组目录
     * @param directory 遭遇组目录路径
     * @throws {ApiError} 当设置失败时抛出错误
     */
    public static async setEncounterGroupsDirectory(directory: string): Promise<void> {
        await this.updateConfigItem('encounter_groups_dir', directory);
    }

    /**
     * 获取遭遇组目录
     * @returns 遭遇组目录路径
     */
    public static async getEncounterGroupsDirectory(): Promise<string | null> {
        try {
            return await this.getConfigItem('encounter_groups_dir', null);
        } catch (error) {
            console.warn('获取遭遇组目录配置失败:', error);
            return null;
        }
    }

    /**
     * 验证配置完整性
     * @param config 配置对象
     * @returns 验证结果
     */
    public static validateConfig(config: ConfigData): {
        isValid: boolean;
        errors: string[];
        warnings: string[];
    } {
        const errors: string[] = [];
        const warnings: string[] = [];

        // 检查必要配置项
        if (!config.encounter_groups_dir || config.encounter_groups_dir.trim() === '') {
            warnings.push('遭遇组目录未配置，将无法获取遭遇组列表');
        }

        // 检查目录路径格式（简单验证）
        if (config.encounter_groups_dir) {
            const invalidChars = /[<>:"|?*]/;
            if (invalidChars.test(config.encounter_groups_dir)) {
                errors.push('遭遇组目录路径包含无效字符');
            }
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }

    /**
     * 创建默认配置
     * @returns 默认配置对象
     */
    public static createDefaultConfig(): ConfigData {
        return {
            encounter_groups_dir: 'encounters'
        };
    }
}

// 导出便捷方法
export const {
    getConfig,
    saveConfig,
    getEncounterGroups,
    updateConfigItem,
    getConfigItem,
    setEncounterGroupsDirectory,
    getEncounterGroupsDirectory,
    validateConfig,
    createDefaultConfig
} = ConfigService;

export default ConfigService;
