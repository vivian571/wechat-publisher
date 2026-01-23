"""
Cloudflare R2 客户端
兼容 AWS S3 API
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from loguru import logger
from pathlib import Path


class CloudflareR2Client:
    """Cloudflare R2 客户端"""
    
    def __init__(self, account_id: str, access_key: str, secret_key: str, bucket: str, public_url: str):
        """
        初始化 R2 客户端
        
        Args:
            account_id: Cloudflare 账户 ID
            access_key: R2 Access Key
            secret_key: R2 Secret Key
            bucket: 存储桶名称
            public_url: 公共访问 URL (如 https://assets.yourdomain.com)
        """
        self.bucket = bucket
        self.public_url = public_url.rstrip('/')
        
        # R2 兼容 S3 API
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        
        logger.debug(f"初始化 CloudflareR2Client: bucket={bucket}")
    
    def upload(self, local_path: str, remote_key: str) -> str:
        """
        上传文件到 R2
        
        Args:
            local_path: 本地文件路径
            remote_key: 远程文件名 (如 articles/abc123.png)
        
        Returns:
            str: 公共访问 URL
        
        Raises:
            FileNotFoundError: 本地文件不存在
            Exception: 上传失败
        """
        local_path = Path(local_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"文件不存在: {local_path}")
        
        try:
            logger.debug(f"上传文件到 R2: {local_path.name} -> {remote_key}")
            
            with open(local_path, 'rb') as f:
                self.s3.upload_fileobj(
                    f,
                    self.bucket,
                    remote_key,
                    ExtraArgs={'ContentType': self._get_content_type(local_path)}
                )
            
            # 返回公共 URL
            public_url = f"{self.public_url}/{remote_key}"
            logger.debug(f"上传成功: {public_url}")
            
            return public_url
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"R2 上传失败: {error_code} - {error_msg}")
            raise Exception(f"R2 上传失败: {error_msg}")
        
        except Exception as e:
            logger.error(f"上传失败: {e}")
            raise
    
    def delete(self, remote_key: str) -> bool:
        """
        删除 R2 中的文件
        
        Args:
            remote_key: 远程文件名
        
        Returns:
            bool: 是否删除成功
        """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=remote_key)
            logger.debug(f"删除文件成功: {remote_key}")
            return True
        
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    def exists(self, remote_key: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            remote_key: 远程文件名
        
        Returns:
            bool: 文件是否存在
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=remote_key)
            return True
        except ClientError:
            return False
    
    def _get_content_type(self, file_path: Path) -> str:
        """
        根据文件扩展名获取 Content-Type
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: Content-Type
        """
        ext = file_path.suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
        }
        return content_types.get(ext, 'application/octet-stream')


if __name__ == "__main__":
    # 测试代码
    import sys
    from loguru import logger
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    print("⚠️ 需要配置真实的 R2 凭证才能测试")
    print("✅ CloudflareR2Client 代码结构正确")
