import { httpClient } from './http-client';
import { API_ENDPOINTS } from './endpoints';
import type {
  ImageHostUploadRequest,
  ImageHostUploadResponse,
  ImageHostCheckRequest,
  ImageHostCheckResponse,
  ImageHostType,
} from './types';

/**
 * 图床上传服务
 * 提供Cloudinary和ImgBB图床的上传和检查功能
 */
export class ImageHostService {
  /**
   * 上传图片到图床
   * @param data 上传请求数据
   * @returns 上传结果
   */
  static async uploadImage(data: ImageHostUploadRequest): Promise<ImageHostUploadResponse> {
    try {
      const response = await httpClient.request<ImageHostUploadResponse>(
        API_ENDPOINTS.IMAGE_HOST_UPLOAD.url,
        {
          method: API_ENDPOINTS.IMAGE_HOST_UPLOAD.method,
          data,
        }
      );
      return response.data;
    } catch (error) {
      console.error('图片上传失败:', error);
      throw error;
    }
  }

  /**
   * 检查图片是否已存在于图床
   * @param data 检查请求数据
   * @returns 检查结果
   */
  static async checkImageExists(data: ImageHostCheckRequest): Promise<ImageHostCheckResponse> {
    try {
      const response = await httpClient.request<ImageHostCheckResponse>(
        API_ENDPOINTS.IMAGE_HOST_CHECK.url,
        {
          method: API_ENDPOINTS.IMAGE_HOST_CHECK.method,
          data,
        }
      );
      return response.data;
    } catch (error) {
      console.error('检查图片失败:', error);
      throw error;
    }
  }

  /**
   * 上传图片到Cloudinary
   * @param imagePath 图片文件路径
   * @param onlineName 在线文件名（可选）
   * @returns 上传结果
   */
  static async uploadToCloudinary(
    imagePath: string,
    onlineName?: string
  ): Promise<ImageHostUploadResponse> {
    return this.uploadImage({
      image_path: imagePath,
      host_type: ImageHostType.CLOUDINARY,
      online_name: onlineName,
    });
  }

  /**
   * 上传图片到ImgBB
   * @param imagePath 图片文件路径
   * @param onlineName 在线文件名（可选）
   * @returns 上传结果
   */
  static async uploadToImgBB(
    imagePath: string,
    onlineName?: string
  ): Promise<ImageHostUploadResponse> {
    return this.uploadImage({
      image_path: imagePath,
      host_type: ImageHostType.IMGBB,
      online_name: onlineName,
    });
  }

  /**
   * 检查Cloudinary中是否存在指定图片
   * @param onlineName 在线文件名
   * @returns 检查结果
   */
  static async checkCloudinaryImage(onlineName: string): Promise<ImageHostCheckResponse> {
    return this.checkImageExists({
      online_name: onlineName,
      host_type: ImageHostType.CLOUDINARY,
    });
  }

  /**
   * 检查ImgBB中是否存在指定图片
   * @param onlineName 在线文件名
   * @returns 检查结果
   */
  static async checkImgBBImage(onlineName: string): Promise<ImageHostCheckResponse> {
    return this.checkImageExists({
      online_name: onlineName,
      host_type: ImageHostType.IMGBB,
    });
  }

  /**
   * 智能上传：先检查是否存在，如果不存在则上传
   * @param imagePath 图片文件路径
   * @param hostType 图床类型
   * @param onlineName 在线文件名（可选）
   * @returns 上传结果或已存在图片URL
   */
  static async smartUpload(
    imagePath: string,
    hostType: ImageHostType,
    onlineName?: string
  ): Promise<ImageHostUploadResponse> {
    if (!onlineName) {
      // 如果没有指定在线文件名，直接上传
      return this.uploadImage({
        image_path: imagePath,
        host_type: hostType,
      });
    }

    try {
      // 先检查图片是否已存在
      const checkResult = await this.checkImageExists({
        online_name: onlineName,
        host_type: hostType,
      });

      if (checkResult.code === 0 && checkResult.data?.exists && checkResult.data?.url) {
        // 图片已存在，返回现有URL
        return {
          code: 0,
          msg: '图片已存在',
          data: {
            url: checkResult.data.url,
            host_type: hostType,
            online_name: onlineName,
          },
        };
      }
    } catch (error) {
      console.warn('检查图片是否存在时出错，直接上传:', error);
      // 忽略检查错误，继续上传
    }

    // 图片不存在或检查失败，执行上传
    return this.uploadImage({
      image_path: imagePath,
      host_type: hostType,
      online_name: onlineName,
    });
  }
}

export default ImageHostService;