"""
资源管理器模块
负责图片上传和链接替换
"""

import re
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from loguru import logger
from PIL import Image


class AssetManager:
    """资源管理器 - 处理图片上传"""
    
    def __init__(self, oss_client):
        """
        初始化资源管理器
        
        Args:
            oss_client: 图床客户端 (如 CloudflareR2Client)
        """
        self.oss_client = oss_client
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.uploaded_cache = {}  # 缓存已上传的图片
        logger.debug("初始化 AssetManager")
    
    def extract_images(self, markdown: str) -> List[str]:
        """
        提取 Markdown 中的所有图片路径
        
        Args:
            markdown: Markdown 内容
        
        Returns:
            List[str]: 图片路径列表
        """
        images = [match[1] for match in self.image_pattern.findall(markdown)]
        logger.debug(f"提取到 {len(images)} 张图片")
        return images
    
    def upload_image(self, local_path: str) -> str:
        """
        上传图片到图床
        
        Args:
            local_path: 本地图片路径
        
        Returns:
            str: 公共访问 URL
        
        Raises:
            FileNotFoundError: 图片文件不存在
            Exception: 上传失败
        """
        local_path = Path(local_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {local_path}")
        
        # 检查缓存
        file_hash = self._calculate_hash(str(local_path))
        if file_hash in self.uploaded_cache:
            logger.debug(f"使用缓存的图片 URL: {local_path.name}")
            return self.uploaded_cache[file_hash]
        
        logger.info(f"📸 上传图片: {local_path.name}")
        
        try:
            # 1. 图片优化 (压缩/格式转换)
            optimized_path = self._optimize_image(str(local_path))
            
            # 2. 生成唯一文件名 (基于内容哈希)
            ext = local_path.suffix
            remote_name = f"articles/{file_hash}{ext}"
            
            # 3. 上传到 OSS
            public_url = self.oss_client.upload(optimized_path, remote_name)
            
            # 4. 缓存结果
            self.uploaded_cache[file_hash] = public_url
            
            # 5. 清理临时文件
            if optimized_path != str(local_path):
                Path(optimized_path).unlink(missing_ok=True)
            
            logger.success(f"✅ 上传成功: {local_path.name} -> {public_url}")
            return public_url
        
        except Exception as e:
            logger.error(f"❌ 上传图片失败: {local_path.name}, 错误: {e}")
            raise
    
    def replace_images(self, markdown: str, base_dir: Path) -> str:
        """
        替换 Markdown 中的本地图片链接为公共 URL
        
        Args:
            markdown: Markdown 内容
            base_dir: Markdown 文件所在目录 (用于解析相对路径)
        
        Returns:
            str: 替换后的 Markdown 内容
        """
        logger.info("🔄 开始替换图片链接...")
        
        def replace_func(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
            # 跳过已经是 HTTP 链接的图片
            if img_path.startswith(('http://', 'https://')):
                logger.debug(f"跳过外链图片: {img_path}")
                return match.group(0)
            
            try:
                # 解析本地路径
                if img_path.startswith('./') or img_path.startswith('../'):
                    local_path = (base_dir / img_path).resolve()
                else:
                    local_path = Path(img_path).resolve()
                
                # 上传图片
                public_url = self.upload_image(str(local_path))
                
                return f'![{alt_text}]({public_url})'
            
            except Exception as e:
                logger.warning(f"⚠️ 无法处理图片 {img_path}: {e}")
                return match.group(0)  # 保持原样
        
        result = self.image_pattern.sub(replace_func, markdown)
        logger.success("✅ 图片链接替换完成")
        return result
    
    def _optimize_image(self, path: str, max_width: int = 1920, quality: int = 85) -> str:
        """
        图片优化: 压缩质量,限制尺寸
        
        Args:
            path: 图片路径
            max_width: 最大宽度 (默认 1920px)
            quality: 压缩质量 (默认 85)
        
        Returns:
            str: 优化后的图片路径
        """
        try:
            img = Image.open(path)
            
            # 检查是否需要调整尺寸
            if img.width <= max_width:
                logger.debug(f"图片尺寸合适,无需优化: {Path(path).name}")
                return path
            
            # 限制最大宽度
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 保存为优化后的文件
            optimized_path = f"{path}.optimized{Path(path).suffix}"
            img.save(optimized_path, quality=quality, optimize=True)
            
            logger.debug(f"图片已优化: {Path(path).name} ({img.width}x{img.height})")
            return optimized_path
        
        except Exception as e:
            logger.warning(f"图片优化失败,使用原图: {e}")
            return path
    
    def _calculate_hash(self, path: str) -> str:
        """
        计算文件 MD5 哈希
        
        Args:
            path: 文件路径
        
        Returns:
            str: MD5 哈希值
        """
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()


if __name__ == "__main__":
    # 测试代码
    import sys
    from loguru import logger
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    # 模拟图床客户端
    class MockOSSClient:
        def upload(self, local_path, remote_name):
            return f"https://example.com/{remote_name}"
    
    # 测试
    manager = AssetManager(MockOSSClient())
    
    test_markdown = """
# 测试文章

![本地图片](./images/test.png)
![外链图片](https://example.com/image.jpg)
"""
    
    images = manager.extract_images(test_markdown)
    print(f"提取到图片: {images}")
    
    print("✅ AssetManager 测试通过")
