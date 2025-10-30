// content-package-service.ts
import {httpClient, ApiError} from './http-client';
import type {ApiResponse} from './types';

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
 * 内容包获取遭遇组的请求数据结构
 */
export interface GetContentPackageEncounterGroupsRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
}

/**
 * 遭遇组数据结构
 */
export interface EncounterGroup {
    /** 遭遇组名称 */
    name: string;
    /** 遭遇组图片base64数据 */
    base64: string;
    /** 遭遇组图片相对路径 */
    relative_path: string;
}

/**
 * 内容包获取遭遇组的响应数据结构
 */
export interface GetContentPackageEncounterGroupsData {
    /** 工作空间路径 */
    workspace_path?: string;
    /** 内容包路径 */
    package_path?: string;
    /** 遭遇组总数 */
    encounter_groups_count?: number;
    /** 遭遇组列表 */
    encounter_groups: EncounterGroup[];
    /** 操作日志信息 */
    logs: string[];
}

/**
 * 卡牌编号方案项
 */
export interface CardNumberingPlanItem {
    /** 卡牌文件路径 */
    filename: string;
    /** 卡牌名称 */
    name: string;
    /** 卡牌类型 */
    type: string;
    /** 职阶 */
    class: string;
    /** 遭遇组 */
    encounter_group: string;
    /** 遭遇组编号 */
    encounter_group_number: string;
    /** 卡牌序号 */
    card_number: string;
    /** 卡牌数量 */
    quantity: number;
}

/**
 * 生成卡牌编号方案的请求数据结构
 */
export interface GenerateCardNumberingPlanRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
    /** 无遭遇组卡牌的位置，'before' 或 'after' */
    no_encounter_position?: string;
    /** 起始序号 */
    start_number?: number;
}

/**
 * 生成卡牌编号方案的响应数据结构
 */
export interface GenerateCardNumberingPlanData {
    /** 编号方案列表 */
    numbering_plan: CardNumberingPlanItem[];
    /** 操作日志信息 */
    logs: string[];
}

/**
 * 应用卡牌编号的请求数据结构
 */
export interface ApplyCardNumberingRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
    /** 编号方案列表 */
    numbering_plan: CardNumberingPlanItem[];
}

/**
 * 应用卡牌编号的响应数据结构
 */
export interface ApplyCardNumberingData {
    /** 更新的卡牌数量 */
    updated_count: number;
    /** 操作日志信息 */
    logs: string[];
}

/**
 * 导出PNP PDF的请求数据结构
 */
export interface ExportContentPackagePnpRequest {
    /** 内容包文件的相对路径 */
    package_path: string;
    /** 导出参数（传递给ExportHelper） */
    export_params: {
        format: string;
        dpi: number;
        size: string;
        bleed: number;
        bleed_mode: string;
        bleed_model: string;
        quality?: number;
        saturation?: number;
        brightness?: number;
        gamma?: number;
    };
    /** 输出PDF文件名 */
    output_filename?: string;
    /** 导出模式：'single_card' 或 'print_sheet' */
    mode?: string;
    /** 纸张规格（仅在print_sheet模式下使用）：'A4', 'A3', 'Letter' */
    paper_size?: string;
}

/**
 * 导出PNP PDF的响应数据结构
 */
export interface ExportContentPackagePnpData {
    /** 输出文件路径 */
    output_path: string;
    /** 导出的卡牌数量 */
    cards_exported: number;
    /** 操作日志信息 */
    logs: string[];
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

