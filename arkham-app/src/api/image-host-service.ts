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
      const response = await httpClient.request<ImageHostUploadResponse>({
        url: API_ENDPOINTS.IMAGE_HOST_UPLOAD.url,
        method: API_ENDPOINTS.IMAGE_HOST_UPLOAD.method,
        data,
        timeout: API_ENDPOINTS.IMAGE_HOST_UPLOAD.timeout,
      });
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
      const response = await httpClient.request<ImageHostCheckResponse>({
        url: API_ENDPOINTS.IMAGE_HOST_CHECK.url,
        method: API_ENDPOINTS.IMAGE_HOST_CHECK.method,
        data,
        timeout: API_ENDPOINTS.IMAGE_HOST_CHECK.timeout,
      });
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
   * 直接上传图片到图床（覆盖上传）
   * @param imagePath 图片文件路径
   * @param hostType 图床类型
   * @param onlineName 在线文件名（可选）
   * @returns 上传结果
   */
  static async smartUpload(
    imagePath: string,
    hostType: ImageHostType,
    onlineName?: string
  ): Promise<ImageHostUploadResponse> {
    // 直接上传，不检查是否已存在，实现覆盖上传
    return this.uploadImage({
      image_path: imagePath,
      host_type: hostType,
      online_name: onlineName,
    });
  }
}

export default ImageHostService;