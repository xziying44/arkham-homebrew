import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type AxiosError
} from 'axios';
import { API_BASE_URL } from './endpoints';
import { ErrorCode, type BaseResponse } from './types';

// 自定义错误类
export class ApiError extends Error {
  public code: number;
  public originalError?: any;

  constructor(code: number, message: string, originalError?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.originalError = originalError;
  }
}

// HTTP客户端类
class HttpClient {
  private instance: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.instance = axios.create({
      baseURL,
      timeout: 300000, // 默认超时5分钟
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  // 设置拦截器
  private setupInterceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse<BaseResponse>) => {
        console.log(`✅ API Response: ${response.config.url}`, response.data);
        
        // 检查业务状态码
        if (response.data.code !== ErrorCode.SUCCESS) {
          throw new ApiError(
            response.data.code,
            response.data.msg,
            response.data
          );
        }
        
        return response;
      },
      (error: AxiosError) => {
        console.error('❌ Response Error:', error);
        
        // HTTP错误处理
        if (error.response) {
          const { status, data } = error.response;
          let errorCode = ErrorCode.SERVER_ERROR;
          let errorMessage = '服务器错误';

          // 根据HTTP状态码映射错误码
          switch (status) {
            case 404:
              errorCode = ErrorCode.NOT_FOUND;
              errorMessage = '接口不存在';
              break;
            case 405:
              errorCode = ErrorCode.METHOD_NOT_ALLOWED;
              errorMessage = '请求方法不支持';
              break;
            case 408:
              errorCode = ErrorCode.TIMEOUT;
              errorMessage = '请求超时';
              break;
            case 409:
              errorCode = ErrorCode.SELECTING_IN_PROGRESS;
              errorMessage = '操作正在进行中';
              break;
            case 500:
              errorCode = ErrorCode.INTERNAL_ERROR;
              errorMessage = '服务器内部错误';
              break;
            default:
              if (data && typeof data === 'object' && 'code' in data && 'msg' in data) {
                errorCode = data.code as number;
                errorMessage = data.msg as string;
              }
          }

          throw new ApiError(errorCode, errorMessage, error.response.data);
        } else if (error.request) {
          // 网络错误
          throw new ApiError(
            ErrorCode.SERVER_ERROR,
            '网络连接失败，请检查服务是否启动',
            error
          );
        } else {
          // 其他错误
          throw new ApiError(
            ErrorCode.SERVER_ERROR,
            error.message || '未知错误',
            error
          );
        }
      }
    );
  }

  // GET请求
  public async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<BaseResponse<T>>> {
    return this.instance.get<BaseResponse<T>>(url, config);
  }

  // POST请求
  public async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<BaseResponse<T>>> {
    return this.instance.post<BaseResponse<T>>(url, data, config);
  }

  // PUT请求
  public async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<BaseResponse<T>>> {
    return this.instance.put<BaseResponse<T>>(url, data, config);
  }

  // DELETE请求
  public async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<BaseResponse<T>>> {
    return this.instance.delete<BaseResponse<T>>(url, config);
  }

  // 通用请求方法
  public async request<T = any>(
    config: AxiosRequestConfig
  ): Promise<AxiosResponse<BaseResponse<T>>> {
    return this.instance.request<BaseResponse<T>>(config);
  }

  // 更新基础URL
  public setBaseURL(baseURL: string): void {
    this.instance.defaults.baseURL = baseURL;
  }

  // 设置默认超时
  public setTimeout(timeout: number): void {
    this.instance.defaults.timeout = timeout;
  }

  // 设置默认请求头
  public setHeader(key: string, value: string): void {
    this.instance.defaults.headers.common[key] = value;
  }
}

// 导出HTTP客户端实例
export const httpClient = new HttpClient();
export default httpClient;