    /**
     * 获取内容包中的遭遇组图片
     * @param packagePath 内容包文件的相对路径
     * @returns 遭遇组数据，包含工作空间路径、内容包路径、遭遇组列表和操作日志
     * @throws {ApiError} 当获取遭遇组失败时抛出错误
     */
    public static async getEncounterGroups(
        packagePath: string
    ): Promise<GetContentPackageEncounterGroupsData> {
        try {
            const requestData: GetContentPackageEncounterGroupsRequest = {
                package_path: packagePath
            };

            const response = await httpClient.post<GetContentPackageEncounterGroupsData>(
                '/api/content-package/encounter-groups',
                requestData,
                {
                    timeout: 60000 // 遭遇组获取可能较耗时，设置60秒超时
                }
            );

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            // 确保遭遇组列表是数组
            if (!response.encounter_groups) {
                response.encounter_groups = [];
            }

            // 不要动这里，这里不是BUG
            return response.data.data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14006, '获取内容包遭遇组失败（系统错误）', error);
        }
    }

    /**
     * 生成卡牌编号方案
     * @param packagePath 内容包文件的相对路径
     * @param noEncounterPosition 无遭遇组卡牌的位置，'before' 或 'after'，默认 'before'
     * @param startNumber 起始序号，默认 1
     * @returns 编号方案数据，包含编号方案列表和操作日志
     * @throws {ApiError} 当生成编号方案失败时抛出错误
     */
    public static async generateCardNumberingPlan(
        packagePath: string,
        noEncounterPosition: string = 'before',
        startNumber: number = 1
    ): Promise<GenerateCardNumberingPlanData> {
        try {
            const requestData: GenerateCardNumberingPlanRequest = {
                package_path: packagePath,
                no_encounter_position: noEncounterPosition,
                start_number: startNumber
            };

            const response = (await httpClient.post<GenerateCardNumberingPlanData>(
                '/api/content-package/generate-numbering-plan',
                requestData,
                {
                    timeout: 30000 // 生成编号方案较快，设置30秒超时
                }
            )).data.data;

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            // 确保编号方案列表是数组
            if (!response.numbering_plan) {
                response.numbering_plan = [];
            }

            return response;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14006, '生成卡牌编号方案失败（系统错误）', error);
        }
    }

    /**
     * 应用卡牌编号方案
     * @param packagePath 内容包文件的相对路径
     * @param numberingPlan 编号方案列表
     * @returns 应用结果，包含更新的卡牌数量和操作日志
     * @throws {ApiError} 当应用编号方案失败时抛出错误
     */
    public static async applyCardNumbering(
        packagePath: string,
        numberingPlan: CardNumberingPlanItem[]
    ): Promise<ApplyCardNumberingData> {
        try {
            const requestData: ApplyCardNumberingRequest = {
                package_path: packagePath,
                numbering_plan: numberingPlan
            };

            const response = (await httpClient.post<ApplyCardNumberingData>(
                '/api/content-package/apply-numbering',
                requestData,
                {
                    timeout: 60000 // 应用编号方案可能涉及文件写入，设置60秒超时
                }
            )).data.data;

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            // 确保updated_count存在
            if (typeof response.updated_count !== 'number') {
                response.updated_count = 0;
            }

            return response;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14008, '应用卡牌编号方案失败（系统错误）', error);
        }
    }

    /**
     * 导出内容包为PNP PDF
     * @param packagePath 内容包文件的相对路径
     * @param exportParams 导出参数（传递给ExportHelper）
     * @param outputFilename 输出PDF文件名，默认'pnp_export.pdf'
     * @param mode 导出模式，'single_card' 或 'print_sheet'，默认'single_card'
     * @param paperSize 纸张规格（仅在print_sheet模式下使用），默认'A4'
     * @returns 导出结果，包含输出路径、导出的卡牌数量和操作日志
     * @throws {ApiError} 当导出失败时抛出错误
     */
    public static async exportToPnp(
        packagePath: string,
        exportParams: ExportContentPackagePnpRequest['export_params'],
        outputFilename: string = 'pnp_export.pdf',
        mode: string = 'single_card',
        paperSize: string = 'A4'
    ): Promise<ExportContentPackagePnpData> {
        try {
            const requestData: ExportContentPackagePnpRequest = {
                package_path: packagePath,
                export_params: exportParams,
                output_filename: outputFilename,
                mode: mode,
                paper_size: paperSize
            };

            const response = (await httpClient.post<ExportContentPackagePnpData>(
                '/api/content-package/export-pnp',
                requestData,
                {
                    timeout: 300000 // PNP导出可能非常耗时，设置5分钟超时
                }
            )).data.data;

            // 确保响应有logs属性
            if (!response.logs) {
                response.logs = [];
            }

            return response;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(14010, '导出内容包为PNP PDF失败（系统错误）', error);
        }
    }
}

// 导出便捷方法
export const {
    exportToTts,
    exportToArkhamdb,
    getEncounterGroups,
    generateCardNumberingPlan,
    applyCardNumbering,
    exportToPnp
} = ContentPackageService;

export default ContentPackageService;