// github-service.ts
import { httpClient, ApiError } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
  GitHubLoginRequest,
  GitHubLoginData,
  GitHubRepositoriesData,
  GitHubUploadRequest,
  GitHubUploadData,
  GitHubStatusData,
  GitHubRepository
} from './types';

/**
 * GitHub图床相关服务API
 */
export class GitHubService {
  /**
   * GitHub登录
   * @param token GitHub Personal Access Token
   * @returns Promise<GitHubLoginData> 登录成功返回用户信息
   * @throws {ApiError} 当登录失败时抛出错误
   */
  public static async login(token: string): Promise<GitHubLoginData> {
    try {
      const requestData: GitHubLoginRequest = { token };
      
      const response = await httpClient.post<GitHubLoginData>(
        API_ENDPOINTS.GITHUB_LOGIN.url,
        requestData,
        {
          timeout: API_ENDPOINTS.GITHUB_LOGIN.timeout
        }
      );
      
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(10003, 'GitHub登录失败（系统错误）', error);
    }
  }

  /**
   * 获取GitHub仓库列表
   * @returns Promise<GitHubRepository[]> 仓库列表
   * @throws {ApiError} 当获取失败时抛出错误
   */
  public static async getRepositories(): Promise<GitHubRepository[]> {
    try {
      const response = await httpClient.get<GitHubRepositoriesData>(
        API_ENDPOINTS.GITHUB_REPOSITORIES.url,
        {
          timeout: API_ENDPOINTS.GITHUB_REPOSITORIES.timeout
        }
      );
      
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(10006, '获取仓库列表失败（系统错误）', error);
    }
  }

  /**
   * 上传图片到GitHub
   * @param imagePath 相对于工作目录的图片文件路径
   * @returns Promise<GitHubUploadData> 上传结果，包含图片直链等信息
   * @throws {ApiError} 当上传失败时抛出错误
   */
  public static async uploadImage(imagePath: string): Promise<GitHubUploadData> {
    try {
      const requestData: GitHubUploadRequest = {
        image_path: imagePath
      };
      
      const response = await httpClient.post<GitHubUploadData>(
        API_ENDPOINTS.GITHUB_UPLOAD.url,
        requestData,
        {
          timeout: API_ENDPOINTS.GITHUB_UPLOAD.timeout
        }
      );
      
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(10012, '上传图片失败（系统错误）', error);
    }
  }

  /**
   * 获取GitHub状态
   * @returns Promise<GitHubStatusData> GitHub连接状态和配置信息
   * @throws {ApiError} 当获取失败时抛出错误
   */
  public static async getStatus(): Promise<GitHubStatusData> {
    try {
      const response = await httpClient.get<GitHubStatusData>(
        API_ENDPOINTS.GITHUB_STATUS.url,
        {
          timeout: API_ENDPOINTS.GITHUB_STATUS.timeout
        }
      );
      
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(10013, '获取GitHub状态失败（系统错误）', error);
    }
  }

  /**
   * 检查是否已登录
   * @returns Promise<boolean> 是否已登录
   */
  public static async isLoggedIn(): Promise<boolean> {
    try {
      const statusData = await this.getStatus();
      return statusData.status.is_logged_in;
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取支持的图片格式列表
   * @returns string[] 支持的文件扩展名
   */
  public static getSupportedImageFormats(): string[] {
    return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
  }

  /**
   * 检查文件格式是否受支持
   * @param filename 文件名
   * @returns boolean 是否支持该格式
   */
  public static isSupportedImageFormat(filename: string): boolean {
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return this.getSupportedImageFormats().includes(ext);
  }
}

// 导出便捷方法
export const {
  login,
  getRepositories,
  uploadImage,
  getStatus,
  isLoggedIn,
  getSupportedImageFormats,
  isSupportedImageFormat
} = GitHubService;

export default GitHubService;
