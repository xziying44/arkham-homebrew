"""
图床上传模块
支持Cloudinary和ImgBB图床服务
"""

import os
import base64
import requests
import cloudinary
import cloudinary.uploader
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ImageUploader(ABC):
    """图床上传器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def check_file_exists(self, online_name: str) -> Optional[str]:
        """检查文件是否已在线上存在，返回URL或None"""
        pass

    @abstractmethod
    def upload_file(self, online_name: str, file_path: str) -> Optional[str]:
        """上传文件并返回URL或None"""
        pass


class CloudinaryUploader(ImageUploader):
    """Cloudinary 图床上传器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        cloudinary.config(
            cloud_name=config["cloud_name"],
            api_key=config["api_key"],
            api_secret=config["api_secret"],
        )

    def check_file_exists(self, online_name: str) -> Optional[str]:
        """检查文件是否已上传到 Cloudinary"""
        try:
            result = (
                cloudinary.Search()
                .expression(f"filename={online_name}")
                .max_results("1")
                .execute()
            )
            if result["total_count"] == 1:
                print(f"{online_name} - 已上传 (Cloudinary)")
                return result["resources"][0]["secure_url"]
        except Exception as e:
            print(f"检查 Cloudinary 文件是否存在时出错: {e}")
        return None

    def upload_file(self, online_name: str, file_path: str) -> Optional[str]:
        """上传文件到 Cloudinary"""
        print(f"{online_name} - 正在上传到 Cloudinary")
        try:
            # 获取自定义文件夹配置
            folder = self.config.get("folder", "AH_LCG")

            upload_options = {
                "public_id": online_name,
                "folder": folder,
                "resource_type": "image",
                "use_filename": True,
                "unique_filename": False
            }

            result = cloudinary.uploader.upload(file_path, **upload_options)
            return result["secure_url"]
        except Exception as e:
            print(f"上传到 Cloudinary 时出错: {e}")
            return None


class ImgBBUploader(ImageUploader):
    """ImgBB 图床上传器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("imgbb_api_key")
        self.api_url = "https://api.imgbb.com/1/upload"
        self.expiration = config.get("imgbb_expiration", 0)  # 0 表示永不过期

    def check_file_exists(self, online_name: str) -> Optional[str]:
        """ImgBB 不支持检查文件是否存在，直接返回 None"""
        # ImgBB API 没有提供直接检查文件是否存在的接口
        return None

    def upload_file(self, online_name: str, file_path: str) -> Optional[str]:
        """上传文件到 ImgBB"""
        print(f"{online_name} - 正在上传到 ImgBB")
        try:
            # 准备文件数据
            with open(file_path, "rb") as file:
                image_data = file.read()

            # 将图像文件转换为 base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 准备请求参数
            payload = {
                'key': self.api_key,
                'image': image_base64,
                'name': online_name,
            }

            # 如果设置了过期时间，添加到参数中
            if self.expiration > 0:
                payload['expiration'] = self.expiration

            # 发送请求
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                # 返回图像的显示 URL
                return result['data']['url']
            else:
                print(f"ImgBB 上传失败: {result}")
                return None

        except Exception as e:
            print(f"上传到 ImgBB 时出错: {e}")
            return None


def create_uploader(config: Dict[str, Any]) -> ImageUploader:
    """根据配置创建相应的图床上传器"""
    image_host = config.get("image_host", "cloudinary").lower()

    if image_host == "imgbb":
        return ImgBBUploader(config)
    elif image_host == "cloudinary":
        return CloudinaryUploader(config)
    else:
        raise ValueError(f"不支持的图床服务: {image_host}")


# 向后兼容的函数
def file_already_uploaded(online_name: str, uploader: ImageUploader) -> Optional[str]:
    """向后兼容的文件检查函数"""
    return uploader.check_file_exists(online_name)


def upload_file(online_name: str, file_path: str, uploader: ImageUploader) -> Optional[str]:
    """向后兼容的上传函数"""
    return uploader.upload_file(online_name, file_path)