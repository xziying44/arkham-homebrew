import { httpClient } from './http-client';
import type {
  ArkhamDBImportRequest,
  ArkhamDBImportResponse,
  ArkhamDBLogsResponse,
  ArkhamDBValidateRequest,
  ArkhamDBValidateResponse
} from './types';

/**
 * ArkhamDB导入服务
 * 提供ArkhamDB内容包的导入、验证和日志获取功能
 */
export class ArkhamDBService {
  /**
   * 导入ArkhamDB内容包
   * @param request 导入请求参数
   * @returns Promise<ArkhamDBImportResponse>
   */
  static async importContentPack(request: ArkhamDBImportRequest): Promise<ArkhamDBImportResponse> {
    const response = await httpClient.post<ArkhamDBImportResponse['data']>(
      '/api/arkhamdb/import',
      request
    );
    return response.data;
  }

  /**
   * 获取ArkhamDB导入日志
   * @returns Promise<ArkhamDBLogsResponse>
   */
  static async getImportLogs(): Promise<ArkhamDBLogsResponse> {
    const response = await httpClient.get<ArkhamDBLogsResponse['data']>(
      '/api/arkhamdb/logs'
    );
    return response.data;
  }

  /**
   * 验证ArkhamDB内容包结构
   * @param request 验证请求参数
   * @returns Promise<ArkhamDBValidateResponse>
   */
  static async validateContentPack(request: ArkhamDBValidateRequest): Promise<ArkhamDBValidateResponse> {
    const response = await httpClient.post<ArkhamDBValidateResponse['data']>(
      '/api/arkhamdb/validate',
      request
    );
    return response.data;
  }

  /**
   * 批量验证ArkhamDB内容包
   * @param contentPacks 内容包列表
   * @returns Promise<ArkhamDBValidateResponse[]>
   */
  static async validateMultipleContentPacks(
    contentPacks: ArkhamDBValidateRequest[]
  ): Promise<ArkhamDBValidateResponse[]> {
    const validationPromises = contentPacks.map(contentPack =>
      this.validateContentPack(contentPack)
    );

    return Promise.all(validationPromises);
  }

  /**
   * 检查是否已有导入记录
   * @returns Promise<boolean> 如果有导入记录返回true，否则返回false
   */
  static async hasImportRecords(): Promise<boolean> {
    try {
      const response = await this.getImportLogs();
      return response.data?.has_logs || false;
    } catch (error) {
      // 如果获取日志失败（比如没有导入记录），返回false
      return false;
    }
  }
}

export default ArkhamDBService;