"""
图床上传模块
支持Cloudinary、ImgBB和Steam云本地HTTP图床服务
"""

import os
import base64
import requests
import cloudinary
import cloudinary.uploader
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from urllib.parse import quote


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

    def _sanitize_name(self, value: str) -> str:
        """清理名称，保留 Cloudinary 可接受的稳定字符。"""
        if not isinstance(value, str):
            return ''
        cleaned = value.replace('\\', '_').replace('/', '_').replace(':', '_')
        cleaned = cleaned.replace('*', '_').replace('?', '_').replace('"', '_')
        cleaned = cleaned.replace('<', '_').replace('>', '_').replace('|', '_')
        cleaned = re.sub(r'_+', '_', cleaned).strip('._')
        return cleaned

    def _build_public_id(self, online_name: str, file_path: str) -> str:
        """根据导出文件路径生成稳定且尽量唯一的 public_id。"""
        clean_name = self._sanitize_name(online_name)
        normalized_path = os.path.normpath(file_path or '')
        path_parts = [part for part in normalized_path.split(os.sep) if part]

        if '.cards' in path_parts:
            cards_index = path_parts.index('.cards')
            relative_parts = path_parts[cards_index + 1:]
            if relative_parts:
                stem_parts = relative_parts[:-1]
                if stem_parts:
                    prefix = self._sanitize_name('_'.join(stem_parts))
                    if prefix:
                        return f"{prefix}_{clean_name}"

        return clean_name

    def check_file_exists(self, online_name: str) -> Optional[str]:
        """检查文件是否已上传到 Cloudinary"""
        try:
            # 清理文件名，确保与上传时使用的名称一致
            clean_name = self._sanitize_name(online_name)

            result = (
                cloudinary.Search()
                .expression(f"filename={clean_name}")
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

            clean_name = self._build_public_id(online_name, file_path)

            upload_options = {
                "public_id": clean_name,
                "folder": folder,
                "resource_type": "image",
                "use_filename": True,
                "unique_filename": False
            }

            print(f"清理后的public_id: {clean_name}")
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


class SteamCloudUploader(ImageUploader):
    """Steam 云上传器 - 不实际上传，只返回本地 HTTP URL。"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = str(config.get("steam_base_url") or "http://127.0.0.1:5000").rstrip("/")
        self.workspace_path = os.path.normpath(str(config.get("workspace_path") or ""))

    def _build_relative_path(self, file_path: str) -> str:
        """将工作区内绝对路径转换为稳定的相对路径。"""
        normalized_file_path = os.path.normpath(str(file_path or ""))

        if self.workspace_path and normalized_file_path.startswith(self.workspace_path):
            relative_path = os.path.relpath(normalized_file_path, self.workspace_path)
        else:
            relative_path = os.path.basename(normalized_file_path)

        return relative_path.replace(os.sep, "/")

    def _build_steam_url(self, file_path: str) -> str:
        """构造 Steam 云上传使用的本地 HTTP URL。"""
        relative_path = self._build_relative_path(file_path)
        encoded_relative_path = quote(relative_path, safe="/._-")
        return f"{self.base_url}/api/image-host/steam/{encoded_relative_path}"

    def check_file_exists(self, online_name: str) -> Optional[str]:
        """若本地文件存在则返回其 Steam 本地 HTTP URL。"""
        file_path = self.config.get("image_path_for_check")
        if isinstance(file_path, str) and file_path and os.path.exists(file_path):
            return self._build_steam_url(file_path)
        return None

    def upload_file(self, online_name: str, file_path: str) -> Optional[str]:
        """返回本地 HTTP URL，而不进行真实上传。"""
        if not isinstance(file_path, str) or not file_path:
            return None
        return self._build_steam_url(file_path)


def create_uploader(config: Dict[str, Any]) -> ImageUploader:
    """根据配置创建相应的图床上传器"""
    image_host = config.get("image_host", "cloudinary").lower()

    if image_host == "imgbb":
        return ImgBBUploader(config)
    elif image_host == "steam":
        return SteamCloudUploader(config)
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
