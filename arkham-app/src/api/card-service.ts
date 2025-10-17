// src/api/card-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
    CardData,
    GenerateCardRequest,
    SaveCardRequest,
    SaveCardEnhancedRequest,
    GenerateCardData,
    SaveCardData
} from './types';

/**
 * 卡牌生成服务API
 */
export class CardService {
    /**
     * 生成卡图
     * @param cardData 卡牌数据JSON
     * @returns base64编码的图片数据
     * @throws {ApiError} 当生成失败时抛出错误
     */
    public static async generateCard(cardData: CardData): Promise<any> {
        try {
            const requestData: GenerateCardRequest = {
                json_data: cardData
            };

            const response = await httpClient.post<GenerateCardData>(
                API_ENDPOINTS.GENERATE_CARD.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.GENERATE_CARD.timeout
                }
            );

            return response.data.data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(4002, '生成卡图失败', error);
        }
    }

    /**
     * 保存卡图
     * @param cardData 卡牌数据JSON
     * @param filename 保存的文件名（含扩展名）
     * @param parentPath 保存的父目录路径，可选
     * @throws {ApiError} 当保存失败时抛出错误
     */
    public static async saveCard(
        cardData: CardData,
        filename: string,
        parentPath?: string
    ): Promise<void> {
        try {
            const requestData: SaveCardRequest = {
                json_data: cardData,
                filename,
                parent_path: parentPath
            };

            await httpClient.post(
                API_ENDPOINTS.SAVE_CARD.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.SAVE_CARD.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(4005, '保存卡图失败', error);
        }
    }

    /**
     * 保存卡图（增强版：支持双面卡牌、格式选择、质量设置和横向图片旋转）
     * @param cardData 卡牌数据JSON
     * @param filename 保存的文件名（不含扩展名）
     * @param options 保存选项
     * @returns 保存成功的文件路径列表
     * @throws {ApiError} 当保存失败时抛出错误
     */
    public static async saveCardEnhanced(
        cardData: CardData,
        filename: string,
        options?: {
            parentPath?: string;
            format?: 'PNG' | 'JPG';
            quality?: number;
            rotateLandscape?: boolean;
        }
    ): Promise<string[]> {
        try {
            const requestData: SaveCardEnhancedRequest = {
                json_data: cardData,
                filename,
                parent_path: options?.parentPath,
                format: options?.format || 'JPG',
                quality: options?.quality || 95,
                rotate_landscape: options?.rotateLandscape || false
            };

            const response = await httpClient.post<SaveCardData>(
                API_ENDPOINTS.SAVE_CARD.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.SAVE_CARD.timeout
                }
            );

            return response.data.data?.saved_files || [];
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(4005, '保存卡图失败', error);
        }
    }

    /**
     * 生成并保存卡图的便捷方法
     * @param cardData 卡牌数据JSON
     * @param filename 保存的文件名（含扩展名）
     * @param parentPath 保存的父目录路径，可选
     * @returns 生成的base64图片数据和保存结果
     * @throws {ApiError} 当操作失败时抛出错误
     */
    public static async generateAndSaveCard(
        cardData: CardData,
        filename: string,
        parentPath?: string
    ): Promise<{ image: string }> {
        try {
            // 先生成卡图
            const result_card = await this.generateCard(cardData);
            const image = result_card?.image

            // 再保存卡图
            await this.saveCard(cardData, filename, parentPath);

            return { image };
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(4002, '生成并保存卡图失败', error);
        }
    }

    /**
     * 验证卡牌数据的基本完整性
     * @param cardData 卡牌数据
     * @returns 验证结果和错误信息
     */
    public static validateCardData(cardData: CardData): {
        isValid: boolean;
        errors: string[]
    } {
        const errors: string[] = [];

        // 检查必要字段

        if (!cardData.type || cardData.type.trim() === '') {
            errors.push('卡牌类型不能为空');
        }




        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * 创建默认卡牌数据模板
     * @param type 卡牌类型
     * @returns 默认卡牌数据
     */
    public static createDefaultCardData(type: string = '支援卡'): CardData {
        return {
            type,
            name: '新卡牌',
            id: '',
            created_at: '',
            version: '1.0',
            subtitle: '',
            class: '多职阶',
            subclass: [],
            health: 0,
            horror: 0,
            slots: '',
            slots2: '',
            level: 0,
            cost: 0,
            submit_icon: [],
            traits: [],
            body: '',
            flavor: '',
            picture_path: ''
        };
    }
}

// 导出便捷方法
export const {
    generateCard,
    saveCard,
    saveCardEnhanced,
    generateAndSaveCard,
    validateCardData,
    createDefaultCardData
} = CardService;

export default CardService;
