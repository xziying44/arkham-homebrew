import requests
import base64
import uuid
import os
import json
from typing import List, Dict, Optional, Tuple


class GitHubImageHost:
    def __init__(self, token: Optional[str] = None):
        """
        初始化GitHub图床类

        Args:
            token (str, optional): GitHub Personal Access Token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = None
        self.username = None
        self.is_authenticated = False
        self.last_error = ""

        if token:
            self._set_token(token)

    def _set_token(self, token: str):
        """设置Token并初始化headers"""
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-GitHub-ImageHost"
        }

    def get_last_error(self) -> str:
        """获取最后一次错误信息"""
        return self.last_error

    def login(self, token: str) -> bool:
        """
        登录GitHub

        Args:
            token (str): GitHub Personal Access Token

        Returns:
            bool: 登录是否成功
        """
        try:
            self._set_token(token)
            return self._authenticate()
        except Exception as e:
            self.last_error = f"登录失败: {str(e)}"
            return False

    def silent_login(self, token: str) -> bool:
        """
        静默登录GitHub（不输出成功信息）

        Args:
            token (str): GitHub Personal Access Token

        Returns:
            bool: 登录是否成功
        """
        try:
            self._set_token(token)
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                self.username = user_info.get("login")
                self.is_authenticated = True
                self.last_error = ""
                return True
            else:
                self.is_authenticated = False
                self.last_error = f"认证失败: HTTP {response.status_code}"
                return False
        except Exception as e:
            self.is_authenticated = False
            self.last_error = f"认证错误: {str(e)}"
            return False

    def _authenticate(self) -> bool:
        """
        验证GitHub Token并获取用户信息

        Returns:
            bool: 认证是否成功
        """
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                self.username = user_info.get("login")
                self.is_authenticated = True
                self.last_error = ""
                return True
            else:
                self.last_error = f"认证失败: HTTP {response.status_code} - {response.text}"
                self.is_authenticated = False
                return False
        except Exception as e:
            self.last_error = f"认证错误: {str(e)}"
            self.is_authenticated = False
            return False

    def _check_authentication(self) -> bool:
        """检查是否已认证"""
        if not self.is_authenticated or not self.token:
            self.last_error = "请先登录GitHub"
            return False
        return True

    def list_repositories(self) -> Tuple[List[Dict], Optional[str]]:
        """
        获取用户的仓库列表

        Returns:
            Tuple[List[Dict], Optional[str]]: (仓库信息列表, 错误信息)
        """
        if not self._check_authentication():
            return [], self.last_error

        try:
            repos = []
            page = 1
            per_page = 100

            while True:
                response = requests.get(
                    f"{self.base_url}/user/repos",
                    headers=self.headers,
                    params={"page": page, "per_page": per_page, "sort": "updated"}
                )

                if response.status_code != 200:
                    self.last_error = f"获取仓库列表失败: HTTP {response.status_code}"
                    return [], self.last_error

                page_repos = response.json()
                if not page_repos:
                    break

                for repo in page_repos:
                    repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "private": repo["private"],
                        "description": repo.get("description", ""),
                        "updated_at": repo["updated_at"]
                    })

                page += 1
                if len(page_repos) < per_page:
                    break

            self.last_error = ""
            return repos, None

        except Exception as e:
            self.last_error = f"获取仓库列表错误: {str(e)}"
            return [], self.last_error

    def upload_image(self, image_path: str, repo_name: Optional[str] = None,
                     branch: str = "main", folder: str = "images") -> Tuple[Optional[str], Optional[str]]:
        """
        上传图片到GitHub仓库

        Args:
            image_path (str): 本地图片路径
            repo_name (str, optional): 仓库名称，如果为None则从配置获取
            branch (str): 分支名称，默认为main
            folder (str): 存储文件夹，默认为images

        Returns:
            Tuple[Optional[str], Optional[str]]: (图片的直链URL, 错误信息)
        """
        if not self._check_authentication():
            return None, self.last_error

        try:
            if not os.path.exists(image_path):
                self.last_error = f"图片文件不存在: {image_path}"
                return None, self.last_error

            # 检查文件是否为图片
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            if not image_path.lower().endswith(valid_extensions):
                self.last_error = f"不支持的文件格式，支持的格式: {', '.join(valid_extensions)}"
                return None, self.last_error

            if not repo_name:
                self.last_error = "请提供仓库名称"
                return None, self.last_error

            if "/" not in repo_name:
                repo_name = f"{self.username}/{repo_name}"

            # 读取并编码图片
            with open(image_path, 'rb') as f:
                image_data = f.read()

            encoded_content = base64.b64encode(image_data).decode('utf-8')

            # 生成唯一文件名
            file_extension = os.path.splitext(image_path)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"{folder}/{unique_filename}" if folder else unique_filename

            # 检查文件是否已存在（虽然UUID重复几率很小）
            check_response = requests.get(
                f"{self.base_url}/repos/{repo_name}/contents/{file_path}",
                headers=self.headers,
                params={"ref": branch}
            )

            if check_response.status_code == 200:
                # 文件名冲突，重新生成
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = f"{folder}/{unique_filename}" if folder else unique_filename

            # 上传文件
            upload_data = {
                "message": f"Upload image: {unique_filename}",
                "content": encoded_content,
                "branch": branch
            }

            response = requests.put(
                f"{self.base_url}/repos/{repo_name}/contents/{file_path}",
                headers=self.headers,
                json=upload_data
            )

            if response.status_code == 201:
                result = response.json()
                download_url = result["content"]["download_url"]
                self.last_error = ""
                return download_url, None
            else:
                self.last_error = f"上传失败: HTTP {response.status_code} - {response.text}"
                return None, self.last_error

        except Exception as e:
            self.last_error = f"上传图片错误: {str(e)}"
            return None, self.last_error

    def get_status(self) -> Dict:
        """获取当前状态信息"""
        return {
            "is_authenticated": self.is_authenticated,
            "username": self.username,
            "has_token": bool(self.token),
            "last_error": self.last_error
        }
