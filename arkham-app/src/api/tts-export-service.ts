// 更新 tts-export-service.ts 文件
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
    OpenDirectoryRequest,
    ExportDeckImageRequest,
    ExportTtsItemRequest
} from './types';

/**
 * TTS导出相关服务API
 */
export class TtsExportService {
    /**
     * 在资源管理器中打开目录
     * @param directoryPath 相对于工作目录的目录路径
     * @throws {ApiError} 当打开失败时抛出错误
     */
    public static async openDirectory(directoryPath: string): Promise<void> {
        try {
            const requestData: OpenDirectoryRequest = {
                directory_path: directoryPath
            };
            
            await httpClient.post(
                API_ENDPOINTS.OPEN_DIRECTORY.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.OPEN_DIRECTORY.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(9003, '打开目录失败（系统错误）', error);
        }
    }

    /**
     * 导出牌库图片
     * @param deckName 牌库文件名（相对于DeckBuilder文件夹）
     * @param format 导出格式，支持"JPG"和"PNG"，默认"PNG"
     * @param quality 图片质量百分比（1-100），仅对JPG格式有效，默认95
     * @throws {ApiError} 当导出失败时抛出错误
     */
    public static async exportDeckImage(
        deckName: string, 
        format: 'JPG' | 'PNG' = 'PNG', 
        quality: number = 95
    ): Promise<void> {
        try {
            const requestData: ExportDeckImageRequest = {
                deck_name: deckName,
                format,
                quality
            };
            
            await httpClient.post(
                API_ENDPOINTS.EXPORT_DECK_IMAGE.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.EXPORT_DECK_IMAGE.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(8005, '导出牌库图片失败（系统错误）', error);
        }
    }

    /**
     * 导出TTS物品
     * @param deckName 牌库名称（DeckBuilder文件夹中的文件名）
     * @param faceUrl 正面图片URL（完整的HTTP/HTTPS地址）
     * @param backUrl 背面图片URL（完整的HTTP/HTTPS地址）
     * @throws {ApiError} 当导出失败时抛出错误
     */
    public static async exportTtsItem(
        deckName: string,
        faceUrl: string,
        backUrl: string
    ): Promise<void> {
        try {
            const requestData: ExportTtsItemRequest = {
                deck_name: deckName,
                face_url: faceUrl,
                back_url: backUrl
            };
            
            await httpClient.post(
                API_ENDPOINTS.EXPORT_TTS_ITEM.url,
                requestData,
                {
                    timeout: API_ENDPOINTS.EXPORT_TTS_ITEM.timeout
                }
            );
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(11005, '导出TTS物品失败（系统错误）', error);
        }
    }
}

// 导出便捷方法
export const {
    openDirectory,
    exportDeckImage,
    exportTtsItem
} = TtsExportService;

export default TtsExportService;
