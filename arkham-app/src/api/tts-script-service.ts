import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';

export class TtsScriptService {
  public static async generateFromCard(cardData: any): Promise<{ GMNotes: string; LuaScript: string }> {
    try {
      const resp = await httpClient.post<{ GMNotes: string; LuaScript: string }>(
        API_ENDPOINTS.GENERATE_TTS_SCRIPT.url,
        { card_data: cardData },
        { timeout: API_ENDPOINTS.GENERATE_TTS_SCRIPT.timeout }
      );
      return resp.data.data as { GMNotes: string; LuaScript: string };
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(11011, '生成TTS脚本失败（系统错误）', error);
    }
  }
}

export default TtsScriptService;
