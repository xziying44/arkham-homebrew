// src/api/language-config-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type { BaseResponse, LanguageConfigData, LanguageConfigItem } from './types';

export class LanguageConfigService {
  /**
   * 获取多语言字体与文本配置
   */
  public static async getLanguageConfig(): Promise<LanguageConfigData> {
    try {
      const response = await httpClient.get<BaseResponse<LanguageConfigData>>(
        API_ENDPOINTS.GET_LANGUAGE_CONFIG.url,
        {
          timeout: API_ENDPOINTS.GET_LANGUAGE_CONFIG.timeout,
        },
      );

      return (response.data.data as LanguageConfigData) ?? {
        config: [],
        fonts: [],
        fontsDir: '',
        fontsDirIsWorkspace: false,
      };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(6001, '获取语言配置失败', error);
    }
  }

  /**
   * 保存多语言字体与文本配置
   */
  public static async saveLanguageConfig(config: LanguageConfigItem[]): Promise<void> {
    try {
      await httpClient.put(
        API_ENDPOINTS.SAVE_LANGUAGE_CONFIG.url,
        { config },
        {
          timeout: API_ENDPOINTS.SAVE_LANGUAGE_CONFIG.timeout,
        },
      );
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(6003, '保存语言配置失败', error);
    }
  }
}

export default LanguageConfigService;

