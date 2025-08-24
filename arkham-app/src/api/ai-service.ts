// ai-service.ts
import httpClient from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
  GenerateCardInfoStreamRequest,
  ParseCardJsonRequest,
  ParseCardJsonResponse,
  GenerateAndParseCardRequest,
  GenerateAndParseCardResponse,
  StreamDataChunk
} from './types';

/**
 * AI服务类 - 处理OpenAI卡牌生成相关接口
 */
class AIService {
  /**
   * 流式生成卡牌JSON信息
   * @param request 生成请求参数
   * @param onChunk 流式数据回调函数
   * @param onError 错误回调函数
   * @param onComplete 完成回调函数
   * @returns Promise<void>
   */
  async generateCardInfoStream(
    request: GenerateCardInfoStreamRequest,
    onChunk: (chunk: StreamDataChunk) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    try {
      const response = await fetch(API_ENDPOINTS.GENERATE_CARD_INFO_STREAM.url, {
        method: API_ENDPOINTS.GENERATE_CARD_INFO_STREAM.method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            onComplete?.();
            break;
          }

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6); // 移除 "data: " 前缀
                if (jsonStr.trim()) {
                  const data: StreamDataChunk = JSON.parse(jsonStr);
                  onChunk(data);

                  // 如果收到完成信号或错误，提前结束
                  if (data.done || data.error) {
                    if (data.error) {
                      onError?.(new Error(data.error));
                    } else {
                      onComplete?.();
                    }
                    return;
                  }
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }

  /**
   * 解析验证卡牌JSON
   * @param request 解析请求参数
   * @returns Promise<ParseCardJsonResponse>
   */
  async parseCardJson(request: ParseCardJsonRequest): Promise<ParseCardJsonResponse> {
    return httpClient.post<ParseCardJsonResponse>(
      API_ENDPOINTS.PARSE_CARD_JSON.url,
      request,
      {
        timeout: API_ENDPOINTS.PARSE_CARD_JSON.timeout || 30000  // ✅ 使用正确的timeout配置，并提供默认值
      }
    );
  }

  /**
   * 一次性生成并解析卡牌
   * @param request 生成请求参数
   * @returns Promise<GenerateAndParseCardResponse>
   */
  async generateAndParseCard(request: GenerateAndParseCardRequest): Promise<GenerateAndParseCardResponse> {
    return httpClient.post<GenerateAndParseCardResponse>(
      API_ENDPOINTS.GENERATE_AND_PARSE_CARD.url,
      request,
      API_ENDPOINTS.GENERATE_AND_PARSE_CARD.timeout
    );
  }
}

// 创建并导出单例实例
const aiService = new AIService();
export default aiService;
